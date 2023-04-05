import sys
from contextlib import closing
from socket import *
import logging

logger = logging.getLogger(__name__)

HEADER_LENGTH = 8
HEADER_BYTEORDER = 'little'



class ClientDisconnectedError(Exception):
    pass


def _recv(sock, size) -> bytes:
    data = b''

    while len(data) < size:
        msg_part = sock.recv(min(5, size - len(data)))
        if not msg_part:
            raise ClientDisconnectedError()
        data += msg_part
        logger.info("received %s/%s bytes of data", len(data), size)
    return data


def recv_message(sock) -> str:
    # get the header
    header = _recv(sock, HEADER_LENGTH)
    msg_length = int.from_bytes(header, HEADER_BYTEORDER)
    # listen to the rest of the message
    message = _recv(sock, msg_length)
    return message.decode()


def send_message(sock, message: str):
    bytes_message = message.encode()
    msg_length = len(bytes_message)
    if msg_length >= 2 ** HEADER_LENGTH:
        raise ValueError(
            "msg is too long, can encode messages up to %s, got %s instead".format(
            2 ** HEADER_LENGTH,
            msg_length
        ))
    header = msg_length.to_bytes(HEADER_LENGTH, byteorder=HEADER_BYTEORDER)
    logger.info("sending the header")
    sock.send(header)
    logger.info("sending %s bytes of data", msg_length)
    sock.send(bytes_message)


def server():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    s.bind(('localhost', 10_000))
    s.listen()
    while True:
        logger.info("waiting for client connections")
        client, addr = s.accept()
        with closing(client):
            while True:
                try:
                    msg = recv_message(client)
                    logger.info(f"received msg from client: %s", msg)
                    send_message(client, msg)
                except ClientDisconnectedError:
                    logger.info("client disconnected")
                    break


def client():
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(('localhost', 10000))
    send_message(s, "hello world" * 10)
    while True:
        msg = recv_message(s)
        logger.info(msg)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if sys.argv[1] == "recv":
        server()
    else:
        client()
