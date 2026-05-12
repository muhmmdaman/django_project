from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import LoginForm
class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy("core:dashboard")
class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("accounts:login")
