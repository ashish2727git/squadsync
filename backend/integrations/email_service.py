"""
SendGrid Email Integration
"""
import os
from typing import List, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@squadsync.com')
        self.from_name = os.getenv('SENDGRID_FROM_NAME', 'SquadSync')

    async def send_verification_email(
        self, 
        to_email: str, 
        username: str, 
        verification_token: str
    ):
        """Send email verification"""
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        verify_url = f"{frontend_url}/verify-email?token={verification_token}"
        
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=To(to_email),
            subject='Verify your SquadSync email',
            html_content=f"""
            <h2>Welcome to SquadSync, {username}!</h2>
            <p>Click the link below to verify your email:</p>
            <a href="{verify_url}">Verify Email</a>
            <p>Or copy this link: {verify_url}</p>
            <p>This link expires in 24 hours.</p>
            """
        )
        
        try:
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending verification email: {e}")
            return False

    async def send_password_reset_email(
        self, 
        to_email: str, 
        username: str, 
        reset_token: str
    ):
        """Send password reset email"""
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=To(to_email),
            subject='Reset your SquadSync password',
            html_content=f"""
            <h2>Password Reset Request</h2>
            <p>Hi {username},</p>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_url}">Reset Password</a>
            <p>Or copy this link: {reset_url}</p>
            <p>This link expires in 1 hour.</p>
            <p>If you didn't request this, ignore this email.</p>
            """
        )
        
        try:
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending password reset email: {e}")
            return False

    async def send_squad_invite_email(
        self, 
        to_email: str, 
        squad_name: str, 
        inviter_name: str, 
        invite_link: str
    ):
        """Send squad invitation email"""
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=To(to_email),
            subject=f'{inviter_name} invited you to join {squad_name}',
            html_content=f"""
            <h2>You're invited to join {squad_name}!</h2>
            <p>{inviter_name} has invited you to join their squad on SquadSync.</p>
            <a href="{invite_link}">Join Squad</a>
            <p>Or copy this link: {invite_link}</p>
            """
        )
        
        try:
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending squad invite email: {e}")
            return False

    async def send_summon_notification_email(
        self, 
        to_email: str, 
        squad_name: str, 
        summoner_name: str, 
        message_text: str
    ):
        """Send summon notification email"""
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=To(to_email),
            subject=f'🚨 Squad Summon: {squad_name}',
            html_content=f"""
            <h2>You've been summoned!</h2>
            <p><strong>{summoner_name}</strong> summoned the squad:</p>
            <blockquote>{message_text}</blockquote>
            <p><a href="{os.getenv('FRONTEND_URL')}/squads">View Squad</a></p>
            """
        )
        
        try:
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending summon email: {e}")
            return False

# Global instance
email_service = EmailService()
