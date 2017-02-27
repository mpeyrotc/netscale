from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from mainApp.forms import *


# Create your views here.
@login_required
def home(request):
    context = {}
    return render(request, 'home.html', context)


def registration(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'registration.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'registration.html', context)

    # If we get here the form data was valid.  Register and login the user.
    form.save()

    # Logs in the new user and redirects to home
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password_1'])

    login(request, new_user)

    return redirect(reverse('home'))
