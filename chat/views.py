from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'chat/main.html')


def room(request, room, name):
    return render(request, 'chat/room.html', {'roomName': room, 'userName': name})
