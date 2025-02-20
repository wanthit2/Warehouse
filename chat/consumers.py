import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
import base64
from .models import ChatSession, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["session_id"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        data = json.loads(text_data)
        message_text = data.get("message", "")
        image_data = data.get("image", None)
        session_id = data.get("sessionid")

        chat_session = await self.get_chat_session(session_id)
        sender = await self.get_user(user.id)

        if sender is None:
            return

        new_message = Message(session=chat_session, sender=sender, text=message_text)

        if image_data:
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]
            new_message.image.save(f"chat_{session_id}_{sender.id}.{ext}", ContentFile(base64.b64decode(imgstr)), save=False)

        await self.save_message(new_message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": new_message.text,
                "sender": sender.username,
                "image": new_message.image.url if new_message.image else None,
                "timestamp": str(new_message.timestamp)
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @staticmethod
    async def get_chat_session(session_id):
        return await ChatSession.objects.aget(id=session_id)

    @staticmethod
    async def get_user(user_id):
        return await User.objects.aget(id=user_id)

    @staticmethod
    async def save_message(message):
        await message.asave()
