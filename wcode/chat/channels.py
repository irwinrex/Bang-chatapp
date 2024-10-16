# channels.py

import os, environ
from pulsar import Client as PulsarClient
from channels.layers import BaseChannelLayer
from asgiref.sync import sync_to_async

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Pulsar settings
PULSAR_SERVICE_URL = env('PULSAR_SERVICE_URL')
PULSAR_ADMIN_URL = env('PULSAR_ADMIN_URL')

class PulsarChannelLayer(BaseChannelLayer):
    def __init__(self):
        self.client = PulsarClient(env['PULSAR_SERVICE_URL'])
        self.producer = self.client.create_producer('django-channel-topic')
    
    async def send(self, channel, message):
        # Convert the message to a string format, if necessary
        await sync_to_async(self.producer.send)(message.encode('utf-8'))

    async def receive(self, channel):
        # Implement a method to receive messages from a Pulsar topic
        # This will require additional implementation based on your needs
        pass

    async def close(self):
        # Close the Pulsar client connection
        await sync_to_async(self.client.close)()
