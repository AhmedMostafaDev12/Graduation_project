from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings


def _send_email(to_email: str, subject: str, html_content: str):
    """
    Internal helper to send an email using SendGrid.
    """
    message = Mail(
        from_email=settings.app_sender_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)
        print(f"Email sent to {to_email}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")


def send_reset_email(to_email: str, token: str):
    subject = "Reset Your Sentry AI Password"
    reset_link = f"{settings.backend_base_url}/api/auth/reset-password?token={token}"  
    
    html_content = f"<p>Click <a href='{reset_link}'>here</a> to reset your password.</p>"
    _send_email(to_email, subject, html_content)


def send_verification_email(to_email: str, token: str):
    verification_link = f"{settings.backend_base_url}/api/auth/verify-email?token={token}"
    subject = "Verify Your Email - Sentry AI"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Email</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 40px 0; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">
                        🛡️ Sentry AI
                    </h1>
                    <p style="color: #f0f0f0; margin: 8px 0 0 0; font-size: 14px;">
                        Burnout Prevention & Wellness Platform
                    </p>
                </td>
            </tr>
            <tr>
                <td style="padding: 0;">
                    <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-top: -20px;">
                        <tr>
                            <td style="padding: 40px 40px 30px 40px;">
                                <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px; font-weight: 600;">
                                    Welcome to Sentry AI! 👋
                                </h2>
                                <p style="color: #666666; margin: 0 0 20px 0; font-size: 16px; line-height: 1.6;">
                                    Thank you for signing up. We're excited to help you prevent burnout and maintain a healthy work-life balance.
                                </p>
                                <p style="color: #666666; margin: 0 0 30px 0; font-size: 16px; line-height: 1.6;">
                                    To get started, please verify your email address by clicking the button below:
                                </p>

                                <!-- Verification Button -->
                                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                    <tr>
                                        <td style="text-align: center; padding: 0 0 30px 0;">
                                            <a href="{verification_link}"
                                               style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.4); transition: all 0.3s ease;">
                                                ✓ Verify Email Address
                                            </a>
                                        </td>
                                    </tr>
                                </table>

                                <div style="background-color: #f8f9fa; border-left: 4px solid #667eea; padding: 15px 20px; margin: 0 0 30px 0; border-radius: 4px;">
                                    <p style="color: #555555; margin: 0; font-size: 14px; line-height: 1.5;">
                                        <strong>🔒 Security Note:</strong> This link will expire in 24 hours for your security.
                                    </p>
                                </div>

                                <p style="color: #666666; margin: 0 0 10px 0; font-size: 14px; line-height: 1.6;">
                                    If the button doesn't work, copy and paste this link into your browser:
                                </p>
                                <p style="margin: 0 0 30px 0;">
                                    <a href="{verification_link}"
                                       style="color: #667eea; font-size: 13px; word-break: break-all; text-decoration: underline;">
                                        {verification_link}
                                    </a>
                                </p>

                                <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">

                                <p style="color: #999999; margin: 0; font-size: 13px; line-height: 1.6;">
                                    If you didn't create an account with Sentry AI, you can safely ignore this email.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 30px 0; text-align: center;">
                    <p style="color: #999999; margin: 0 0 10px 0; font-size: 12px;">
                        © 2025 Sentry AI. All rights reserved.
                    </p>
                    <p style="color: #999999; margin: 0; font-size: 12px;">
                        Your burnout prevention companion
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    _send_email(to_email, subject, html_content)
