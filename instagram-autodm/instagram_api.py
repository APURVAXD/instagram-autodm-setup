import requests
import os

class InstagramAPI:
    """Instagram Graph API wrapper"""
    
    BASE_URL = "https://graph.facebook.com/v19.0"
    
    def __init__(self, access_token):
        self.access_token = access_token
    
    def get_user_info(self):
        """Get Instagram user profile info"""
        url = f"{self.BASE_URL}/me"
        params = {
            'fields': 'id,username',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_instagram_business_account(self, page_id):
        """Get Instagram Business Account ID from Page"""
        url = f"{self.BASE_URL}/{page_id}"
        params = {
            'fields': 'instagram_business_account',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('instagram_business_account', {}).get('id')
    
    def get_recent_media(self, instagram_user_id, limit=10):
        """Get recent posts"""
        url = f"{self.BASE_URL}/{instagram_user_id}/media"
        params = {
            'fields': 'id,caption,media_type,media_url,permalink,timestamp',
            'limit': limit,
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        return response.json().get('data', [])
    
    def get_comments_on_media(self, media_id):
        """Get comments on a specific post"""
        url = f"{self.BASE_URL}/{media_id}/comments"
        params = {
            'fields': 'id,text,username,timestamp,from{id,username}',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        return response.json().get('data', [])
    
    def reply_to_comment(self, comment_id, message):
        """Reply to a comment"""
        url = f"{self.BASE_URL}/{comment_id}/replies"
        data = {
            'message': message,
            'access_token': self.access_token
        }
        response = requests.post(url, data=data)
        return response.json()
    
    def send_dm(self, instagram_user_id, recipient_id, message, cta_button_text=None, cta_button_url=None):
        """Send DM to user"""
        url = f"{self.BASE_URL}/{instagram_user_id}/messages"
        
        # Build message payload
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message},
            'access_token': self.access_token
        }
        
        # Add CTA button if provided
        if cta_button_text and cta_button_url:
            payload['message']['attachment'] = {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': message,
                    'buttons': [{
                        'type': 'web_url',
                        'url': cta_button_url,
                        'title': cta_button_text
                    }]
                }
            }
            # Remove redundant text when using template
            del payload['message']['text']
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def subscribe_to_webhooks(self, instagram_user_id):
        """Subscribe to comment webhooks"""
        url = f"{self.BASE_URL}/{instagram_user_id}/subscribed_apps"
        data = {
            'subscribed_fields': 'comments',
            'access_token': self.access_token
        }
        response = requests.post(url, data=data)
        return response.json()
    
    @staticmethod
    def get_long_lived_token(short_lived_token, app_id, app_secret):
        """Exchange short-lived token for long-lived token (60 days)"""
        url = "https://graph.facebook.com/v19.0/oauth/access_token"
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': app_id,
            'client_secret': app_secret,
            'fb_exchange_token': short_lived_token
        }
        response = requests.get(url, params=params)
        return response.json().get('access_token')
    
    @staticmethod
    def get_user_pages(access_token):
        """Get Facebook Pages connected to user"""
        url = "https://graph.facebook.com/v19.0/me/accounts"
        params = {
            'access_token': access_token
        }
        response = requests.get(url, params=params)
        return response.json().get('data', [])
