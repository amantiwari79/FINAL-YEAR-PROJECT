from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label=_('First Name'))
    last_name = forms.CharField(max_length=150, required=True, label=_('Last Name'))
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label=_('Password'))
    password_confirm = forms.CharField(widget=forms.PasswordInput(), required=True, label=_('Confirm Password'))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with that email already exists.'))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(_("Passwords do not match."))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
