from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Article
from tickets.models import Ticket


@login_required
def article_list(request):
    articles = Article.objects.all()
    q = request.GET.get('q')
    category = request.GET.get('category')
    if q:
        articles = articles.filter(title__icontains=q) | articles.filter(content__icontains=q) | articles.filter(tags__icontains=q)
    if category:
        articles = articles.filter(category=category)
    return render(request, 'knowledge/article_list.html', {
        'articles': articles,
        'category_choices': Article.CATEGORY_CHOICES,
        'q': q,
        'selected_category': category,
    })


@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'knowledge/article_detail.html', {'article': article})


@login_required
def create_article(request, ticket_id=None):
    ticket = None
    if ticket_id:
        ticket = get_object_or_404(Ticket, pk=ticket_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category = request.POST.get('category', 'other')
        tags = request.POST.get('tags', '').strip()
        source_id = request.POST.get('source_ticket')

        if title and content:
            article = Article.objects.create(
                title=title,
                content=content,
                category=category,
                tags=tags,
                created_by=request.user,
                source_ticket_id=source_id if source_id else None,
            )
            messages.success(request, f'Article "{article.title}" saved to knowledge base.')
            return redirect('article_detail', pk=article.pk)

    return render(request, 'knowledge/create_article.html', {
        'ticket': ticket,
        'category_choices': Article.CATEGORY_CHOICES,
    })
