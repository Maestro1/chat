from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.views import View
from .forms import UserCreationForm, LoginForm
from chat.models import Community, Message
from django.contrib.auth import authenticate, login, logout
# Create your views here.
import logging
logger = logging.getLogger(__name__)

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request,'chat/register.html',{'form': form})
"""
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('community')
    else:
        form = LoginForm()
    return render(request,'chat/login.html',{'form':form})

def user_logout(request):
    logout(request)
    return redirect('login')
"""
class GetAllUsers(LoginRequiredMixin,View):
    def get(self, request):
        """ 
        Get list of all users from the database
        """
        users = User.objects.all().exclude(id = request.user.id)
        return render(request,'chat/index.html',{'users': users})

    def post(self,request):
        """ 
        To connect sender and receiver to their chat room
        """
        sender = request.user.id
        receiver = request.POST['users']

        sender_user = User.objects.get(id=sender)
        receiver_user = User.objects.get(id=receiver)
        #setting receiver as a session variable
        request.session['receiver_user'] = receiver

        #check if sender and receiver already have a room
        get_room = Community.objects.filter(Q(sender=sender_user,recipient=receiver_user)| Q(sender=receiver_user,recipient=sender_user))
        #Fetch room name if a room already  exists
        if get_room:
            room_name = get_room[0].room_name

        #Createv a new room if room doesn't exist
        else:
            logging.info("new Room")
            new_room = get_random_string(10)

            while True:
                room_exists = Community.objects.filter(room_name=new_room)
                if room_exists:
                    new_room = get_random_string(10)
                else:
                    break
            create_room = Community.objects.create(sender=sender_user,recipient=receiver_user,room_name=new_room)
            create_room.save()
            room_name = create_room.room_name
        return redirect('room',room_name=room_name)

class ChatRoom(LoginRequiredMixin,View):
    queryset = Community.objects.all()

    def get(self, request,room_name,*args,**kwargs):
        get_object_or_404(Community,room_name=self.kwargs.get("room_name"))
        room = Community.objects.get(room_name=self.kwargs.get("room_name"))
        sender = request.user.id
        sender_name = User.objects.get(id=sender).username

        #Sets up the user as sender user for chatting
        if room.recipient.id == sender:
            receiver = room.sender.id
        else:
            receiver = room.recipient.id

        #Get all previous messages from DB
        messages = Message.objects.filter(Q(sender=sender,recipient=receiver) | Q(sender=receiver,recipient=sender)).order_by('timestamp')

        return render(request,'chat/room.html',{
            'room_name':room_name,
            'sender_id':sender,
            'receiver_id':receiver,
            'messages':messages,
            'sender_name':sender_name
            })
