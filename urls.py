from django.urls import path

from . import views

urlpatterns = [
        path("community/",views.GetAllUsers.as_view(),name="community"),
        path("rooms/<str:room_name>/",views.ChatRoom.as_view(),name="room"),
        ]
