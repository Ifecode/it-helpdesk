from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.contrib import messages
from .models import Ticket, TicketComment, Profile
from .classifier import classify
from .assignment import auto_assign
from knowledge.models import Article


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    is_manager = hasattr(user, 'profile') and user.profile.role == 'manager'

    my_tickets = Ticket.objects.filter(assigned_to=user).exclude(status__in=['resolved', 'closed'])
    all_tickets = Ticket.objects.all()

    # Stats
    total = all_tickets.count()
    open_count = all_tickets.filter(status='open').count()
    in_progress = all_tickets.filter(status='in_progress').count()
    resolved = all_tickets.filter(status='resolved').count()

    # SLA breached (open tickets past deadline)
    now = timezone.now()
    sla_breached = []
    for t in all_tickets.filter(status__in=['open', 'in_progress']):
        if t.is_sla_breached:
            sla_breached.append(t.id)

    # Staff workload (manager view)
    staff_workload = []
    if is_manager:
        staff = User.objects.filter(is_staff=True).annotate(
            open_count=Count('assigned_tickets', filter=Q(assigned_tickets__status__in=['open', 'in_progress']))
        )
        staff_workload = list(staff)

    # Category breakdown
    category_counts = all_tickets.values('category').annotate(count=Count('id')).order_by('-count')

    # Avg resolution time (hours)
    resolved_tickets = all_tickets.filter(resolved_at__isnull=False)
    avg_resolution = None
    if resolved_tickets.exists():
        times = [t.resolution_time_hours for t in resolved_tickets if t.resolution_time_hours]
        avg_resolution = round(sum(times) / len(times), 1) if times else None

    context = {
        'my_tickets': my_tickets,
        'all_tickets': all_tickets[:20],
        'is_manager': is_manager,
        'stats': {
            'total': total,
            'open': open_count,
            'in_progress': in_progress,
            'resolved': resolved,
            'sla_breached': len(sla_breached),
        },
        'staff_workload': staff_workload,
        'category_counts': category_counts,
        'avg_resolution': avg_resolution,
        'sla_breached_ids': sla_breached,
    }
    return render(request, 'dashboard.html', context)


@login_required
def ticket_list(request):
    tickets = Ticket.objects.all()

    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    category_filter = request.GET.get('category')
    assigned_filter = request.GET.get('mine')

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    if assigned_filter == '1':
        tickets = tickets.filter(assigned_to=request.user)

    return render(request, 'ticket_list.html', {
        'tickets': tickets,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
        'category_choices': Ticket.CATEGORY_CHOICES,
        'filters': {'status': status_filter, 'priority': priority_filter, 'category': category_filter, 'mine': assigned_filter},
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    comments = ticket.comments.all()
    related_articles = Article.objects.filter(category=ticket.category)[:3]

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'comment':
            body = request.POST.get('body', '').strip()
            if body:
                TicketComment.objects.create(ticket=ticket, author=request.user, body=body)

        elif action == 'update_status':
            new_status = request.POST.get('status')
            ticket.status = new_status
            if new_status == 'resolved' and not ticket.resolved_at:
                ticket.resolved_at = timezone.now()
            ticket.save()

        elif action == 'reassign':
            uid = request.POST.get('user_id')
            if uid:
                ticket.assigned_to_id = uid
                ticket.save()

        return redirect('ticket_detail', pk=pk)

    staff_users = User.objects.filter(is_staff=True)
    return render(request, 'ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'related_articles': related_articles,
        'staff_users': staff_users,
        'status_choices': Ticket.STATUS_CHOICES,
    })


@login_required
def create_ticket(request):
    """Manual ticket creation (for testing without email)."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        user_email = request.POST.get('user_email', '').strip()

        if title and description and user_email:
            result = classify(title, description)
            ticket = Ticket.objects.create(
                title=title,
                description=description,
                user_email=user_email,
                category=result['category'],
                priority=result['priority'],
                required_level=result['level'],
                sla_hours=result['sla_hours'],
            )
            assignee = auto_assign(ticket)
            if assignee:
                ticket.assigned_to = assignee
                ticket.save()
            messages.success(request, f'Ticket #{ticket.id} created and assigned.')
            return redirect('ticket_detail', pk=ticket.id)

    return render(request, 'create_ticket.html')
