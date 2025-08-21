"""
Help router for Karma System bot.
Handles help and support requests.
"""
from aiogram import Router
from aiogram.types import Message
import os

router = Router()

# This router is included in main.py but handlers are minimal
# since help is mainly handled in menu.py
