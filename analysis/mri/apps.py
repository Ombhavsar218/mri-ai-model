from django.apps import AppConfig
from tensorflow.keras.models import load_model
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
# import torch

class MriConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mri'

    def ready(self):
        # Models are now lazily loaded in views.py to prevent memory errors with Django's autoreloader.
        pass
