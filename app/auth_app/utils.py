import jwt, datetime
from django.conf import settings

def generate_jwt(user):
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def decode_jwt(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None

def generate_tokens(user):
    access_payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        'iat': datetime.datetime.utcnow(),
    }
    refresh_payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow(),
        'type': 'refresh'
    }
    return {
        'access': jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256'),
        'refresh': jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
    }
