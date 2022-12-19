import pika
import requests
from pika import BlockingConnection

from stable_diffusion.settings import settings


class ConnectionStore:
    _rabbitmq_conn: BlockingConnection

    def __init__(self):
        pika_conn_params = pika.URLParameters(settings.RABBITMQ_DSN)
        pika_conn_params._retry_delay = 5
        pika_conn_params._heartbeat = 120

        self._rabbitmq_conn = pika.BlockingConnection(pika_conn_params)

    def get_channel(self):
        return self._rabbitmq_conn.channel()

    def get_session(self):
        api_session = requests.Session()
        api_session.headers.update({"Authorization": "Bearer " + settings.SERVICE_KEY})

        return api_session


connection_store = ConnectionStore()
