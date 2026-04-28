from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.core.config import settings
from pydantic import EmailStr
from typing import List
import os

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
    MAIL_STARTTLS=False, # Port 465 is SSL/TLS
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class EmailService:
    @staticmethod
    async def send_email(subject: str, recipients: List[EmailStr], body: str):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message)

    @staticmethod
    async def send_reset_password_email(email: str, token: str):
        # In a real app, this would be a full URL to the frontend
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        subject = "Vatify - Reset Your Password"
        body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px; line-height: 1.6;">
            <h2 style="color: #2563eb;">Reset Your Password</h2>
            <p>You requested a password reset for your Vatify account.</p>
            <p>Click the button below to set a new password. This link will expire in 15 minutes.</p>
            <a href="{reset_link}" style="display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0;">Reset Password</a>
            <p>If you didn't request this, you can safely ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            <p style="font-size: 12px; color: #64748b;">Vatify - Smart KRA Compliance for Kenya</p>
        </body>
        </html>
        """
        await EmailService.send_email(subject, [email], body)

    @staticmethod
    async def send_mfa_otp_email(email: str, otp: str):
        subject = "Vatify - Your Verification Code"
        body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px; line-height: 1.6;">
            <h2 style="color: #2563eb;">Verify Your Login</h2>
            <p>Your one-time verification code is:</p>
            <div style="font-size: 32px; font-weight: 900; letter-spacing: 4px; color: #2563eb; padding: 20px; background: #f8fafc; border-radius: 8px; text-align: center; margin: 20px 0;">
                {otp}
            </div>
            <p>This code will expire in 5 minutes. Do not share this code with anyone.</p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            <p style="font-size: 12px; color: #64748b;">Vatify Security</p>
        </body>
        </html>
        """
        await EmailService.send_email(subject, [email], body)
    @staticmethod
    async def send_verification_email(email: str, token: str):
        # Activation link for the frontend
        verify_link = f"http://localhost:3000/verify-account?token={token}"
        subject = "Vatify - Please Verify Your Account"
        body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                <div style="background-color: #2563eb; padding: 20px; text-align: center;">
                    <h2 style="color: white; margin: 0;">Welcome to Vatify</h2>
                </div>
                <div style="padding: 30px;">
                    <h3 style="color: #1e293b;">Final Step: Activate Your Account</h3>
                    <p>Thank you for signing up for Vatify. To start managing your KRA compliance, please verify your email address by clicking the button below.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verify_link}" style="display: inline-block; padding: 14px 30px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">Verify My Account</a>
                    </div>
                    <p style="color: #64748b; font-size: 14px;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="color: #2563eb; font-size: 12px; word-break: break-all;">{verify_link}</p>
                    <p>If you didn't create an account, you can safely ignore this email.</p>
                </div>
                <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="font-size: 12px; color: #64748b; margin: 0;">Vatify - Smart Compliance for Kenya</p>
                </div>
            </div>
        </body>
        </html>
        """
        await EmailService.send_email(subject, [email], body)
