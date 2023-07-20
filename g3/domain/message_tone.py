from enum import Enum


class MessageTone(str, Enum):
    PROFESSIONAL = "professional"
    PERSONAL = "personal"
    FRIENDLY = "friendly"
    FUNNY = "funny"
