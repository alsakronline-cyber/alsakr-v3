import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from app.core.config import Settings
import logging

settings = Settings()
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME

    def _send_sync(self, to_email: str, subject: str, html_content: str):
        """Blocking SMTP send function."""
        try:
            msg = MIMEMultipart()
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_content, "html"))

            # Connect (SSL or TLS)
            if self.smtp_port == 465:
                # Implicit SSL
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            else:
                # STARTTLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            
            logger.info(f"📧 Email sent to {to_email}: {subject}")
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")

    async def send_email(self, to_email: str, subject: str, html_content: str):
        """Async wrapper for sending emails without blocking event loop."""
        # Run the blocking _send_sync in a separate thread
        await asyncio.to_thread(self._send_sync, to_email, subject, html_content)

    async def send_inquiry_notification(self, inquiry: Dict[str, Any]):
        """Notify Admin about a new inquiry."""
        subject = f"🆕 New Inquiry from {inquiry.get('buyer_id')}"
        
        products_html = "<ul>"
        for p in inquiry.get('products', []):
            products_html += f"<li>{p.get('name', 'Product')} (Qty: {p.get('quantity', 1)})</li>"
        products_html += "</ul>"

        body = f"""
        <h2>New Inquiry Received</h2>
        <p><strong>Buyer:</strong> {inquiry.get('buyer_id')}</p>
        <p><strong>Message:</strong> {inquiry.get('message', 'No message')}</p>
        <h3>Products:</h3>
        {products_html}
        <br>
        <a href="https://app.alsakronline.com/vendor/dashboard">View in Vendor Dashboard</a>
        """
        
        # Send to Admin (Sales)
        await self.send_email(settings.ADMIN_EMAIL, subject, body)

    async def send_quote_notification(self, quote: Dict[str, Any]):
        """Notify Buyer about a new quote."""
        # We need the buyer's email. 
        # CAUTION: The quote object might only have 'inquiry_id'. 
        # We might need to fetch the inquiry to get the buyer_id, 
        # OR assume the caller passes the buyer email.
        # For MVP: We will fetch the inquiry if not provided, or optimize later.
        # Actually, let's defer this complexity. Ideally, InquiryService handles this.
        # But QuoteService creates the quote.
        pass # To be implemented when integrating call

    async def send_quote_status_notification(self, quote: Dict[str, Any], status: str):
        """Notify Vendor about quote acceptance/rejection."""
        subject = f"Quote {quote.get('id')} was {status.upper()}"
        body = f"""
        <h2>Quote Update</h2>
        <p>The quote for Inquiry {quote.get('inquiry_id')} has been <strong>{status}</strong>.</p>
        <br>
        <a href="https://app.alsakronline.com/vendor/dashboard">View Dashboard</a>
        """
        await self.send_email(settings.ADMIN_EMAIL, subject, body)

email_service = EmailService()
