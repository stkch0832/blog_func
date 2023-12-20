from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('new', views.post_create, name='new'),
    path('detail/<int:pk>/', views.post_detail, name='detail'),
    path('detail/<int:pk>/edit', views.post_edit, name='edit'),
    path('detail/<int:pk>/delete', views.post_delete, name='delete'),
]
