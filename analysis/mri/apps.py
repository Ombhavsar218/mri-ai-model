from django.apps import AppConfig
from tensorflow.keras.models import load_model
from transformers import GPT2LMHeadModel, GPT2Tokenizer
# import torch

class MriConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mri'

    def ready(self):
        # Load the MRI model once when the app starts
        global mri_model
        MODEL_PATH = "/home/ritesh/projects/mri-ai-model/Brain_Tumor_Model.h5"
        mri_model = load_model(MODEL_PATH)

        # Load the GPT-2 model and tokenizer
        global gpt_tokenizer, gpt_model
        try:
            gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")
        except Exception as e:
            print(f"Error loading GPT-2 model: {e}")
