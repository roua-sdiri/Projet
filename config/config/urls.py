"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.views.generic import TemplateView

from EntreprisesApp import account_views as acc   # ← new

urlpatterns = [
    path('', TemplateView.as_view(template_name='shared/home.html'), name='home'),
    path('login/', LoginView.as_view(template_name='entreprise/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),

    # ← new: accounts
    path('accounts/register/', acc.RegisterView.as_view(), name='register'),
    path('accounts/profile/', acc.ProfileView.as_view(), name='profile'),
    path('accounts/profile/edit/', acc.ProfileEditView.as_view(), name='profile_edit'),
    path('accounts/profile/delete/', acc.ProfileDeleteView.as_view(), name='profile_delete'),
    path('accounts/password-reset/', acc.AppPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset/done/', acc.AppPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', acc.AppPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', acc.AppPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('entreprises/', include('EntreprisesApp.urls')),
    path('vehicules/', include('VehiculesApp.urls')),
    path('offres/', include('OffresApp.urls')),
    path('expeditions/', include('ExpeditionsApp.urls')),
]

