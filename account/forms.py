from django import forms
from django.contrib.auth import get_user_model
from .models import Profile
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate
from datetime import date


User = get_user_model()


class UserCreateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput()
    )

    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput()
    )

    confirm_password = forms.CharField(
        label='パスワード（確認用）',
        widget=forms.PasswordInput()
    )


    def __init__(self, *args, **kwargs):
        for field in self.base_fields.values():
            field.widget.attrs["class"] = "form-control"
        super().__init__(*args, **kwargs)


    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            existing_user = User.objects.get(email=email)
            if existing_user.is_active:
                raise forms.ValidationError('このメールアドレスは既に使用されています')
        return email


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data["password"]
        confirm_password = cleaned_data["confirm_password"]
        if password != confirm_password:
            raise ValidationError('パスワードが一致しません')


    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user


    class Meta:
        model = User
        fields = ('email', 'password',)


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label='メールアドレス',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        required=True,
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )


class UserEmailForm(forms.Form):
    new_email = forms.EmailField(
        required=True,
        label='新しいメールアドレス',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        required=True,
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            existing_user = User.objects.get(email=email)
            if existing_user.is_active:
                raise forms.ValidationError('このメールアドレスは既に使用されています')
        return email


    def clean_password(self):
        password = self.cleaned_data['password']
        if not authenticate(
            email=self.user.email,
            password=password
            ):
            raise forms.ValidationError('パスワードが正しくありません')

        return password


class UserPasswordForm(forms.Form):
    current_password = forms.CharField(
        required=True,
        label='現在のパスワード',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )
    new_password = forms.CharField(
        required=True,
        label='新しいパスワード',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )
    confirm_password = forms.CharField(
        required=True,
        label='新しいパスワード（確認用）',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


    def clean_current_password(self):
        current_password = self.cleaned_data['current_password']
        if not authenticate(
            email=self.user.email,
            password=current_password,
            ):
            raise forms.ValidationError('パスワードが正しくありません')

        return current_password


    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data["new_password"]
        confirm_password = cleaned_data["confirm_password"]
        if new_password != confirm_password:
            raise ValidationError('パスワードが一致しません')


class ProfileForm(forms.ModelForm):
    introduction = forms.CharField(
        label='自己PR',
        required=False,
        widget=forms.Textarea()
    )

    birth = forms.DateField(
        label='生年月日',
        widget=forms.NumberInput(attrs={
            'type': 'date',
        })
    )

    image = forms.ImageField(
        required=False,
        label='イメージ画像',
        widget=forms.FileInput,
        )

    def __init__(self, *args, **kwargs):
        for field in self.base_fields.values():
            field.widget.attrs["class"] = "form-control"
        super().__init__(*args, **kwargs)

    def clean_birth(self):
        birth = self.cleaned_data["birth"]
        today = date.today()
        if birth >= today:
            raise forms.ValidationError('正しい日付を入力してください')

        return birth

    class Meta:
        model = Profile
        exclude = ('user',)
