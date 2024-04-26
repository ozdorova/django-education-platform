import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

# аналог views.py


class ChatConsumer(AsyncWebsocketConsumer):
    """Потребитель, принимающий wesocket соединения для чата"""

    async def connect(self):
        """Соединение"""
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = 'chat_%s' % self.id

        # присоединиться к группе чат комнаты
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name)
        # принять соединение
        await self.accept()

    async def disconnect(self, close_code):
        """Отключение от чата"""
        # покинуть группу чат комнаты
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_layer)

    async def receive(self, text_data):
        """Получить сообщение из websocket"""
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        now = timezone.now()
        # отправить сообщение в группу чат комнаты
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )

    async def chat_message(self, event):
        # отправить сообщение в веб сокет
        await self.send(text_data=json.dumps(event))
