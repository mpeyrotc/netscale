from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import simplejson as json
import re
from django.db import transaction
import time
import datetime
import operator

from django.contrib.auth.models import User
from friendship.models import Friend, Follow, FriendshipRequest
from s3 import s3_upload, s3_delete

# Used to create and manually log in a user
from django.contrib.auth import login, authenticate

from mainApp.forms import *
from mainApp.models import *


def get_user(request):
    return User.objects.filter(id__exact=request.user.id)[0]


def get_profile(request):
    return UserProfile.objects.filter(user__exact=get_user(request))[0]


@login_required
def home(request):
    profile = get_profile(request)
    context = {"profile": profile}
    now = datetime.datetime.now()
    search_results = []

    print profile.gmail_account

    if request.method == 'POST':
        search_token = request.POST['search_value']

        if profile.friends:
            friends = Friend.objects.friends(request.user)

            for friend in friends:
                value = 0
                friend_profile = UserProfile.objects.filter(user__exact=
                                                             User.objects.filter(id__exact=friend.id)[0])[0]

                for thread in friend_profile.threads.all():
                    if thread.contacts:
                        contacts = thread.contacts.split(",")

                        for contact in contacts:
                            if search_token in contact:
                                p = re.compile("[0-9]+ [a-zA-Z]{3} ([0-9]+)")
                                m = p.search(thread.date)
                                temp = thread.size * 3

                                if m:
                                    year = int(m.group(1))

                                    if((now.year - year) <= 3):
                                        value += temp
                                    elif((now.year - year) <= 5):
                                        value += temp * 0.87
                                    elif ((now.year - year) <= 10):
                                        value += temp * 0.6
                                    else:
                                        value += temp * 0.2

                search_results.append((friend_profile, value))
        else:
            context["result"] = ""

        value = 20
        for thread in profile.threads.all():
            if thread.contacts:
                contacts = thread.contacts.split(",")

                for contact in contacts:
                    if search_token in contact:
                        p = re.compile("[0-9]+ [a-zA-Z]{3} ([0-9]+)")
                        m = p.search(thread.date)
                        temp = thread.size * 3

                        if m:
                            year = int(m.group(1))

                            if ((now.year - year) <= 3):
                                value += temp
                            elif ((now.year - year) <= 5):
                                value += temp * 0.87
                            elif ((now.year - year) <= 10):
                                value += temp * 0.6
                            else:
                                value += temp * 0.2

        search_results.append((profile, value))
        search_results.sort(key=lambda tup: tup[1])
        search_results.reverse()

        if len(search_results) > 5:
            search_results = search_results[0:4]

        context["result"] = search_results
    else:
        context["result"] = ""

    context['user_profiles'] = UserProfile.objects.all()
    current_user = User.objects.filter(id__exact=request.user.id)[0]
    context['user_profile'] = UserProfile.objects.filter(user__exact=current_user)[0]
    context['user_id'] = request.user.id

    # friendships
    friend_requests = Friend.objects.unrejected_requests(user=request.user)
    p = re.compile('User #([0-9]+) friendship requested #([0-9]+)')

    context['requests'] = []

    for f_request in friend_requests:
        req_profile = UserProfile.objects.filter(user__exact=f_request.from_user)[0]
        context['requests'].append({'profile': req_profile,
                                    'request': f_request.id})

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


def add_email(request):
    if request.method == 'POST':
        profile = get_profile(request)
        profile.gmail_account = json.dumps(request.POST['email_address'])
        profile.save()

    return HttpResponse([], content_type='application/json')

@transaction.atomic
def add_contacts(request):
    if request.method == 'POST':
        result = json.loads(request.POST['contacts'])

        profile = get_profile(request)

        # if profile.contacts:
        #     profile.contacts = profile.contacts + contact + ","
        # else:
        #     profile.contacts = contact + ","

        if not profile.threads.filter(thread_id=result["t_id"]).exists() and int(result['thread_size']) > 1:
            date = result['date']

            contact = Thread(size=result['thread_size'], contacts=result['contacts'], date=date,
                             thread_id=result['t_id'])
            contact.save()
            profile.threads.add(contact)
            profile.save()

        if int(result['thread_size']) > 2:
            print "worked " + str(int(result['thread_size']))
        else:
            print "not worked " + str(result['thread_size'])

    return HttpResponse([], content_type='application/json')


@login_required
def profiles(request, id):
    context = {}

    if User.objects.filter(id__exact=id):
        current_user = User.objects.filter(id__exact=request.user.id)[0]
        context['user_profile'] = UserProfile.objects.filter(user__exact=current_user)[0]
        profile = UserProfile.get_user_profile_with_id(id)
        context['profile'] = profile
        context['id'] = id
        context['user_id'] = request.user.id
        context['is_followed'] = UserProfile.objects.filter(user__exact=current_user)[0].friends.filter(
            id=UserProfile.objects.filter(user__exact=User.objects.filter(id__exact=id))[0].id)

        # Get user's profile form
        try:
            if request.method == 'GET':
                form = ""
                context['form'] = form

                context['is_friend'] = False
                friends = Friend.objects.friends(request.user)

                for friend in friends:
                    if friend == User.objects.filter(id__exact=id)[0]:
                        context['is_friend'] = True

                requests = Friend.objects.requests(User.objects.filter(id__exact=id)[0])
                for frequest in requests:
                    if frequest.from_user == request.user:
                        context['is_friend'] = True

            return render(request, 'profile.html', context)

            user = User.objects.filter(id__exact=id)[0]
            profile = UserProfile.objects.select_for_update().get(user__exact=user)
            db_update_time = profile.update_time  # Copy timestamp to check after form is bound
            form = ""
            if not form.is_valid():
                context['profile'] = profile
                context['form'] = form
                return render(request, 'profile.html', context)

            # if update times do not match, someone else updated DB record while were editing
            if db_update_time != form.cleaned_data['update_time']:
                # refetch from DB and try again.
                profile = UserProfile.objects.get(user=User.objects.filter(id__exact=id)[0])
                form = ""
                context['message'] = 'Another user has modified this record.  Re-enter your changes.'
                context['form'] = form
                context['profile'] = profile

                return render(request, 'profile.html', context)

            # Set update info to current time and user, and save it!
            profile.update_time = ""
            form.save()

            # form = EditForm(instance=entry)
            context['message'] = 'Entry updated.'
            context['entry'] = profile
            context['form'] = form

            return render(request, 'profile.html', context)

        except UserProfile.DoesNotExist:
            context = {'message': 'Record with id={0} does not exist'.format(id)}
            return render(request, 'profile.html', context)

    else:
        return home(request)


@login_required
def send_request(request, other_id, user_id):
    # will break if not existent!
    other_user = User.objects.filter(id__exact=other_id)[0]
    user = User.objects.filter(id__exact=user_id)[0]

    Friend.objects.add_friend(
        user,  # The sender
        other_user,  # The recipient
        message='Hi! I would like to add you')  # This message is optional

    return redirect(reverse('home'))


@login_required
def accept_request(request, req_id):
    # will break if not existent!
    friend_request = FriendshipRequest.objects.get(pk=req_id)
    friend_request.accept()

    return redirect(reverse('home'))


@login_required
def reject_request(request, req_id):
    # will break if not existent!
    friend_request = FriendshipRequest.objects.get(pk=req_id)
    friend_request.reject()



    return redirect(reverse('home'))


@login_required
def network(request):
    context = {}
    result = {}
    profile = get_profile(request)

    if profile.friends:
        friends = Friend.objects.friends(request.user)

        for friend in friends:
            friend_profile = UserProfile.objects.filter(user__exact=
                                                        User.objects.filter(id__exact=friend.id)[0])[0]

            print friends
            for thread in friend_profile.threads.all():
                if thread.contacts:
                    contacts = thread.contacts.split(",")

                    for contact in contacts:
                        if contact in result:
                            result[contact] += 1
                        else:
                            result[contact] = 1

    for thread in profile.threads.all():
        if thread.contacts:
            contacts = thread.contacts.split(",")

            for contact in contacts:
                if contact in result:
                    result[contact] += 1
                else:
                    result[contact] = 1

    sorted_result = sorted(result.items(), key=operator.itemgetter(1))
    context['result'] = reversed(sorted_result)

    return render(request, 'network.html', context)


@login_required
@transaction.atomic
def edit_profile(request):
    context = {}
    profile = get_profile(request)

    # Get user's profile form
    try:
        if request.method == 'GET':
            form = ProfileForm(instance=profile)
            context['form'] = form

            context['contacts'] = profile.contacts

            return render(request, 'edit-profile.html', context)

        db_update_time = profile.update_time  # Copy timestamp to check after form is bound
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if not form.is_valid():
            context['profile'] = profile
            context['form'] = form
            return render(request, 'edit-profile.html', context)

        # if update times do not match, someone else updated DB record while were editing
        if db_update_time != form.cleaned_data['update_time']:
            # refetch from DB and try again.
            profile = UserProfile.objects.get(user=User.objects.filter(id__exact=id)[0])
            form = ProfileForm(instance=profile)
            context['message'] = 'Another user has modified this record.  Re-enter your changes.'
            context['form'] = form
            context['profile'] = profile

            return render(request, 'edit-profile.html', context)

        # Set update info to current time and user, and save it!
        profile.update_time = datetime.datetime.now()

        if form.cleaned_data['picture']:
            url = s3_upload(form.cleaned_data['picture'], profile.id)
            form.picture = url

        form.save()

        # form = EditForm(instance=entry)
        context['message'] = 'Entry updated.'
        context['entry'] = profile
        context['form'] = form

        return render(request, 'profile.html', context)

    except UserProfile.DoesNotExist:
        return redirect(reverse('home'))

    return render(request, 'edit-profile.html', context)


@login_required
def get_picture(request, id):
    if User.objects.filter(id__exact=id):
        profile = UserProfile.objects.filter(user__exact=User.objects.filter(id__exact=id))[0]
        if not profile.picture:
            raise Http404

        content_type = guess_type(profile.picture.name)
        return HttpResponse(profile.picture, content_type=content_type)
    else:
        return redirect(reverse('home'))
