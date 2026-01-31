"""
Twilio Integration for WebRTC TURN servers and voice quality
"""
import os
from typing import Optional
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.api_key_sid = os.getenv('TWILIO_API_KEY_SID')
        self.api_key_secret = os.getenv('TWILIO_API_KEY_SECRET')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None

    def generate_turn_credentials(self, username: str) -> dict:
        """
        Generate TURN server credentials for WebRTC
        This provides better voice quality and connection reliability
        """
        if not self.client:
            # Fallback to free STUN servers
            return {
                'iceServers': [
                    {'urls': 'stun:stun.l.google.com:19302'},
                    {'urls': 'stun:stun1.l.google.com:19302'},
                ]
            }
        
        try:
            # Get Twilio TURN credentials
            token = self.client.tokens.create()
            
            return {
                'iceServers': token.ice_servers
            }
        except Exception as e:
            print(f"Error generating TURN credentials: {e}")
            return {
                'iceServers': [
                    {'urls': 'stun:stun.l.google.com:19302'},
                ]
            }

    def generate_video_access_token(
        self, 
        identity: str, 
        room_name: str
    ) -> str:
        """
        Generate Twilio Video access token for enhanced video calls
        """
        if not self.api_key_sid or not self.api_key_secret:
            raise Exception("Twilio API credentials not configured")
        
        token = AccessToken(
            self.account_sid,
            self.api_key_sid,
            self.api_key_secret,
            identity=identity
        )
        
        # Grant access to Twilio Video
        video_grant = VideoGrant(room=room_name)
        token.add_grant(video_grant)
        
        return token.to_jwt()

    async def send_sms(
        self, 
        to_number: str, 
        message: str
    ) -> bool:
        """Send SMS notification"""
        if not self.client:
            print("Twilio not configured, skipping SMS")
            return False
        
        try:
            from_number = os.getenv('TWILIO_PHONE_NUMBER')
            if not from_number:
                print("TWILIO_PHONE_NUMBER not set")
                return False
            
            message = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            return message.sid is not None
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    def get_ice_servers(self) -> dict:
        """
        Get ICE servers configuration for WebRTC
        Returns Twilio TURN servers if available, otherwise free STUN servers
        """
        return self.generate_turn_credentials("anonymous")

twilio_service = TwilioService()
