import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from app.config import settings

logger = logging.getLogger("gtm_center.email_sender")


def send_cold_email(
    to_email: str,
    subject: str,
    body: str,
    prospect_name: Optional[str] = None,
    company_name: Optional[str] = None,
) -> dict:
    """
    Sends a cold outreach email via Gmail SMTP.
    Requires SMTP_EMAIL and SMTP_APP_PASSWORD in environment settings.
    
    Returns dict with success status and message.
    """
    if not settings.smtp_email or not settings.smtp_app_password:
        logger.warning("SMTP credentials not configured. Email not sent.")
        return {
            "success": False,
            "error": "SMTP credentials not configured. Add SMTP_EMAIL and SMTP_APP_PASSWORD in backend .env file."
        }

    try:
        # Build HTML email with GTM branding
        html_body = _build_html_email(
            subject=subject,
            body=body,
            prospect_name=prospect_name,
            company_name=company_name
        )

        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"GTM Command Center <{settings.smtp_email}>"
        msg["To"] = to_email

        # Attach plain text fallback + HTML version
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Connect to Gmail SMTP and send
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.smtp_email, settings.smtp_app_password)
            server.sendmail(settings.smtp_email, to_email, msg.as_string())

        logger.info(f"Cold email sent successfully to {to_email}")
        return {
            "success": True,
            "message": f"Email successfully sent to {to_email}",
            "to": to_email,
            "subject": subject,
        }

    except smtplib.SMTPAuthenticationError:
        logger.error("Gmail authentication failed. Check your App Password.")
        return {
            "success": False,
            "error": "Gmail authentication failed. Make sure you're using a Gmail App Password (not your regular password). Enable 2FA first at myaccount.google.com/security"
        }
    except smtplib.SMTPRecipientsRefused:
        logger.error(f"Recipient email refused: {to_email}")
        return {
            "success": False,
            "error": f"Email address {to_email} was refused by Gmail. Please check the address."
        }
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to send email: {str(e)}"
        }


def _build_html_email(
    subject: str,
    body: str,
    prospect_name: Optional[str] = None,
    company_name: Optional[str] = None,
) -> str:
    """Builds a beautiful HTML email template for cold outreach."""
    
    # Format body with line breaks for HTML
    html_body_lines = body.replace("\n", "<br>")
    
    greeting = f"Hi {prospect_name}," if prospect_name else "Hi,"
    company_tag = f"<span style='color:#a78bfa;'>@ {company_name}</span>" if company_name else ""

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
    </head>
    <body style="margin:0;padding:0;background:#0f0f1a;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f1a;padding:40px 20px;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="background:#13131f;border-radius:16px;border:1px solid #1e1e3a;overflow:hidden;">
              
              <!-- Header -->
              <tr>
                <td style="background:linear-gradient(135deg,#6d28d9,#4f46e5);padding:24px 32px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td>
                        <span style="font-size:11px;font-weight:700;letter-spacing:3px;color:#c4b5fd;text-transform:uppercase;">Agentic GTM Command Center</span>
                        <h1 style="margin:4px 0 0;font-size:20px;font-weight:700;color:#ffffff;">AI-Powered Outreach {company_tag}</h1>
                      </td>
                      <td align="right">
                        <span style="background:rgba(255,255,255,0.15);color:#fff;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:1px;">AI SDR</span>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:32px;">
                  <p style="font-size:14px;color:#94a3b8;margin:0 0 8px;">{greeting}</p>
                  <div style="font-size:15px;line-height:1.75;color:#e2e8f0;margin:0;">
                    {html_body_lines}
                  </div>
                </td>
              </tr>

              <!-- Divider -->
              <tr>
                <td style="padding:0 32px;">
                  <hr style="border:none;border-top:1px solid #1e1e3a;margin:0;">
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="padding:20px 32px;">
                  <p style="font-size:11px;color:#475569;margin:0;line-height:1.6;">
                    This email was generated and sent by the 
                    <strong style="color:#7c3aed;">Agentic GTM Command Center</strong> — 
                    an autonomous AI sales intelligence platform.<br>
                    To unsubscribe, reply with "UNSUBSCRIBE" in the subject line.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
