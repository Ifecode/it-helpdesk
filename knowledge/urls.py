from django.urls import path
from . import views

urlpatterns = [
    path('knowledge/', views.article_list, name='article_list'),
    path('knowledge/<int:pk>/', views.article_detail, name='article_detail'),
    path('knowledge/create/', views.create_article, name='create_article'),
    path('knowledge/create/<int:ticket_id>/', views.create_article, name='create_article_from_ticket'),
]
