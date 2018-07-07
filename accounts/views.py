from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_email
from django.shortcuts import redirect
from django.shortcuts import render

from answers.models import Answer
from questions.models import Question
from .forms import *


def register_view(request):
    if request.user.is_authenticated:
        return redirect('questions:questions')

    next = request.GET.get('next')
    form = SignUpForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            temp_user = User.objects.filter(username=username)
            if len(temp_user) != 0:
                messages.error(request, f"Username: {username}, already in use")
                return redirect('signup')
            if len(password) < 8:
                messages.error(request, f"Enter a password with more that 8 characters")
                return redirect('signup')

            user = User.objects.create_user(**form.cleaned_data)
            user.save()

            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)

                perms_codename_list = [
                    'add_question', 'change_question', 'delete_question',
                    'add_answer', 'change_answer', 'delete_answer',
                ]

                perms_list = list()

                for codename in perms_codename_list:
                    content_type = ContentType.objects.get_for_model(Question)
                    if codename.endswith('answer'):
                        content_type = ContentType.objects.get_for_model(Answer)
                    perms_list.append(Permission.objects.get(codename=codename, content_type=content_type))

                user.user_permissions.set(perms_list)

                if next:
                    return redirect(next)
                return redirect('questions:questions')
            else:
                messages.error(request, "Please enter all credentials")
                return redirect('signup')

    return render(
        request,
        template_name='auth_form.html',
        content_type='text/html',
        context={
            'form': SignUpForm(),
            'title': 'Sign Up',
            'type': 'Sign Up',
            'other': 'Login',
            'url': '/login/'
        }
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect('questions:questions')

    next = request.GET.get('next')
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                if next:
                    return redirect(next)
                return redirect('questions:questions')
            else:
                messages.error(request, "Please enter valid credentials")
                return redirect('login')
        else:
            messages.error(request, "Please enter valid credentials")
            return redirect('login')
    return render(
        request,
        template_name='auth_form.html',
        content_type='text/html',
        context={
            'form': LoginForm(),
            'title': 'Login',
            'type': 'Login',
            'other': 'Sign Up',
            'url': '/signup/'
        }
    )


def logout_user(request):
    logout(request)
    return redirect('login')


def get_user_view(request, id):
    form = ProfileForm(request.POST or None, instance=User.objects.filter(id=id).first())

    if request.method == "POST":
        if form.is_valid():

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            temp_user = User.objects.filter(username=username)
            if len(temp_user) != 0 and request.user != temp_user.first():
                messages.error(request, f"Username: {username} already in use")
                return redirect(request.path)

            temp_user = User.objects.filter(email=email)
            if len(temp_user) != 0 and request.user != temp_user.first():
                messages.error(request, f"Email: {email} already in use")
                return redirect(request.path)

            import re

            if email and not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                messages.error(request, f"Email: {email}, in not valid")
                return redirect(request.path)

            temp_user = User.objects.filter(id=id).first()
            temp_user.first_name = form.cleaned_data['first_name']
            temp_user.last_name = form.cleaned_data['last_name']
            temp_user.email = form.cleaned_data['email']
            temp_user.username = form.cleaned_data['username']
            temp_user.save()

            return redirect('questions:questions')

    return render(
        request,
        template_name='user_profile.html',
        content_type='text/html',
        context={
            'form': form,
            'title': request.user.username + ' | Edit',
            'type': 'Update Profile',
        }
    )


class PasswordChangeForm1(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = None


def change_password(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm1(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm1(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })
