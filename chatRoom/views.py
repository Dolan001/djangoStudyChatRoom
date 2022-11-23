from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from .models import Message, Room, Topic
from .forms import RoomForm, UserForm


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')
  
    context = {'page':page}
    return render(request, 'login_reg.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured dering registration')

    context = {'form':form}
    return render(request, 'login_reg.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains = q)
    )
    topics = Topic.objects.all()
    topic_limit = topics[0:5]
    room_count = rooms.count()

    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count':room_count,
        'room_messages':room_messages,
        'topic_limit': topic_limit
        }
    return render(request,'home.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()[0:5]
    context = {
        'user':user,
        'rooms':rooms,
        'room_messages':room_messages,
        'topics':topics
    }
    return render(request,'profile.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room=room,
            body = request.POST.get('body')
        )
        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages':room_messages,
        'participants':participants
    }
    if request.user.is_authenticated:
        room.participants.add(request.user)
        return render(request, 'room.html', context)
    else:
        return redirect('home')

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
    
        return redirect('home')
    context = {
        'form':form,
        'topics':topics
    }
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed for this action")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST, instance=room)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {
        'form': form,
        'topics':topics,
        'room':room
        }
    return render(request,'room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed for this action")
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj':room}
    return render(request,'delete.html', context) 


@login_required(login_url='login')
def deleteMessage(request, pk):
    msg = Message.objects.get(id=pk)
    if request.user != msg.user:
        return HttpResponse("You are not allowed for this action")
    if request.method == 'POST':
        msg.delete()
        return redirect('home')
    context = {'obj':msg}
    return render(request,'delete.html', context)       


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {
        'form':form
    }
    return render(request,'update_user.html', context)


def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q') !=None else ""
    topics = Topic.objects.filter(name__icontains = q)
    return render(request, 'topics.html', {'topics':topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'activity.html', {'room_messages':room_messages})
