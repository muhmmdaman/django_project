from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
            }
        )
    )
    def clean(self):
        cleaned_data = super().clean()
        user = self.user_cache
        if user is not None:
            from messaging.models import UserRestriction
            from django.utils import timezone
            active_ban = user.restrictions.filter(
                restriction_type="banned", is_active=True
            ).first()
            if active_ban:
                if active_ban.expires_at and timezone.now() > active_ban.expires_at:
                    active_ban.is_active = False
                    active_ban.save(update_fields=["is_active"])
                else:
                    raise ValidationError(
                        f"Your account has been banned. Reason: {active_ban.reason}",
                        code="banned_user",
                    )
        return cleaned_data
