from django.db import models
from django.contrib.auth.models import  User,AnonymousUser
from django.db.models import SET

# Create your models here.

class Message(models.Model):
    sender = models.ForeignKey(User,related_name='message_sender',
            on_delete=SET(AnonymousUser.id))
    recipient = models.ForeignKey(User,related_name='message_recipient',
            on_delete=SET(AnonymousUser.id))
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Community(models.Model):
    sender = models.ForeignKey(User, related_name='community_sender',
            on_delete=SET(AnonymousUser.id))
    recipient = models.ForeignKey(User,related_name='community_recipient',
            on_delete=SET(AnonymousUser.id))
    room_name = models.CharField(max_length=200,unique=True)

    def __str__(self):
        return self.community_name
