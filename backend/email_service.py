import requests
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode
from typing import List, Dict, Optional
import secrets
import hashlib
import base64

class OutlookEmailService:
    """Service for interacting with Microsoft Outlook/Graph API"""
    
    def __init__(self):
        self.client_id = os.getenv('OUTLOOK_CLIENT_ID')
        self.client_secret = os.getenv('OUTLOOK_CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.scope = 'https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Mail.ReadWrite'
        self.auth_base_url = 'https://login.microsoftonline.com/common/oauth2/v2.0'
        self.graph_base_url = 'https://graph.microsoft.com/v1.0'
        self.code_verifier = None
        self.code_challenge = None

    def _generate_pkce(self):
        """Generate PKCE code verifier and challenge"""
        self.code_verifier = secrets.token_urlsafe(32)
        m = hashlib.sha256()
        m.update(self.code_verifier.encode('ascii'))
        self.code_challenge = base64.urlsafe_b64encode(m.digest()).decode('ascii').replace('=', '')

    def get_auth_url(self) -> str:
        """Generate OAuth2 authorization URL with PKCE"""
        self._generate_pkce()
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_mode': 'query',
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'S256'
        }
        return f"{self.auth_base_url}/authorize?{urlencode(params)}"

    def get_access_token(self, auth_code: str) -> Optional[Dict]:
        """Exchange authorization code for access token with PKCE"""
        token_url = f"{self.auth_base_url}/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'code_verifier': self.code_verifier
        }
        
        try:
            response = requests.post(token_url, data=data)
            print(f"[DEBUG] Token response status: {response.status_code}")
            if response.status_code == 200:
                token_data = response.json()
                print(f"[DEBUG] Token data keys: {list(token_data.keys())}")
                return token_data
            else:
                print(f"[ERROR] Token request failed: {response.text}")
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
        
        return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh an expired access token"""
        token_url = f"{self.auth_base_url}/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'scope': self.scope
        }
        
        try:
            response = requests.post(token_url, data=data)
            print(f"[DEBUG] Refresh token response status: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[ERROR] Token refresh failed: {response.text}")
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
        
        return None

    def send_reply(self, access_token: str, original_email_id: str, reply_content: str) -> bool:
        """Send reply to an email"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"[DEBUG] Preparing to send reply to email {original_email_id}")
            
            # Make sure reply_content is a string
            if isinstance(reply_content, dict):
                content_text = reply_content.get('content', str(reply_content))
            else:
                content_text = str(reply_content)
            
            print(f"[DEBUG] Processed reply content: {content_text[:100]}...")
            
            # First, get the original email to extract sender information
            original_email = self.get_email_by_id(access_token, original_email_id)
            if not original_email:
                print(f"[ERROR] Could not fetch original email {original_email_id}")
                return False
            
            sender_email = original_email['sender']
            sender_name = original_email.get('sender_name', '')
            subject = original_email['subject']
            
            print(f"[DEBUG] Replying to: {sender_email} with subject: {subject}")
            
            # Try method 1: Use createReply endpoint
            reply_url = f"{self.graph_base_url}/me/messages/{original_email_id}/createReply"
            
            response = requests.post(reply_url, headers=headers)
            
            if response.status_code == 201:
                # Method 1 worked - proceed with draft update
                reply_draft = response.json()
                draft_id = reply_draft['id']
                
                print(f"[DEBUG] Reply draft created with ID: {draft_id}")
                
                # Update the reply with our content
                update_url = f"{self.graph_base_url}/me/messages/{draft_id}"
                
                update_payload = {
                    "body": {
                        "contentType": "Text",
                        "content": content_text
                    }
                }
                
                print(f"[DEBUG] Updating reply with content...")
                update_response = requests.patch(update_url, headers=headers, json=update_payload)
                
                if update_response.status_code != 200:
                    print(f"[ERROR] Failed to update reply content: {update_response.status_code} - {update_response.text}")
                    return False
                
                print(f"[DEBUG] Reply content updated successfully")
                
                # Send the reply
                send_url = f"{self.graph_base_url}/me/messages/{draft_id}/send"
                send_response = requests.post(send_url, headers=headers)
                
                if send_response.status_code == 202:
                    print(f"[DEBUG] Reply sent successfully using createReply method")
                    return True
                else:
                    print(f"[ERROR] Failed to send reply: {send_response.status_code} - {send_response.text}")
                    return False
            
            else:
                # Method 1 failed, try method 2: Direct send
                print(f"[DEBUG] createReply failed ({response.status_code}), trying direct send method")
                print(f"[DEBUG] createReply error: {response.text}")
                
                # Method 2: Send reply directly
                send_url = f"{self.graph_base_url}/me/sendMail"
                
                # Build reply subject
                reply_subject = subject if subject.startswith('RE:') else f"RE: {subject}"
                
                email_payload = {
                    "message": {
                        "subject": reply_subject,
                        "body": {
                            "contentType": "Text",
                            "content": content_text
                        },
                        "toRecipients": [
                            {
                                "emailAddress": {
                                    "address": sender_email,
                                    "name": sender_name
                                }
                            }
                        ],
                        "internetMessageHeaders": [
                            {
                                "name": "In-Reply-To",
                                "value": f"<{original_email_id}>"
                            }
                        ]
                    }
                }
                
                print(f"[DEBUG] Sending reply directly to {sender_email}")
                direct_response = requests.post(send_url, headers=headers, json=email_payload)
                
                if direct_response.status_code == 202:
                    print(f"[DEBUG] Reply sent successfully using direct send method")
                    return True
                else:
                    print(f"[ERROR] Direct send also failed: {direct_response.status_code} - {direct_response.text}")
                    return False
            
        except Exception as e:
            print(f"[ERROR] Exception in send_reply: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _get_sender_email(self, access_token: str, email_id: str) -> str:
        """Get sender email address for a message"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            url = f"{self.graph_base_url}/me/messages/{email_id}"
            params = {'$select': 'from'}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()['from']['emailAddress']['address']
        except Exception as e:
            print(f"[ERROR] Failed to get sender email: {str(e)}")
        
        return ""

    def get_conversation_context(self, access_token: str, email_id: str) -> List[Dict]:
        """Get conversation context for better reply generation"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Get the original email to find conversation ID
            email = self.get_email_by_id(access_token, email_id)
            if not email:
                return []
            
            conversation_id = email['conversation_id']
            
            # Get all messages in conversation
            params = {
                '$filter': f"conversationId eq '{conversation_id}'",
                '$orderby': 'receivedDateTime desc',
                '$select': 'sender,subject,body,receivedDateTime',
                '$top': 5
            }
            
            url = f"{self.graph_base_url}/me/messages"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                messages = response.json().get('value', [])
                context = []
                
                for message in messages:
                    context.append({
                        'sender': message['sender']['emailAddress']['address'],
                        'subject': message['subject'],
                        'body': self._extract_text_from_body(message['body'])[:500],
                        'timestamp': message['receivedDateTime']
                    })
                
                return context
        except Exception as e:
            print(f"Error getting conversation context: {str(e)}")
        
        return []
    
    def get_email_by_id(self, access_token: str, email_id: str) -> Optional[Dict]:
        """Get full email details by ID"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            url = f"{self.graph_base_url}/me/messages/{email_id}"
            params = {
                '$select': 'id,sender,subject,body,receivedDateTime,conversationId'
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                email = response.json()
                return {
                    'id': email['id'],
                    'sender': email['sender']['emailAddress']['address'],
                    'sender_name': email['sender']['emailAddress']['name'],
                    'subject': email['subject'],
                    'body': self._extract_text_from_body(email['body']),
                    'timestamp': email['receivedDateTime'],
                    'conversation_id': email['conversationId']
                }
            else:
                print(f"[ERROR] Failed to get email by ID: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error getting email by ID: {str(e)}")
        
        return None

    def get_recent_emails(self, access_token: str, limit: int = 20) -> List[Dict]:
        """Fetch recent emails from inbox"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        params = {
            '$top': limit,
            '$orderby': 'receivedDateTime desc',
            '$filter': f"receivedDateTime ge {since_date}",
            '$select': 'id,sender,subject,body,receivedDateTime,isRead,hasAttachments,conversationId'
        }
        
        try:
            url = f"{self.graph_base_url}/me/messages"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                emails = []
                
                for email in data.get('value', []):
                    processed_email = {
                        'id': email['id'],
                        'sender': email['sender']['emailAddress']['address'],
                        'sender_name': email['sender']['emailAddress']['name'],
                        'subject': email['subject'],
                        'body': self._extract_text_from_body(email['body']),
                        'timestamp': email['receivedDateTime'],
                        'is_read': email['isRead'],
                        'has_attachments': email['hasAttachments'],
                        'conversation_id': email['conversationId'],
                        'priority': 'high' if 'urgent' in email['subject'].lower() else 'medium'
                    }
                    emails.append(processed_email)
                
                print(f"[DEBUG] Successfully fetched {len(emails)} emails")
                return emails
            else:
                print(f"[ERROR] Failed to fetch emails: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
        
        return []
    
    def get_new_emails_since_last_sync(self, access_token: str) -> List[Dict]:
        """Get new emails since last sync (for live monitoring)"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        since_date = (datetime.now() - timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        params = {
            '$top': 5,
            '$orderby': 'receivedDateTime desc',
            '$filter': f"receivedDateTime ge {since_date}",
            '$select': 'id,sender,subject,body,receivedDateTime,conversationId'
        }
        
        try:
            url = f"{self.graph_base_url}/me/messages"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                emails = []
                
                for email in data.get('value', []):
                    processed_email = {
                        'id': email['id'],
                        'sender': email['sender']['emailAddress']['address'],
                        'sender_name': email['sender']['emailAddress']['name'],
                        'subject': email['subject'],
                        'body': self._extract_text_from_body(email['body']),
                        'timestamp': email['receivedDateTime'],
                        'conversation_id': email['conversationId'],
                        'priority': 'high' if 'urgent' in email['subject'].lower() else 'medium'
                    }
                    emails.append(processed_email)
                
                return emails
        except Exception as e:
            print(f"Error fetching new emails: {str(e)}")
        
        return []

    def check_if_replied(self, access_token: str, email_id: str) -> bool:
        """Check if a reply has been sent to this email"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Get the conversation ID first
            email = self.get_email_by_id(access_token, email_id)
            if not email:
                return False
                
            conversation_id = email['conversation_id']
            
            # Check for replies in the conversation
            params = {
                '$filter': f"conversationId eq '{conversation_id}'",
                '$select': 'id,subject,internetMessageHeaders,sender',
                '$orderby': 'receivedDateTime desc'
            }
            
            url = f"{self.graph_base_url}/me/messages"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                messages = response.json().get('value', [])
                
                # Get current user's email to identify sent messages
                me_response = requests.get(f"{self.graph_base_url}/me", headers=headers)
                if me_response.status_code == 200:
                    my_email = me_response.json().get('mail', '').lower()
                    
                    for message in messages:
                        sender_email = message.get('sender', {}).get('emailAddress', {}).get('address', '').lower()
                        if sender_email == my_email and message['id'] != email_id:
                            return True
            
        except Exception as e:
            print(f"Error checking reply status: {str(e)}")
        
        return False

    def _extract_text_from_body(self, body: Dict) -> str:
        """Extract plain text from email body"""
        if not body or not isinstance(body, dict):
            return ""
            
        content = body.get('content', '')
        content_type = body.get('contentType', 'Text')
        
        if content_type == 'Text':
            return content
        elif content_type == 'HTML':
            # Simple HTML tag removal
            import re
            text = re.sub('<[^<]+?>', '', content)
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
            text = text.replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&quot;', '"').replace('&#39;', "'")
            return text.strip()
        
        return content