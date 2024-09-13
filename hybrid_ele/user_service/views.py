from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import StudentRegistrationForm, TutorRegistrationForm, CustomPasswordResetForm
from .models import User

class StudentRegistrationView(CreateView):
    model = User
    form_class = StudentRegistrationForm
    template_name = 'user_service/student_register.html'
    success_url = reverse_lazy('student_dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

class TutorRegistrationView(CreateView):
    model = User
    form_class = TutorRegistrationForm
    template_name = 'user_service/tutor_register.html'
    success_url = reverse_lazy('tutor_dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

class CustomLoginView(LoginView):
    template_name = 'user_service/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_student:
            return reverse_lazy('student_dashboard')
        elif user.is_tutor:
            return reverse_lazy('tutor_dashboard')
        else:
            return reverse_lazy('home')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'user_service/password_reset.html'
    email_template_name = 'user_service/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = CustomPasswordResetForm

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'user_service/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')