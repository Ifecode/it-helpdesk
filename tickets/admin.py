from django.contrib import admin
from .models import Ticket, TicketComment, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'specialization']
    list_filter = ['role']


class CommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ['created_at', 'author']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'priority', 'category', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'category', 'required_level']
    search_fields = ['title', 'description', 'user_email']
    inlines = [CommentInline]
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
