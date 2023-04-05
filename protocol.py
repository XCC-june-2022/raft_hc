import pickle


def encode_request(method, *args):
    return pickle.dumps((method, args))


def decode_response(request):
    return pickle.loads(request)
