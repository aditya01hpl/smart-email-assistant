import re
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import html

def validate_email_relevance(email_body: str, subject: str) -> bool:
    """Conservative rule-based email relevance validation (fallback for AI)"""
    
    # Convert to lowercase for analysis
    subject_lower = subject.lower()
    body_lower = email_body.lower()
    
    # STRICT spam/marketing indicators - only mark as irrelevant if clearly spam
    strict_spam_indicators = [
        'click here to unsubscribe',
        'you have won',
        'congratulations you have been selected',
        'limited time offer expires',
        'act now or lose out',
        'make money fast',
        'work from home opportunity',
        'get rich quick',
        'no obligation',
        'call now',
        'order now',
        'buy now',
        'subscribe now',
        'click to claim',
        'final notice',
        'this is not spam'
    ]
    
    # Important indicators that should ALWAYS be relevant
    always_relevant_keywords = [
        'meeting', 'schedule', 'appointment', 'deadline', 'urgent', 'important',
        'project', 'task', 'deliverable', 'client', 'customer', 'interview',
        'conference', 'proposal', 'contract', 'invoice', 'payment', 'account',
        'password', 'security', 'verification', 'confirm', 'approval',
        'leave', 'vacation', 'sick', 'request', 'application', 'feedback',
        'review', 'update', 'notification', 'alert', 'reminder', 'follow up',
        'discussion', 'question', 'inquiry', 'support', 'help', 'issue',
        'problem', 'solution', 'opportunity', 'collaboration', 'partnership'
    ]
    
    # Check for always relevant keywords first
    for keyword in always_relevant_keywords:
        if keyword in subject_lower or keyword in body_lower:
            print(f"[DEBUG] Email marked RELEVANT due to keyword: {keyword}")
            return True
    
    # Check for strict spam indicators
    spam_count = 0
    for indicator in strict_spam_indicators:
        if indicator in subject_lower or indicator in body_lower:
            spam_count += 1
    
    # Only mark as irrelevant if multiple spam indicators are present
    if spam_count >= 2:
        print(f"[DEBUG] Email marked IRRELEVANT due to {spam_count} spam indicators")
        return False
    
    # Check for obvious promotional patterns
    promotional_patterns = [
        r'unsubscribe.*here',
        r'click.*to.*stop.*receiving',
        r'you.*received.*this.*email.*because',
        r'promotional.*email',
        r'marketing.*email'
    ]
    
    promotional_matches = 0
    for pattern in promotional_patterns:
        if re.search(pattern, body_lower):
            promotional_matches += 1
    
    # Only mark as irrelevant if clearly promotional AND no personal elements
    if promotional_matches >= 2:
        # Check if it has personal elements
        personal_indicators = ['dear', 'hi', 'hello', 'thank you', 'regards', 'sincerely']
        has_personal = any(indicator in body_lower for indicator in personal_indicators)
        
        if not has_personal:
            print(f"[DEBUG] Email marked IRRELEVANT due to promotional patterns without personal touch")
            return False
    
    # Check sender domain - be more lenient
    if '@' in body_lower:
        # If email contains other email addresses, likely legitimate correspondence
        return True
    
    # Default to RELEVANT - conservative approach
    print(f"[DEBUG] Email marked RELEVANT by default (conservative approach)")
    return True

def clean_email_content(content: str) -> str:
    """Clean and normalize email content"""
    if not content:
        return ""
    
    # Decode HTML entities
    content = html.unescape(content)
    
    # Remove excessive whitespace
    content = re.sub(r'\s+', ' ', content)
    
    # Remove email signatures (simple pattern)
    content = re.sub(r'\n--\n.*', '', content, flags=re.DOTALL)
    
    # Remove forwarded message indicators
    content = re.sub(r'-----Original Message-----.*', '', content, flags=re.DOTALL)
    content = re.sub(r'From:.*Sent:.*To:.*Subject:.*', '', content, flags=re.DOTALL)
    
    # Remove excessive line breaks
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

def extract_email_metadata(email_data: Dict) -> Dict:
    """Extract and normalize email metadata"""
    metadata = {
        'has_attachments': email_data.get('has_attachments', False),
        'is_read': email_data.get('is_read', False),
        'priority': 'normal',  # Default priority
        'word_count': len(email_data.get('body', '').split()),
        'char_count': len(email_data.get('body', '')),
        'domain': extract_domain(email_data.get('sender', '')),
        'time_received': parse_email_timestamp(email_data.get('timestamp', ''))
    }
    
    # Determine priority based on keywords
    subject = email_data.get('subject', '').lower()
    body = email_data.get('body', '').lower()
    
    high_priority_keywords = ['urgent', 'asap', 'immediate', 'critical', 'emergency']
    if any(keyword in subject or keyword in body for keyword in high_priority_keywords):
        metadata['priority'] = 'high'
    
    return metadata

def extract_domain(email_address: str) -> str:
    """Extract domain from email address"""
    try:
        return email_address.split('@')[1].lower()
    except (IndexError, AttributeError):
        return ""

def parse_email_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse email timestamp string to datetime object"""
    try:
        # Handle ISO format with Z
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, AttributeError):
        return None

def format_relative_time(timestamp: str) -> str:
    """Format timestamp as relative time (e.g., '2 hours ago')"""
    try:
        email_time = parse_email_timestamp(timestamp)
        if not email_time:
            return "Unknown time"
        
        now = datetime.now(email_time.tzinfo)
        diff = now - email_time
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    except Exception:
        return "Unknown time"

def generate_email_hash(email_id: str, content: str) -> str:
    """Generate hash for email deduplication"""
    combined = f"{email_id}:{content[:100]}"
    return hashlib.md5(combined.encode()).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized

def estimate_reading_time(content: str) -> int:
    """Estimate reading time in minutes"""
    word_count = len(content.split())
    # Average reading speed: 200 words per minute
    reading_time = max(1, word_count // 200)
    return reading_time

def detect_language(content: str) -> str:
    """Simple language detection (fallback method)"""
    # This is a very basic implementation
    # In production, you might want to use a proper language detection library
    
    english_indicators = ['the', 'and', 'or', 'but', 'with', 'from', 'to', 'at', 'in', 'on']
    words = content.lower().split()
    
    english_word_count = sum(1 for word in words[:50] if word in english_indicators)
    
    if english_word_count >= 3:
        return 'en'
    else:
        return 'unknown'

def extract_action_items(content: str) -> List[str]:
    """Extract potential action items from email content"""
    action_patterns = [
        r'please\s+([^.!?]+)',
        r'could\s+you\s+([^.!?]+)',
        r'can\s+you\s+([^.!?]+)',
        r'need\s+to\s+([^.!?]+)',
        r'should\s+([^.!?]+)',
        r'must\s+([^.!?]+)',
        r'action\s+item[s]?:\s*([^.!?]+)',
        r'todo[s]?:\s*([^.!?]+)',
        r'deadline[s]?:\s*([^.!?]+)'
    ]
    
    action_items = []
    content_lower = content.lower()
    
    for pattern in action_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        for match in matches:
            if len(match.strip()) > 5:  # Filter out very short matches
                action_items.append(match.strip())
    
    return action_items[:5]  # Return max 5 action items

def extract_dates_and_times(content: str) -> List[str]:
    """Extract dates and times mentioned in email content"""
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD or YYYY-MM-DD
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b',
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}\b'
    ]
    
    time_patterns = [
        r'\b\d{1,2}:\d{2}\s*(?:am|pm)?\b',
        r'\b\d{1,2}\s*(?:am|pm)\b'
    ]
    
    found_dates = []
    content_lower = content.lower()
    
    for pattern in date_patterns + time_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        found_dates.extend(matches)
    
    return list(set(found_dates))  # Remove duplicates

def calculate_response_urgency(email_data: Dict) -> str:
    """Calculate response urgency based on email content and metadata"""
    subject = email_data.get('subject', '').lower()
    body = email_data.get('body', '').lower()
    sender_domain = extract_domain(email_data.get('sender', ''))
    
    urgency_score = 0
    
    # Check for urgent keywords
    urgent_keywords = ['urgent', 'asap', 'immediate', 'critical', 'emergency', 'deadline']
    urgency_score += sum(2 for keyword in urgent_keywords if keyword in subject)
    urgency_score += sum(1 for keyword in urgent_keywords if keyword in body)
    
    # Check for time-sensitive words
    time_sensitive = ['today', 'tomorrow', 'this week', 'by friday', 'end of day', 'eod']
    urgency_score += sum(1 for phrase in time_sensitive if phrase in body)
    
    # Check sender domain (internal vs external)
    if sender_domain and any(domain in sender_domain for domain in ['gmail.com', 'outlook.com', 'yahoo.com']):
        urgency_score -= 1  # Personal emails might be less urgent
    
    # Check for question marks (might need response)
    urgency_score += min(2, body.count('?'))
    
    if urgency_score >= 4:
        return 'high'
    elif urgency_score >= 2:
        return 'medium'
    else:
        return 'low'

def validate_environment() -> Dict[str, bool]:
    """Validate that all required environment variables are set"""
    required_vars = [
        'FLASK_SECRET_KEY',
        'OUTLOOK_CLIENT_ID',
        'OUTLOOK_CLIENT_SECRET',
        'REDIRECT_URI',
        'FRONTEND_URL'
    ]
    
    validation_result = {}
    for var in required_vars:
        validation_result[var] = bool(os.getenv(var))
    
    return validation_result