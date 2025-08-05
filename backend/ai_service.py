import requests
import json
from typing import List, Dict, Optional
import re

class OllamaService:
    """Service for interacting with Ollama local LLM"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "phi3:mini"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api"
    
    def check_health(self) -> bool:
        """Check if Ollama service is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            return any(self.model in name for name in model_names)
        except Exception as e:
            print(f"Ollama health check failed: {str(e)}")
            return False
    
    def _make_request(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Make request to Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent classification
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
        except Exception as e:
            print(f"Error making Ollama request: {str(e)}")
        
        return None
    
    def check_email_relevance(self, email_body: str, subject: str) -> bool:
        """Check if email is relevant (not spam, ads, or irrelevant content)"""
        system_prompt = """You are an email relevance classifier. You should be VERY CONSERVATIVE about marking emails as not relevant.

        Mark as NOT_RELEVANT ONLY if the email is clearly:
        - Obvious spam (Nigerian prince, lottery winnings, etc.)
        - Mass marketing campaigns with unsubscribe links
        - Automated promotional emails from retailers
        - Clear phishing attempts
        - Newsletter subscriptions that are clearly promotional

        Mark as RELEVANT if the email contains:
        - Any personal communication (even if brief)
        - Work-related content (interviews, leave requests, project updates)
        - Important notifications (password changes, account updates)
        - Meeting invitations or scheduling
        - Any form of direct communication between people
        - Client or customer communications
        - Service notifications from legitimate companies
        - Any email that might require a response

        When in doubt, always choose RELEVANT. It's better to include an email than to miss something important.

        IMPORTANT: Respond with ONLY one word: either 'RELEVANT' or 'NOT_RELEVANT'. Do not provide explanations or additional text."""
        
        prompt = f"""
        Email Subject: {subject}
        
        Email Content (first 500 chars): {email_body[:500]}
        
        Classification:"""
        
        response = self._make_request(prompt, system_prompt)
        
        if response:
            # Clean the response to extract just the classification
            response_clean = response.upper().strip()
            
            # Look for RELEVANT or NOT_RELEVANT in the response
            if 'NOT_RELEVANT' in response_clean or 'NOT RELEVANT' in response_clean:
                classification = 'NOT_RELEVANT'
            elif 'RELEVANT' in response_clean:
                classification = 'RELEVANT'
            else:
                # If unclear, default to relevant
                classification = 'RELEVANT'
                
            print(f"[DEBUG] AI Classification for '{subject[:30]}...': {classification}")
            return classification == 'RELEVANT'
        
        # If AI fails, default to relevant (conservative approach)
        print(f"[DEBUG] AI classification failed for '{subject[:30]}...', defaulting to RELEVANT")
        return True
    
    def summarize_email(self, email_body: str, subject: str) -> str:
        """Generate a concise, human-like summary of the email"""
        system_prompt = """You are an expert email summarizer. Create concise bullet-point summaries.

        Guidelines:
        - Use 1-3 bullet points maximum
        - Focus on key information and action items
        - Use simple, natural language
        - Highlight deadlines or requests
        - Mention if response is needed
        - Keep each point to 1 short sentence"""
        
        prompt = f"""
        Subject: {subject}
        
        Email Content: {email_body}
        
        Please provide a bullet-point summary:"""
        
        response = self._make_request(prompt, system_prompt)
        
        if response:
            lines = response.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('•') and not line.startswith('-'):
                    line = f"• {line}"
                if line:
                    formatted_lines.append(line)
            
            return '\n'.join(formatted_lines)
        
        return f"• Email from {subject} - content review needed"
    
    def generate_reply(self, email_body: str, subject: str, context: List[Dict] = None) -> str:
        """Generate a professional, human-like reply to the email"""
        system_prompt = """You are an email assistant helping to draft professional replies. Read the email carefully and understand the context before responding.

        Guidelines:
        - Write as if you are the recipient responding directly 
        - Be concise (1-2 sentences maximum)
        - Use a natural, conversational tone
        - Address the main point of the email appropriately
        - If someone is sharing information with you, acknowledge it appropriately
        - If someone is asking a question, answer it directly
        - If it's a status update or FYI, acknowledge receipt and thank them
        - Use appropriate greetings (Hi [Name of sender]) and professional closings
        - Do NOT respond as if you are the sender of the original email
        - Use Regards name as Aditya Mishra as he is the owner of this mail also keep this mind while responding that this mail is received to Aditya Mishra

        Important: Understand who is writing to whom and respond accordingly."""
        
        # Extract sender name from context or subject for personalization
        sender_name = "there"
        if context and len(context) > 0:
            sender_email = context[0].get('sender', '')
            if '@' in sender_email:
                sender_name = sender_email.split('@')[0].title()
        
        context_str = ""
        if context and len(context) > 1:
            context_str = "\n\nConversation Context (previous messages):\n"
            for i, msg in enumerate(context[:-1]):
                context_str += f"{i+1}. From {msg['sender']}: {msg['body'][:100]}...\n"
        
        prompt = f"""
        Original Email Subject: {subject}
        
        Original Email Content: {email_body[:800]}
        {context_str}
        
        Please write a professional and appropriate reply. Remember to respond as the recipient of this email:"""
        
        response = self._make_request(prompt, system_prompt)
        
        if response:
            reply = response.strip()
            
            # Clean up any AI artifacts
            reply = reply.replace("Subject:", "").replace("Dear recipient", "Hi")
            
            # Add appropriate greeting if not present
            if not any(greeting in reply.lower()[:50] for greeting in ['hi', 'hello', 'dear', 'thank you']):
                if sender_name and sender_name != "there":
                    reply = f"Hi {sender_name},\n\n{reply}"
                else:
                    reply = f"Hi,\n\n{reply}"
            
            # Add closing if not present
            if not any(closing in reply.lower()[-100:] for closing in ['regards', 'best', 'thanks', 'sincerely']):
                reply = f"{reply}\n\nBest regards"
            
            return reply
        
        return "Thank you for your email. I'll review this and get back to you soon.\n\nBest regards"
    
    def enhance_reply(self, original_reply: str, additional_context: str = "") -> str:
        """Enhance or modify an existing reply"""
        system_prompt = """Help improve an email reply. Make it more natural and professional while keeping the core message."""
        
        prompt = f"""
        Original Reply: {original_reply}
        
        Additional Context: {additional_context}
        

        Please improve this reply:"""
        
        response = self._make_request(prompt, system_prompt)
        return response if response else original_reply