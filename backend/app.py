from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import requests
from email_service import OutlookEmailService
from ai_service import OllamaService
from models import EmailDatabase
from utils import validate_email_relevance
from flask import Blueprint, jsonify, session
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
CORS(app, supports_credentials=True, origins=[os.getenv('FRONTEND_URL')])

# Initialize services
email_service = OutlookEmailService()
ai_service = OllamaService()
db = EmailDatabase()
executor = ThreadPoolExecutor(max_workers=5)

# Global variable to store active access tokens
active_tokens = {}

def background_email_check():
    """Background thread to check for new emails periodically"""
    while True:
        try:
            current_token = active_tokens.get('current')
            if current_token:
                print("[BACKGROUND] Checking for new emails...")
                new_emails = email_service.get_new_emails_since_last_sync(current_token)
                if new_emails:
                    print(f"[BACKGROUND] Found {len(new_emails)} new emails")
                    for email in new_emails:
                        process_email(email, current_token)
                    db.update_last_sync()
        except Exception as e:
            print(f"[BACKGROUND ERROR] Email check failed: {str(e)}")
        time.sleep(300)

@app.route('/auth/login')
def login():
    """Initiate OAuth flow with Microsoft"""
    try:
        auth_url = email_service.get_auth_url()
        print(f"[DEBUG] Generated auth URL: {auth_url}")
        return jsonify({'auth_url': auth_url})
    except Exception as e:
        print(f"[ERROR] Failed to generate auth URL: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback from Microsoft"""
    print(f"[DEBUG] Auth callback received")
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        error_desc = request.args.get('error_description', '')
        print(f"[ERROR] OAuth error: {error} - {error_desc}")
        return redirect(f"{os.getenv('FRONTEND_URL')}?auth=error&reason={error_desc}")

    if code:
        print(f"[DEBUG] Received auth code: {code[:10]}...")
        try:
            token_data = email_service.get_access_token(code)
            if token_data:
                print(f"[DEBUG] Successfully obtained tokens")
                # Store both ways for compatibility
                session['token_data'] = token_data
                session['access_token'] = token_data['access_token']  # Add this line
                session['refresh_token'] = token_data.get('refresh_token', '')
                session['token_issued_at'] = time.time()
                session['expires_in'] = token_data.get('expires_in', 3600)
                active_tokens['current'] = token_data['access_token']
                
                print(f"[DEBUG] Session data stored: {list(session.keys())}")
                return redirect(f"{os.getenv('FRONTEND_URL')}?auth=success")
            else:
                print(f"[ERROR] Failed to obtain tokens")
                return redirect(f"{os.getenv('FRONTEND_URL')}?auth=error&reason=token_exchange_failed")
        except Exception as e:
            print(f"[ERROR] Exception during token exchange: {str(e)}")
            return redirect(f"{os.getenv('FRONTEND_URL')}?auth=error&reason=exception")

    return redirect(f"{os.getenv('FRONTEND_URL')}?auth=error&reason=no_code")

def get_valid_token():
    """Get a valid access token, refreshing if needed"""
    if 'token_data' not in session:
        print("[DEBUG] No token_data in session")
        return None
    
    # Check if token is expired (with 5 minute buffer)
    issued_at = session.get('token_issued_at', 0)
    expires_in = session.get('expires_in', 3600)
    current_time = time.time()
    
    print(f"[DEBUG] Token check - Issued: {issued_at}, Expires in: {expires_in}, Current: {current_time}")
    
    if current_time - issued_at > (expires_in - 300):  # 5 minute buffer
        print("[DEBUG] Token expired, attempting refresh")
        refresh_token = session.get('refresh_token')
        if refresh_token:
            new_token = email_service.refresh_access_token(refresh_token)
            if new_token:
                print("[DEBUG] Token refreshed successfully")
                session['token_data'] = new_token
                session['access_token'] = new_token['access_token']
                session['refresh_token'] = new_token.get('refresh_token', refresh_token)
                session['token_issued_at'] = time.time()
                session['expires_in'] = new_token.get('expires_in', 3600)
                active_tokens['current'] = new_token['access_token']
                return new_token['access_token']
            else:
                print("[DEBUG] Token refresh failed")
                return None
        else:
            print("[DEBUG] No refresh token available")
            return None
    
    access_token = session['token_data']['access_token']
    print(f"[DEBUG] Using existing token: {access_token[:20]}...")
    return access_token

@app.route('/api/status')
def get_status():
    """Get authentication and service status"""
    # Check if we have valid token data
    has_token_data = 'token_data' in session and 'access_token' in session
    authenticated = False
    
    if has_token_data:
        # Verify token is still valid
        token = get_valid_token()
        authenticated = token is not None
    
    ollama_status = ai_service.check_health()
    last_sync = db.get_last_sync_time()

    print(f"[DEBUG] Status check - Auth: {authenticated}, Has session: {has_token_data}, Ollama: {ollama_status}")
    print(f"[DEBUG] Session keys: {list(session.keys())}")

    return jsonify({
        'authenticated': authenticated,
        'ollama_status': ollama_status,
        'last_sync': last_sync
    })

def process_email(email, access_token=None):
    """Process and save a single email"""
    try:
        print(f"[DEBUG] Processing email: {email.get('subject', 'No subject')[:30]}...")

        # Check if email already exists
        existing = db.get_email_by_id(email['id'])
        if existing:
            print(f"[DEBUG] Email already exists in database")
            return existing

        # Skip emails sent by the current user (replies we sent)
        try:
            token_to_use = access_token or get_valid_token()
            if token_to_use:
                # Get current user's email
                headers = {'Authorization': f'Bearer {token_to_use}'}
                me_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
                if me_response.status_code == 200:
                    my_email = me_response.json().get('mail', '').lower()
                    sender_email = email.get('sender', '').lower()
                    
                    if sender_email == my_email:
                        print(f"[DEBUG] Skipping email sent by current user: {sender_email}")
                        return None
        except Exception as e:
            print(f"[ERROR] Failed to check sender: {str(e)}")

        # Check relevance
        try:
            is_relevant = ai_service.check_email_relevance(email['body'], email['subject'])
            print(f"[DEBUG] AI relevance result for '{email['subject'][:30]}...': {is_relevant}")
        except Exception as e:
            print(f"[ERROR] AI relevance check failed, using fallback: {str(e)}")
            is_relevant = validate_email_relevance(email['body'], email['subject'])
            print(f"[DEBUG] Fallback relevance result for '{email['subject'][:30]}...': {is_relevant}")

        if not is_relevant:
            print(f"[DEBUG] Email '{email['subject'][:30]}...' marked as NOT RELEVANT - skipping")
            return None
        
        print(f"[DEBUG] Email '{email['subject'][:30]}...' marked as RELEVANT - processing")

        # Generate summary
        print(f"[DEBUG] Generating summary...")
        try:
            summary = ai_service.summarize_email(email['body'], email['subject'])
        except Exception as e:
            print(f"[ERROR] Summary generation failed: {str(e)}")
            summary = f"• Email from {email.get('sender', 'Unknown sender')}\n• Subject: {email.get('subject', 'No subject')}"

        # Check reply status
        print(f"[DEBUG] Checking reply status...")
        has_reply = False
        try:
            # Use the passed token or get from session
            token_to_use = access_token or get_valid_token()
            if token_to_use:
                has_reply = email_service.check_if_replied(token_to_use, email['id'])
        except Exception as e:
            print(f"[ERROR] Reply check failed: {str(e)}")

        # Generate draft reply if needed
        draft_reply = None
        if not has_reply:
            print(f"[DEBUG] Generating draft reply...")
            try:
                token_to_use = access_token or get_valid_token()
                context = []
                if token_to_use:
                    context = email_service.get_conversation_context(token_to_use, email['id'])
                draft_reply = ai_service.generate_reply(email['body'], email['subject'], context)
            except Exception as e:
                print(f"[ERROR] Reply generation failed: {str(e)}")
                draft_reply = "Thank you for your email. I'll review this and get back to you soon.\n\nBest regards"

        # Save to database
        processed_email = {
            'id': email['id'],
            'sender': email['sender'],
            'sender_name': email.get('sender_name', ''),
            'subject': email['subject'],
            'body': email['body'][:500] + '...' if len(email['body']) > 500 else email['body'],
            'timestamp': email['timestamp'],
            'summary': summary,
            'has_reply': has_reply,
            'draft_reply': draft_reply,
            'is_relevant': is_relevant,
            'conversation_id': email.get('conversation_id', ''),
            'priority': email.get('priority', 'medium')
        }

        print(f"[DEBUG] Saving email to database...")
        db.save_email(processed_email)
        return processed_email

    except Exception as e:
        print(f"[ERROR] Error processing email {email.get('id', 'unknown')}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/api/emails/sync', methods=['POST'])
def sync_emails():
    """Sync recent emails and process them with AI"""
    access_token = get_valid_token()
    if not access_token:
        print("[ERROR] Sync attempted without valid authentication")
        return jsonify({'error': 'Not authenticated'}), 401

    print("[DEBUG] Starting email sync...")
    try:
        emails = email_service.get_recent_emails(access_token, limit=20)
        print(f"[DEBUG] Retrieved {len(emails) if emails else 0} emails from API")

        if not emails:
            return jsonify({'message': 'No emails found', 'emails': []})

        processed_emails = []
        for email in emails:
            result = process_email(email, access_token)
            if result:
                processed_emails.append(result)

        db.update_last_sync()
        print(f"[DEBUG] Sync completed. Processed {len(processed_emails)} emails")

        return jsonify({
            'message': f'Processed {len(processed_emails)} relevant emails',
            'emails': processed_emails,
            'total_fetched': len(emails)
        })

    except Exception as e:
        print(f"[ERROR] Sync failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails')
def get_emails():
    """Get all processed relevant emails"""
    try:
        emails = db.get_all_emails()
        print(f"[DEBUG] Retrieved {len(emails)} relevant emails from database")
        return jsonify({'emails': emails})
    except Exception as e:
        print(f"[ERROR] Failed to get emails: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails/<email_id>')
def get_email_details(email_id):
    """Get detailed email information"""
    try:
        email = db.get_email_by_id(email_id)
        if not email or not email.get('is_relevant', True):
            return jsonify({'error': 'Email not found'}), 404

        # Try to get full email content if we have a valid token
        access_token = get_valid_token()
        if access_token:
            try:
                full_email = email_service.get_email_by_id(access_token, email_id)
                if full_email:
                    email['full_body'] = full_email['body']
            except Exception as e:
                print(f"[ERROR] Failed to get full email content: {str(e)}")

        return jsonify({'email': email})
    except Exception as e:
        print(f"[ERROR] Failed to get email details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails/<email_id>/reply', methods=['POST'])
def send_reply(email_id):
    """Send reply to an email"""
    access_token = get_valid_token()
    if not access_token:
        print("[ERROR] Reply attempted without valid authentication")
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        data = request.get_json()
        print(f"[DEBUG] Raw request data: {data}")
        print(f"[DEBUG] Data type: {type(data)}")
        
        # Extract reply content properly
        reply_content = None
        if isinstance(data, dict):
            if 'content' in data:
                content_value = data['content']
                # Handle nested content structure
                if isinstance(content_value, dict) and 'content' in content_value:
                    reply_content = content_value['content']
                    print(f"[DEBUG] Extracted content from nested 'content' key")
                else:
                    reply_content = content_value
                    print(f"[DEBUG] Extracted content from 'content' key")
            elif 'reply_content' in data:
                reply_content = data['reply_content']
                print(f"[DEBUG] Extracted content from 'reply_content' key")
            else:
                # If data itself contains the message
                print(f"[DEBUG] Data keys: {list(data.keys())}")
                reply_content = str(data)
        else:
            reply_content = str(data)
        
        # Ensure reply_content is a string
        if isinstance(reply_content, dict):
            # If it's still a dict, try to extract content or convert to string
            if 'content' in reply_content:
                reply_content = reply_content['content']
            else:
                reply_content = str(reply_content)
        
        # Convert to string if it's not already
        reply_content = str(reply_content) if reply_content is not None else ""
        
        print(f"[DEBUG] Final reply_content type: {type(reply_content)}")
        print(f"[DEBUG] Final reply_content: {reply_content[:200]}...")
        
        if not reply_content or reply_content.strip() == '':
            return jsonify({'error': 'Reply content is required'}), 400

        print(f"[DEBUG] Sending reply to email {email_id}")
        
        # Check if this email exists in our database and get the original ID
        email_record = db.get_email_by_id(email_id)
        if email_record:
            # Use the ID from our database (which should be the original email ID)
            original_email_id = email_record['id']
            print(f"[DEBUG] Using original email ID from database: {original_email_id}")
        else:
            # Use the provided ID
            original_email_id = email_id
            print(f"[DEBUG] Using provided email ID: {original_email_id}")

        # Send reply
        success = email_service.send_reply(
            access_token,
            original_email_id,
            reply_content
        )

        if success:
            print(f"[DEBUG] Reply sent successfully")
            # Mark the original email as replied in the database
            if email_record:
                db.mark_as_replied(email_record['id'])
            else:
                db.mark_as_replied(email_id)
            return jsonify({'message': 'Reply sent successfully'})
        else:
            print(f"[ERROR] Failed to send reply")
            return jsonify({'error': 'Failed to send reply. Please try again.'}), 500

    except Exception as e:
        print(f"[ERROR] Reply failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails/<email_id>/regenerate-reply', methods=['POST'])
def regenerate_reply(email_id):
    """Regenerate draft reply for an email"""
    try:
        email = db.get_email_by_id(email_id)
        if not email or not email.get('is_relevant', True):
            return jsonify({'error': 'Email not found'}), 404

        context = []
        access_token = get_valid_token()
        if access_token:
            try:
                context = email_service.get_conversation_context(access_token, email_id)
            except Exception as e:
                print(f"[ERROR] Failed to get conversation context: {str(e)}")

        # Generate new reply
        try:
            new_reply = ai_service.generate_reply(
                email['body'], 
                email['subject'], 
                context
            )
        except Exception as e:
            print(f"[ERROR] AI reply generation failed: {str(e)}")
            new_reply = "Thank you for your email. I'll review this and get back to you soon.\n\nBest regards"

        # Update database
        db.update_draft_reply(email_id, new_reply)

        return jsonify({'draft_reply': new_reply})

    except Exception as e:
        print(f"[ERROR] Failed to regenerate reply: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get email statistics"""
    try:
        stats = db.get_email_stats()
        print(f"[DEBUG] Email stats: {stats}")
        return jsonify({'stats': stats})
    except Exception as e:
        print(f"[ERROR] Failed to get stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/session')
def debug_session():
    """Debug session information"""
    return jsonify({
        'session_keys': list(session.keys()),
        'has_token_data': 'token_data' in session,
        'has_access_token': 'access_token' in session,
        'token_issued_at': session.get('token_issued_at'),
        'expires_in': session.get('expires_in'),
        'current_time': time.time()
    })

@app.route('/api/debug/db-test')
def debug_db_test():
    """Test database functionality"""
    try:
        emails = db.get_all_emails()
        stats = db.get_email_stats()

        return jsonify({
            'database_working': True,
            'email_count': len(emails),
            'stats': stats,
            'sample_emails': emails[:2] if emails else []
        })
    except Exception as e:
        return jsonify({
            'database_working': False,
            'error': str(e)
        })

@app.route('/api/debug/ollama-test')
def debug_ollama_test():
    """Test Ollama functionality"""
    try:
        health = ai_service.check_health()
        if health:
            test_summary = ai_service.summarize_email("This is a test email body", "Test Subject")
            test_reply = ai_service.generate_reply("This is a test email body", "Test Subject")

            return jsonify({
                'ollama_working': True,
                'health': health,
                'test_summary': test_summary,
                'test_reply': test_reply
            })
        else:
            return jsonify({
                'ollama_working': False,
                'health': health,
                'message': 'Ollama not running or phi3 model not available'
            })
    except Exception as e:
        return jsonify({
            'ollama_working': False,
            'error': str(e)
        })

@app.route('/api/logout', methods=['POST'])
def logout():
    """Clear session and logout"""
    session.clear()
    active_tokens.clear()
    print("[DEBUG] User logged out, session cleared")
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    print("[DEBUG] Starting Flask application...")
    print(f"[DEBUG] Frontend URL: {os.getenv('FRONTEND_URL')}")
    print(f"[DEBUG] Ollama health: {ai_service.check_health()}")
    
    # Start background email checker
    threading.Thread(target=background_email_check, daemon=True).start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)