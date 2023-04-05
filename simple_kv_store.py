import logging
import threading

from raft.message_interface import recv_message, send_message
from raft.persisted_dict import PersistedDictionary
from raft.protocol import decode_response, encode_request
from socket import *


logger = logging.getLogger(__name__)


class KVServer:
    def __init__(self, host, port):
        self.data = PersistedDictionary('foo.dct')
        self.host = host
        self.port = port
        self.data_lock = threading.Lock()

    def start(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
        sock.bind((self.host, self.port))
        sock.listen(1)
        logger.info(f'Server running at {self.host}:{self.port}')
        while True:
            client, addr = sock.accept()
            logger.info(f'client connection received from {addr}')
            t = threading.Thread(target=self.handle_client, args=(client, ), daemon=True)
            t.start()

    def handle_client(self, client):
        while True:
            msg = recv_message(client)
            method, args = decode_response(msg)
            with self.data_lock:
                resp = getattr(self, method.lower())(*args)
                send_message(client, encode_request(resp))

    def set(self, key, value):
        self.data[key] = value
        return 'OK'

    def get(self, key):
        try:
            value = self.data[key]
            return 'RETURN', value
        except KeyError:
            return 'UNKNOWN'

    def delete(self, key):
        try:
            self.data.pop(key)
            return 'OK'
        except KeyError:
            return 'UNKNOWN'
