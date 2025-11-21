import resend
from app.core.config import settings

class ResendClient:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.no_reply_default_sender = settings.RESEND_NO_REPLY_DEFAULT_SENDER
        resend.api_key = self.api_key
    
    def send_mail(self, sender, to, subject, html=None, text=None):
        if not html and not text:
            raise ValueError("Either 'html' or 'text' must be provided.")
        params: resend.Emails.SendParams = {
            "from": sender or self.default_sender,
            "to": to,
            "subject": subject
        }
        if html:
            params["html"] = html
        if text:
            params["text"] = text
        email: resend.Email = resend.Emails.send(params)
        return email
    
    def send_login_code(self, code, email):
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
                <h2 style="margin-bottom: 10px;">Your Login Code</h2>

                <p style="font-size: 18px; margin: 0 0 20px;">
                    Use the code below to complete your sign-in:
                    <br><br>
                    <strong style="font-size: 24px;">{code}</strong>
                </p>

                <p style="font-size: 12px; line-height: 1.4; color: #666;">
                    This code will expire in 10 minutes. If it expires before you use it,
                    simply sign in again to receive a new code.
                </p>
            </body>
        </html>
        """
        self.send_mail(
            sender=self.no_reply_default_sender,
            to=[email],
            subject="Your Login Code",
            html=html,
        )
            