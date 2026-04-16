from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    CATEGORY_CHOICES = [
        ('network', 'Network'),
        ('access', 'Access / Permissions'),
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('email', 'Email'),
        ('password', 'Password Reset'),
        ('printer', 'Printer'),
        ('onboarding', 'Onboarding'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source_ticket = models.ForeignKey(
        'tickets.Ticket', on_delete=models.SET_NULL, null=True, blank=True, related_name='articles'
    )

    def __str__(self):
        return self.title

    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    class Meta:
        ordering = ['-created_at']
