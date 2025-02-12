import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatSession, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.room_name}'

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
        message_text = data.get('message')
        session_id = self.room_name

        chat_session = await self.get_chat_session(session_id)
        sender = await self.get_user(user.id)

        if not chat_session or not sender:
            return

        # ✅ บันทึกข้อความลงฐานข้อมูล
        new_message = await self.save_message(chat_session, sender, message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_message.text,
                'sender': sender.username,
                'timestamp': str(new_message.timestamp)
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    @staticmethod
    async def get_chat_session(session_id):
        try:
            return await ChatSession.objects.aget(id=session_id)
        except ChatSession.DoesNotExist:
            return None

    @staticmethod
    async def get_user(user_id):
        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    async def save_message(chat_session, sender, text):
        return await Message.objects.acreate(session=chat_session, sender=sender, text=text)
