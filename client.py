import socket
from raft.message_interface import send_message, recv_message
from raft.protocol import encode_request, decode_response

def run_echo_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall('hello world'.encode())
        response = s.recv(1024).decode()

    print(f'client received {response}')


class NetworkedKVClient:

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    def __getitem__(self, item):
        send_message(self.s, encode_request('GET', item))
        resp_method, val = decode_response(recv_message(self.s))
        if resp_method == 'UNKNOWN':
            raise KeyError(f'key {item} not found')
        elif resp_method == 'RETURN':
            return val[0]
        else:
            raise TypeError(f'invalid response method {resp_method}')

    def __setitem__(self, key, value):
        send_message(self.s, encode_request('SET', key, value))
        resp_method, *_ = decode_response(recv_message(self.s))
        if resp_method != 'OK':
            raise ValueError(f'{resp_method}')

    def __delitem__(self, key):
        send_message(self.s, encode_request('DELETE', key))
        resp_method, val = decode_response(recv_message(self.s))
        if resp_method == 'UNKNOWN':
            raise KeyError(f'key {key} not found')
