from django.shortcuts import render, redirect, get_object_or_404
from . import forms
from .models import UserActivateToken
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from . import models

User = get_user_model()

def index(request):
    return render(request, 'account/index.html')


def user_signup(request):
    if request.method == 'POST':
        form = forms.UserCreateForm(request.POST or None)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'メールを送信しました。認証を完了してください。')
                redirect('account/activate_user.html')
            except ValidationError as e:
                form.add_error('email', e)
                form.add_error('password', e)
    else:
        form = forms.UserCreateForm()

    return render(request, 'account/user_form.html', context={
        'form': form,
    })


def activate_user(request, token):
    user_activate_token = UserActivateToken.objects.activate_user_by_token(
        token)
    messages.success(request, '認証が完了しました。')
    return redirect('account:login')


def user_login(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'ログインが完了しました')
                    return redirect('blog:index')
                else:
                    messages.error(request, 'ユーザー登録が完了していません')
            else:
                messages.error(request, 'ユーザーIDまたはパスワードが間違っています')
    else:
        form = forms.LoginForm()
    return render(request, 'account/user_form.html', context={
        'form': form,
    })


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'ログアウトしました')
    return redirect('account:login')


@login_required
def user_email(request):
    user_data = get_object_or_404(User, pk=request.user.pk)

    if request.method == 'POST':
        form = forms.UserEmailForm(request.user, request.POST or None)

        if form.is_valid():
            try:
                user_data.email = form.cleaned_data['new_email']
                user_data.save()
                messages.success(request, 'メールアドレスを変更しました')
                return redirect('account:email')
            except forms.ValidationError as e:
                form.add_error('new_email', e)
                form.add_error('password', e)

    else:
        form = forms.UserEmailForm(request.user)

    return render(request, 'account/email_form.html', context={
        'user_data': user_data,
        'form': form,
    })


@login_required
def user_password(request):
    user_data = get_object_or_404(User, pk=request.user.pk)

    if request.method == 'POST':
        form = forms.UserPasswordForm(request.user, request.POST or None)

        if form.is_valid():
            try:
                user_data.set_password(form.cleaned_data['new_password'])
                user_data.save()
                messages.success(request, 'パスワードを変更しました')

                user = authenticate(
                    email=user_data.email,
                    password=form.cleaned_data['new_password']
                )
                login(request, user)

                return redirect('account:password')
            except forms.ValidationError as e:
                form.add_error('current_password', e)
                form.add_error('new_password', e)

    else:
        form = forms.UserPasswordForm(request.user)

    return render(request, 'account/password_form.html', context={
        'form': form,
        })


@login_required
def user_profile(request):
    profile_data = get_object_or_404(models.Profile, user_id=request.user.pk)

    if request.method == 'POST':
        form = forms.ProfileForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            try:
                profile_data.username = form.cleaned_data['username']
                profile_data.introduction = form.cleaned_data['introduction']
                profile_data.birth = form.cleaned_data['birth']
                if form.cleaned_data['image']:
                    profile_data.image = form.cleaned_data['image']
                profile_data.save()
                messages.success(request, 'プロフィールを更新しました')
                return redirect('account:profile')

            except forms.ValidationError as e:
                form.add_error('birth', e)

    else:
        form = forms.ProfileForm(instance=profile_data)

    return render(request, 'account/profile_form.html', context={
        'profile_data': profile_data,
        'form': form,
    })


@login_required
def user_withdrawal(request):
    user_data = get_object_or_404(User, pk=request.user.pk)

    if request.method == 'POST':
        user_data.email = user_data.email + "_dummy"
        user_data.is_active = False
        user_data.save()
        logout(request)
        messages.success(request, '退会が完了しました')
        return redirect('account:login')
    else:
        return render(request, 'account/withdrawal.html')
