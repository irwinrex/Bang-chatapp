# chat/models.py

from django.db import models

class ChatRoom(models.Model):
    """Model representing a chat room."""
    room_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.room_name

# If using MongoDB solely, you might not need traditional Django models.
# In that case, you can choose to keep this file empty or use it for any future models you plan to integrate with Django's ORM.
