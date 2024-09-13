from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('student/register/', views.StudentRegistrationView.as_view(), name='student_register'),
    path('tutor/register/', views.TutorRegistrationView.as_view(), name='tutor_register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='user_service/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='user_service/password_reset_complete.html'), name='password_reset_complete'),
]