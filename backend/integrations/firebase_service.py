"""
Firebase Cloud Messaging for Push Notifications
"""
import os
import json
from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, messaging

class FirebaseService:
    def __init__(self):
        # Initialize Firebase Admin SDK
        cred_dict = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        try:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except ValueError:
            # Already initialized
            pass

    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> bool:
        """Send push notification to single device"""
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=token
        )
        
        try:
            response = messaging.send(message)
            return True
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False

    async def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> dict:
        """Send notification to multiple devices"""
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            tokens=tokens
        )
        
        try:
            response = messaging.send_multicast(message)
            return {
                'success_count': response.success_count,
                'failure_count': response.failure_count
            }
        except Exception as e:
            print(f"Error sending multicast: {e}")
            return {'success_count': 0, 'failure_count': len(tokens)}

    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> bool:
        """Send notification to topic subscribers"""
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            topic=topic
        )
        
        try:
            response = messaging.send(message)
            return True
        except Exception as e:
            print(f"Error sending to topic: {e}")
            return False

    async def subscribe_to_topic(
        self,
        tokens: List[str],
        topic: str
    ) -> dict:
        """Subscribe tokens to topic"""
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            return {
                'success_count': response.success_count,
                'failure_count': response.failure_count
            }
        except Exception as e:
            print(f"Error subscribing to topic: {e}")
            return {'success_count': 0, 'failure_count': len(tokens)}

firebase_service = FirebaseService()
