import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from chat.models import Message
import logging

class ChatConsumer(WebsocketConsumer):
    logging.info("Entered Consumer")

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(self.room_group_name,
                self.channel_name)       
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name, self.channel_name
                )
    def save_message(self, message, sender, receiver):
        sender_user = User.objects.get(id = sender)
        receiver_user = User.objects.get(id=receiver)
        new_message = Message.objects.create(message=message,sender=sender_user,
                recipient=receiver_user)
        new_message.save()
    #receive message from websocket
    def receive(self, text_data):
        logging.info("Data Recived from socket")
        logging.info(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        #self.send(text_data=json.dumps({"message":message}))
        sender = text_data_json["sender"]
        receiver = text_data_json["receiver"]
        sender_name = text_data_json['sender_name']
        self.save_message(message,sender,receiver)
        #Send message to room group
        async_to_sync(self.channel_layer.group_send)(
        self.room_group_name, {"type": "chat.message",
                               "message": message,
                               "sender": sender,
                               "receiver": receiver,
                               "sender_name": sender_name}
        )
#Receive Message from group
    def chat_message(self,event):
        logging.info(event)
        message = event["message"]
        sender = event["sender"]
        receiver = event["receiver"]
        sender_name = event["sender_name"]
        #Send message to WebSocket
        self.send(text_data=json.dumps({"message":message,
            "sender": sender,
            "receiver": receiver,
            "sender_name": sender_name}))
