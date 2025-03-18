from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from tensorflow.keras.models import load_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import numpy as np
import cv2
import os
import base64
from io import BytesIO
from PIL import Image
from .forms import RegistrationForm,LoginForm
from .models import Registration
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware
from django.http import HttpResponseRedirect
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MRIImage
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def home(request):
    return render(request, 'mri/index.html')


from django.contrib.auth.models import User

def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password1']

        try:
            # Check if a user with the given email exists
            user = Registration.objects.get(email=email)
        except Registration.DoesNotExist:
            user = None

        if user is not None and check_password(password, user.password):  # Verify hashed password
            # Log in the user (managing session manually if using a custom user model)
            request.session['user_id'] = user.id  # Store user ID in session
            return redirect('mri/home')  # Redirect to index.html
        else:
            # Invalid credentials, return with an error
            return render(request, 'mri/login.html', {'error': 'Invalid email or password', 'popup_active': True})

    return render(request, 'mri/login.html')



def register_user(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            # Check if passwords match
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            
            if password1 != password2:
                # If passwords don't match, show an error
                return render(request, 'mri/register.html', {'form': form, 'status': 'Passwords do not match'})
            
            # Hash password before saving to the database
            hashed_password = make_password(password1)
            
            # Save the registration data
            Registration.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=hashed_password
            )
            
            # Show success popup on first render
            return render(request, 'mri/register.html', {'form': RegistrationForm(), 'status': 'success'})
        
        else:
            # If form is invalid, return with error status
            return render(request, 'mri/register.html', {'form': form, 'status': 'error'})

    # For GET requests, no popup should appear
    return render(request, 'mri/register.html', {'form': RegistrationForm(), 'status': None})



# Load the trained model
MODEL_PATH = "D:/Final Project2/Final Project2/Final Project/Brain_Tumor_Model.h5"
model = load_model(MODEL_PATH)


def predict_image(image_file):
    # Read the image as a byte stream using PIL
    image = Image.open(image_file)
    
    # Convert the image to a NumPy array
    img_array = np.array(image)
    
    # Convert RGB to BGR (OpenCV uses BGR by default)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # Preprocessing: Resize the image to the model's expected input size
    img_resized = cv2.resize(img_bgr, (224, 224))  # Change 224x224 to your model's input size if different

    # Normalize the image (if necessary)
    img_normalized = img_resized / 255.0  # Example normalization, modify according to your model

    # Expand dimensions to match the batch size (since models expect 4D input)
    img_expanded = np.expand_dims(img_normalized, axis=0)

    # Predict using the model
    predictions = model.predict(img_expanded)
    
    # Define the classes in the same order as the model output
    class_names = ["glioma", "meningioma", "notumor", "pituitary"]

    # Get the predicted class by finding the index of the highest probability
    predicted_class_index = np.argmax(predictions)
    predicted_class = class_names[predicted_class_index]
    confidence = predictions[0][predicted_class_index]

    # Determine tumor status
    if predicted_class == "notumor":
        tumor_status = "Tumor not detected"
    else:
        tumor_status = "Tumor detected"

    return predicted_class, confidence, tumor_status


def process_form(request):
    if request.method == "POST":
        # Handle image upload
        image_file = request.FILES.get("image-upload")
        if image_file:
            # Convert the uploaded image to base64 for display in the template
            image = Image.open(image_file)
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # Perform the actual prediction using the image
            prediction, confidence, tumor_status = predict_image(image_file)
            
            # Convert confidence to percentage format
            confidence_percentage = confidence * 100  # Convert to percentage

            # Extract patient details from the form
            patient_name = request.POST.get("patient_name")
            patient_age = request.POST.get("patient_age")
            patient_weight = request.POST.get("patient_weight")
            blood_group = request.POST.get("blood_group")
            gender = request.POST.get("gender")
            doctor_name = request.POST.get("diagnosis")
            medical_type = request.POST.get("medical_type")
            medical_problem = request.POST.get("medical_problem")
            
            # Render the results page with the prediction and tumor status
            return render(request, "mri/results.html", {
                "image_base64": img_base64,
                "prediction": prediction,
                "confidence": confidence_percentage,  # Pass the confidence as a percentage
                "tumor_status": tumor_status,
                "patient_name": patient_name,
                "patient_age": patient_age,
                "patient_weight": patient_weight,
                "blood_group": blood_group,
                "gender": gender,
                "diagnosis": doctor_name,
                "medical_type": medical_type,
                "medical_problem": medical_problem,
            })
        else:
            return JsonResponse({"status": "error", "message": "No image uploaded."})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."})




def logout_user(request):
    logout(request)  # Clear the session and log out the user
    response = redirect('mri:login')  # Redirect to the login page
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Prevent caching
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response



def prevent_cache(view_func):
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return wrapper

@prevent_cache
def home(request):
    return render(request, 'mri/index.html')


# Initialize GPT-2
gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")

# Function to generate GPT-2 response
def generate_gpt2_response(user_message):
    try:
        inputs = gpt_tokenizer.encode(user_message, return_tensors="pt")
        outputs = gpt_model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)
        response = gpt_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    except Exception as e:
        print(f"Error generating GPT-2 response: {e}")
        return "Sorry, something went wrong with the chatbot."

# View to handle chatbot messages
'''@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        data = json.loads(request.body)  # Parse the JSON body
        print("Received message:", data.get("message"))  # Log received message

        if data.get("message"):
            user_message = data.get("message")
            response = generate_gpt2_response(user_message)
            print("Generated response:", response)  # Log generated response
            return JsonResponse({"response": response})

        return JsonResponse({"response": "Invalid input!"})
    return JsonResponse({"response": "Only POST requests are allowed!"})'''


def process_mri_form(request):
    if request.method == "POST":
        image_id = request.POST.get("image_id")
        corrected_label = request.POST.get("corrected_label")

        if not image_id:  # 🔴 Handle missing image_id
            return JsonResponse({"error": "No image ID provided"}, status=400)

        mri_image = get_object_or_404(MRIImage, id=image_id)
        mri_image.corrected_label = corrected_label
        mri_image.reviewed_by_doctor = True
        mri_image.save()

        return JsonResponse({"success": "Correction saved successfully!"})
@csrf_exempt
def submit_correction(request):
    if request.method == "POST":
        image_id = request.POST.get("image_id")
        corrected_label = request.POST.get("corrected_label")

        print(f"🚀 Received image_id: {image_id}")  # Debugging

        if not image_id:
            print("🚨 No image ID received in request!")  
            return JsonResponse({"message": "No image ID provided"}, status=400)

        # 🔍 Log all available MRIImage IDs
        all_images = MRIImage.objects.all().values_list('id', flat=True)
        print(f"🔍 Existing MRIImage IDs: {list(all_images)}")

        try:
            mri_image = MRIImage.objects.get(id=image_id)
            mri_image.corrected_label = corrected_label
            mri_image.reviewed_by_doctor = True
            mri_image.save()
            return JsonResponse({"message": "Correction saved successfully!"})
        except MRIImage.DoesNotExist:
            print(f"🚨 MRIImage with ID {image_id} not found!")  
            return JsonResponse({"message": "Image not found"}, status=404)

    return JsonResponse({"message": "Invalid request"}, status=400)
