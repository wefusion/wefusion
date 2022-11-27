import neo4j
import pika
from neo4j import Session as Neo4jSession
from pika import BlockingConnection
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SQLASession

from stable_diffusion.settings import settings


class ConnectionStore:
    _rabbitmq_conn: BlockingConnection
    _sqla_engine: Engine

    def __init__(self):
        pika_conn_params = pika.URLParameters(settings.RABBITMQ_DSN)
        pika_conn_params._retry_delay = 5
        pika_conn_params._heartbeat = 120

        self._rabbitmq_conn = pika.BlockingConnection(pika_conn_params)
        self._sqla_engine = create_engine(settings.POSTGRES_DSN)
        self._neo4j_driver = neo4j.GraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def get_channel(self):
        return self._rabbitmq_conn.channel()

    def get_sqla_session(self) -> SQLASession:
        return SQLASession(bind=self._sqla_engine)

    def get_neo4j_session(self) -> Neo4jSession:
        return self._neo4j_driver.session()


connection_store = ConnectionStore()
