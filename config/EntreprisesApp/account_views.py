from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, TemplateView

from .account_forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile

User = get_user_model()


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Compte créé avec succès. Bienvenue sur TransConnect !')
        return redirect('profile')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_profile(self.request.user)
        return context


class ProfileEditView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_edit.html'

    def get(self, request):
        return self._render(request,
                            UserUpdateForm(instance=request.user),
                            ProfileUpdateForm(instance=get_profile(request.user)))

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=get_profile(request.user))
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profil mis à jour.')
            return redirect('profile')
        return self._render(request, user_form, profile_form)

    def _render(self, request, user_form, profile_form):
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'accounts/profile_confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = self.object
        logout(self.request)
        user.delete()
        messages.success(self.request, 'Votre compte a été supprimé.')
        return redirect(self.success_url)


class AppPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class AppPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class AppPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class AppPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'