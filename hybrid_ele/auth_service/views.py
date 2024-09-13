from django.contrib.auth import authenticate
from ninja import NinjaAPI
from ninja.security import HttpBearer
from django.contrib.auth.models import User
from django.conf import settings
import jwt
from datetime import datetime, timedelta

api = NinjaAPI()

def create_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

@api.post("/login")
def login(request, username: str, password: str):
    user = authenticate(username=username, password=password)
    if user:
        token = create_token(user)
        return {"token": token}
    return {"error": "Invalid credentials"}

@api.post("/register")

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            return user
        except:
            return None

@api.get("/validate-token", auth=AuthBearer())
def validate_token(request):
    return {"valid": True}