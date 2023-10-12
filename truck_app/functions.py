import json

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import CustomUser as User


def remove_string(value=None):
    x = value
    x = x.strip('"')
    return x
