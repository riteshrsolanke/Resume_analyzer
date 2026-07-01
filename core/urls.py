from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('resume/upload/', views.upload_resume, name='upload_resume'),
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    path('resume/<int:resume_id>/analyze/', views.analyze, name='analyze'),
    path('results/<int:analysis_id>/', views.results, name='results'),
]
