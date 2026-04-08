"""
IMAP Email Ingestion.
Run this on a schedule (cron / management command) to pull new emails.
"""
import imaplib
import email
from email.header import decode_header
from django.conf import settings
from .models import Ticket
from .classifier import classify
from .assignment import auto_assign


def decode_str(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return value or ''


def get_email_body(msg):
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode('utf-8', errors='replace')
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode('utf-8', errors='replace')
    return body.strip()


def fetch_and_create_tickets():
    """
    Connect to IMAP, read unseen emails, create tickets.
    Returns count of tickets created.
    """
    created = 0
    try:
        mail = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
        mail.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
        mail.select(settings.IMAP_FOLDER)

        _, message_ids = mail.search(None, 'UNSEEN')

        for msg_id in message_ids[0].split():
            _, msg_data = mail.fetch(msg_id, '(RFC822)')
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            # Decode subject
            subject_parts = decode_header(msg.get('Subject', 'No Subject'))
            title = ''.join(
                decode_str(part) if isinstance(part, bytes) else part
                for part, enc in subject_parts
            )

            sender = msg.get('From', 'unknown@unknown.com')
            # Extract just the email address
            if '<' in sender:
                user_email = sender.split('<')[1].strip('>')
            else:
                user_email = sender.strip()

            body = get_email_body(msg)

            # Classify
            result = classify(title, body)

            # Create ticket
            ticket = Ticket.objects.create(
                title=title or 'No Subject',
                description=body or '(No body)',
                user_email=user_email,
                category=result['category'],
                priority=result['priority'],
                required_level=result['level'],
                sla_hours=result['sla_hours'],
                raw_email=raw.decode('utf-8', errors='replace'),
            )

            # Auto assign
            assignee = auto_assign(ticket)
            if assignee:
                ticket.assigned_to = assignee
                ticket.save()

            # Mark as read
            mail.store(msg_id, '+FLAGS', '\\Seen')
            created += 1

        mail.logout()

    except Exception as e:
        print(f"[Email Ingestion Error] {e}")

    return created
