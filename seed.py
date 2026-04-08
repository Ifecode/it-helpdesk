"""
Seed script: creates demo users, profiles, tickets, and knowledge articles.
Run with: python manage.py shell < seed.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from tickets.models import Profile, Ticket, TicketComment
from knowledge.models import Article
import random

# ── Users ──────────────────────────────────────────────────────────────────
users_data = [
    ('manager',    'manager',    'Mike',   'Adeyemi',   'manager'),
    ('senior1',    'senior1',    'Sarah',  'Okonkwo',   'senior'),
    ('consultant1','consultant1','James',  'Bello',     'consultant'),
    ('consultant2','consultant2','Amaka',  'Chukwu',    'consultant'),
    ('associate1', 'associate1', 'Tunde',  'Adeola',    'associate'),
    ('associate2', 'associate2', 'Ngozi',  'Eze',       'associate'),
]

created_users = {}
for username, password, first, last, role in users_data:
    user, _ = User.objects.get_or_create(username=username, defaults={
        'first_name': first, 'last_name': last,
        'email': f'{username}@company.com', 'is_staff': True,
    })
    user.set_password(password)
    user.save()
    Profile.objects.update_or_create(user=user, defaults={'role': role})
    created_users[role] = created_users.get(role, []) + [user]

print(f"✅ Created {len(users_data)} users")

# ── Tickets ─────────────────────────────────────────────────────────────────
ticket_data = [
    ('Cannot connect to VPN from home', 'I have been trying to connect to the office VPN since morning but it keeps timing out. I am using Windows 11.', 'john.doe@company.com', 'network', 'high', 'consultant', 4, 'in_progress'),
    ('Password reset request', 'I forgot my password and cannot log in to my machine. Please help urgently.', 'mary.jones@company.com', 'password', 'medium', 'associate', 4, 'resolved'),
    ('Printer not working on 3rd floor', 'The HP printer near the conference room is offline. Multiple staff affected.', 'peter.smith@company.com', 'printer', 'low', 'associate', 8, 'open'),
    ('New staff onboarding - Chidi Obi', 'New developer joining Monday. Needs laptop, email, GitHub and Jira access set up.', 'hr@company.com', 'onboarding', 'high', 'senior', 24, 'open'),
    ('Outlook keeps crashing on startup', 'Every time I open Outlook it crashes after 2 seconds. Tried restarting. Using Office 365.', 'fatima.musa@company.com', 'email', 'medium', 'consultant', 8, 'in_progress'),
    ('Request access to Finance shared drive', 'I have been moved to the Finance team and need access to their shared folder on the server.', 'emeka.obi@company.com', 'access', 'medium', 'consultant', 8, 'open'),
    ('Laptop screen flickering badly', 'My Dell laptop screen has been flickering since yesterday. Makes it hard to work.', 'aisha.balogun@company.com', 'hardware', 'high', 'consultant', 8, 'open'),
    ('Cannot install Figma — admin rights', 'Trying to install Figma for the design project but need admin rights to proceed.', 'design@company.com', 'software', 'low', 'associate', 24, 'resolved'),
    ('Entire office internet is down', 'No internet across the building since 9am. Affects all departments. Critical.', 'ceo@company.com', 'network', 'critical', 'manager', 1, 'resolved'),
    ('Email not syncing on phone', 'My work email stopped syncing on my iPhone. Tried removing and re-adding the account.', 'tola.adebayo@company.com', 'email', 'medium', 'consultant', 8, 'open'),
]

staff_by_level = created_users

def pick_staff(level):
    pool = created_users.get(level, [])
    if not pool:
        # fallback up the chain
        for fallback in ['associate', 'consultant', 'senior', 'manager']:
            pool = created_users.get(fallback, [])
            if pool:
                break
    return random.choice(pool) if pool else None

tickets = []
for i, (title, desc, email, cat, pri, level, sla, status) in enumerate(ticket_data):
    assignee = pick_staff(level)
    resolved_at = None
    if status == 'resolved':
        resolved_at = timezone.now() - timezone.timedelta(hours=random.randint(1, sla))
    t = Ticket.objects.create(
        title=title, description=desc, user_email=email,
        category=cat, priority=pri, required_level=level,
        sla_hours=sla, status=status, assigned_to=assignee,
        resolved_at=resolved_at,
        created_at=timezone.now() - timezone.timedelta(hours=random.randint(1, 48)),
    )
    # Force the created_at (auto_now_add workaround)
    Ticket.objects.filter(pk=t.pk).update(
        created_at=timezone.now() - timezone.timedelta(hours=random.randint(2, 72))
    )
    tickets.append(t)

print(f"✅ Created {len(tickets)} tickets")

# ── Comments ─────────────────────────────────────────────────────────────────
TicketComment.objects.create(ticket=tickets[0], author=pick_staff('consultant'), body='Checked firewall logs — seems like UDP port 1194 is blocked. Escalating to network team.')
TicketComment.objects.create(ticket=tickets[1], author=pick_staff('associate'), body='Reset password via AD. User confirmed they can log in.')
TicketComment.objects.create(ticket=tickets[4], author=pick_staff('consultant'), body='Cleared Outlook profile cache. Issue persists. Will try repair install.')
print("✅ Added comments")

# ── Knowledge Articles ────────────────────────────────────────────────────────
articles = [
    ('How to Fix VPN Timeout Issues', 'network', 'vpn, windows, remote',
     '1. Ensure UDP port 1194 is open on your router.\n2. Try switching from UDP to TCP in VPN settings.\n3. Flush DNS: run `ipconfig /flushdns` in Command Prompt.\n4. Reinstall the VPN client if issue persists.\n5. Contact IT if none of the above works.'),
    ('Password Reset Procedure', 'password', 'password, active-directory, account',
     '1. Go to https://aka.ms/sspr or call IT on ext. 100.\n2. Verify identity via phone or backup email.\n3. Set a new password meeting policy requirements (8+ chars, uppercase, number, symbol).\n4. Log in and update saved passwords in browser.'),
    ('Printer Offline Troubleshooting', 'printer', 'printer, hp, offline',
     '1. Check printer is powered on and connected to the network.\n2. On Windows: go to Devices & Printers → right-click → See what\'s printing → Printer → Uncheck "Use Printer Offline".\n3. Restart the Print Spooler service.\n4. Reinstall printer driver if needed.'),
    ('New Staff Onboarding Checklist', 'onboarding', 'onboarding, new-hire, setup',
     'Day 1 Setup:\n- Create AD account and email\n- Assign laptop from IT store\n- Install required software (Office, Teams, VPN client)\n- Add to relevant distribution lists\n- Create Jira and GitHub accounts\n- Brief security orientation'),
]

for title, cat, tags, content in articles:
    Article.objects.create(
        title=title, category=cat, tags=tags, content=content,
        created_by=pick_staff('senior'),
        source_ticket=tickets[0] if cat == 'network' else None,
    )

print(f"✅ Created {len(articles)} knowledge articles")
print("\n🎉 Seed complete! Login credentials:")
for username, password, first, last, role in users_data:
    print(f"   {role:<12} → username: {username:<15} password: {password}")
