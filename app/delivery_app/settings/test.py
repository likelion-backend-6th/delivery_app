from threading import local
from .base import *

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "*",
]

CSRF_TRUSTED_ORIGINS = []
