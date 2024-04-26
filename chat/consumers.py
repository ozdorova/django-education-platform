import json
from channels.generic.websocket import WebsocketConsumer

# аналог views.py


class ChatConsumer(WebsocketConsumer):
    """Потребитель, принимающий wesocket соединения для чата"""

    def connect(self):
        """Принять соединение"""
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        """Получить сообщение из websocket"""
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # отправить сообщение в websocket
        self.send(text_data=json.dumps({'message': message}))
