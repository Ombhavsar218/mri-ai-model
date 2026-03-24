from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from tensorflow.keras.models import load_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import numpy as np
import cv2
# import os
import base64
from io import BytesIO
from PIL import Image
from .forms import RegistrationForm,LoginForm,ExpertRegistrationForm, ExpertLoginForm,RecommendationForm
from .models import Registration,MRIRecord,CompleteReview
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout
# from django.utils.decorators import decorator_from_middleware
# from django.middleware.cache import CacheMiddleware
# from django.http import HttpResponseRedirect
from transformers import GPT2LMHeadModel, GPT2Tokenizer
# import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MRIImage,Expert,DoctorInfo,Registration
# import json
# from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
import json
import requests
from weasyprint import HTML
from django.template.loader import render_to_string
from django.http import HttpResponse
from .utils.llama_client import get_llama_response
from .forms import CustomPasswordResetForm
from .utils.yolo_utils import yolo_inference
import os

def home(request):
    return render(request, 'mri/index.html')




def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password1']

        # Check if a user with the given email exists
        users = Registration.objects.filter(email=email)
        user = None
        
        for u in users:
            if check_password(password, u.password):
                user = u
                break

        if user is not None:
            # Log in the user (managing session manually if using a custom user model)
            request.session['user_id'] = user.id  # Store user ID in session
            return redirect('home')  # Redirect to index.html
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



# Lazily load the trained model to prevent memory issues during Django startup
_mri_model = None

def get_mri_model():
    global _mri_model
    if _mri_model is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        MODEL_PATH = os.path.join(BASE_DIR, "Brain_Tumor_Model.h5")
        _mri_model = load_model(MODEL_PATH)
    return _mri_model


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
    predictions = get_mri_model().predict(img_expanded)
    
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
            try:
                mri_image = MRIImage.objects.get(image_base64=img_base64)
                prediction = mri_image.corrected_label
                confidence = mri_image.confidence
                tumor_status = mri_image.corrected_label
            except MRIImage.DoesNotExist:
                # Perform the actual prediction using the image
                prediction, confidence, tumor_status = predict_image(image_file)
                # Convert confidence to percentage format
                confidence = confidence * 100 
  

            # Extract patient details from the form
            patient_name = request.POST.get("patient_name")
            patient_age = request.POST.get("patient_age")
            patient_weight = request.POST.get("patient_weight")
            blood_group = request.POST.get("blood_group")
            gender = request.POST.get("gender")
            doctor_name = request.POST.get("diagnosis")
            medical_type = request.POST.get("medical_type")
            medical_problem = request.POST.get("medical_problem")
            
            # Save data to database
            mri_record = MRIRecord.objects.create(
                patient_name=patient_name,
                patient_age=patient_age,
                patient_weight=patient_weight,
                blood_group=blood_group,
                gender=gender,
                doctor_name=doctor_name,
                medical_type=medical_type,
                medical_problem=medical_problem,
                mri_image=image_file,
                prediction=prediction,
                tumor_status=tumor_status  # Removed confidence field
            )

            # Perform YOLO inference for tumor detection
            annotated_path, tumor_count = yolo_inference(mri_record.mri_image.path)

            # Render the results page with the prediction and tumor status
            return render(request, "mri/results.html", {
                "image_base64": img_base64,
                "prediction": prediction,
                 "confidence": confidence,  # Renamed correctly
                "tumor_status": tumor_status,
                "patient_name": patient_name,
                "patient_age": patient_age,
                "patient_weight": patient_weight,
                "blood_group": blood_group,
                "gender": gender,
                "diagnosis": doctor_name,
                "medical_type": medical_type,
                "medical_problem": medical_problem,
                'annotated': settings.MEDIA_URL + os.path.relpath(annotated_path, settings.MEDIA_ROOT),  # result
                'tumor_count': tumor_count,
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


# # Initialize GPT-2
# gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")

# # Function to generate GPT-2 response
# def generate_gpt2_response(user_message):
#     try:
#         inputs = gpt_tokenizer.encode(user_message, return_tensors="pt")
#         outputs = gpt_model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)
#         response = gpt_tokenizer.decode(outputs[0], skip_special_tokens=True)
#         return response
#     except Exception as e:
#         print(f"Error generating GPT-2 response: {e}")
#         return "Sorry, something went wrong with the chatbot."

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
            mri_image = MRIImage.objects.get(image_base64=image_id)
            mri_image.corrected_label = corrected_label
            mri_image.reviewed_by_doctor = True
            mri_image.confidence = 90.0
            mri_image.save()
            return JsonResponse({"message": "Correction saved successfully!"})
        except MRIImage.DoesNotExist:
            print(f"🚨 MRIImage with ID {image_id} not found!")  
            mri_image = MRIImage.objects.create(image_base64=image_id)
            mri_image.corrected_label = corrected_label
            mri_image.reviewed_by_doctor = True
            mri_image.confidence = 90.0
            mri_image.save()
            return JsonResponse({"message": "Correction saved successfully!"})

    return JsonResponse({"message": "Invalid request"}, status=400)


def dashboard(request):
    return render(request, 'mri/dashboard.html')

# Expert Registration View
def expert_register(request):
    if request.method == "POST":
        form = ExpertRegistrationForm(request.POST)
        
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 != password2:
                return render(request, "mri/expertreg1.html", {"form": form, "status": "error_password"})

            # Hash password before saving
            form.instance.password = make_password(password1)
            form.save()
            return render(request, "mri/expertreg1.html", {"form": ExpertRegistrationForm(), "status": "success"})

    else:
        form = ExpertRegistrationForm()
    
    return render(request, "mri/expertreg1.html", {"form": form})


def expert_login(request):
    if request.method == "POST":
        email = request.POST.get('email')  # Ensure this matches the form input name
        password = request.POST.get('password')  # Change 'password1' to 'password'

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'mri/expertlogin.html', {'error': 'Email and password are required.', 'popup_active': True})

        try:
            user = Expert.objects.get(email=email)
        except Expert.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, 'mri/expertlogin.html', {'error': 'Email and password are required.', 'popup_active': True})

        if check_password(password, user.password):  # Verify hashed password
            request.session['expert_id'] = user.id  # Store session
            request.session['expert_email'] = user.email  # ✅ Add this line
            return redirect("expertdashboard")  # Change this to your dashboard view
        else:
             return render(request, 'mri/expertlogin.html', {'error': 'Invalid email or password', 'popup_active': True})

    return render(request, "mri/expertlogin.html")


# Expert Dashboard View
#@login_required
def expert_dashboard(request):
    return render(request, 'mri/expertdashboard.html')

def info_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        experience = request.POST.get('experience')
        specialization = request.POST.get('specialization')
        qualification = request.POST.get('qualification')
        gender = request.POST.get('gender')
        city_state = request.POST.get('city_state')
        profile_image = request.FILES.get('profile_image')

        doctor = DoctorInfo(
            name=name,
            age=age,
            mobile=mobile,
            email=email,
            experience=experience,
            specialization=specialization,
            qualification=qualification,
            gender=gender,
            city_state=city_state,
            profile_image=profile_image
        )
        doctor.save()

        request.session['notification_alerts'] = [{'message': 'Information submitted successfully!', 'tags': 'success'}]
        return redirect('infoform')

    notification_alerts = request.session.pop('notification_alerts', None)
    return render(request, 'mri/infoform.html', {'notification_alerts': notification_alerts})


@csrf_exempt
def send_to_expert(request):
    if request.method == "POST":
        try:
            patient_name = request.POST.get("patient_name")

            # ✅ Prevent duplicate records
            existing_record = MRIRecord.objects.filter(patient_name=patient_name).first()
            if existing_record:
                return JsonResponse({"message": "Record already exists!"}, status=200)

            # ✅ Handle image file properly
            image_file = request.FILES.get("image")

            MRIRecord.objects.create(
                patient_name=patient_name,
                patient_age=request.POST.get("patient_age"),
                patient_weight=request.POST.get("patient_weight"),
                blood_group=request.POST.get("blood_group"),
                gender=request.POST.get("gender"),
                doctor_name=request.POST.get("doctor_name"),
                medical_type=request.POST.get("medical_type"),
                medical_problem=request.POST.get("medical_problem"),
                prediction=request.POST.get("prediction"),
                tumor_status=request.POST.get("tumor_status"),
                mri_image=image_file,  # ✅ Store Image
                recommendation=request.POST.get("recommendation"),  # ✅ Store recommendation
                precaution=request.POST.get("precaution")  # ✅ Store precaution
            )

            return JsonResponse({"message": "Data sent successfully!"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def submit_recommendation(request):
    if request.method == "POST":
        recommendation = request.POST.get("recommendation")

        if not recommendation:
            return JsonResponse({"error": "No recommendation provided"}, status=400)

        # Save to the latest record
        latest_record = MRIRecord.objects.last()
        if latest_record:
            latest_record.recommendation = recommendation
            latest_record.save()

        return JsonResponse({"message": "Recommendation saved successfully!"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def submit_precaution(request):
    if request.method == "POST":
        precaution = request.POST.get("precaution")

        latest_record = MRIRecord.objects.last()
        if latest_record:
            latest_record.precaution = precaution
            latest_record.save()

        return JsonResponse({"message": "Precaution saved successfully!"})
    if not precaution:
        return JsonResponse({"error": "No recommendation provided"}, status=400)

def expert_dashboard(request):
    total_scans = CompleteReview.objects.count()
    pending_reports = MRIRecord.objects.count()
    expert_count = Expert.objects.count()
    doctor_count = DoctorInfo.objects.count()
    total_doctors = expert_count + doctor_count

    context = {
    'total_scans': total_scans,
    'pending_reports': pending_reports,
    'total_doctors': total_doctors,
    'expert_doctors': expert_count,
    'normal_doctors': doctor_count,
}
    return render(request, 'mri/expertdashboard.html', context)

def all_mri_records(request):
    records = MRIRecord.objects.all()
    return render(request, 'mri/checkings.html', {'records': records})

@csrf_exempt
def record_detail(request, record_id):
    record = get_object_or_404(MRIRecord, id=record_id)

    if request.method == "POST":
        recommendation = request.POST.get("recommendation")
        precaution = request.POST.get("precaution")

        if recommendation is not None:
            record.recommendation = recommendation
        if precaution is not None:
            record.precaution = precaution

        record.save()
        return redirect('record_detail', record_id=record.id)

    return render(request, 'mri/record_detail.html', {'record': record})

def print_mri_report(request, record_id):
    record = get_object_or_404(MRIRecord, id=record_id)

    # Move the record to CompleteReview
    review = CompleteReview.objects.create(
        patient_name=record.patient_name,
        patient_age=record.patient_age,
        gender=record.gender,
        medical_type=record.medical_type,
        prediction=record.prediction,
        tumor_status=record.tumor_status,
        doctor_name=record.doctor_name,
        medical_problem=record.medical_problem,
        recommendation=record.recommendation,
        precaution=record.precaution,
        mri_image=record.mri_image
    )

    # Delete the record from MRIRecord after moving
    record.delete()

    # Pass the newly created review object to the template
    return render(request, 'mri/printable_report.html', {
        'record': review
    })


def download_mri_pdf(request, record_id):
    record = get_object_or_404(CompleteReview, pk=record_id)
    html_string = render_to_string('mri/printable_report.html', {'record': record})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=report_{record_id}.pdf'
    return response

def patient_list(request):
    reviews = CompleteReview.objects.all()
    return render(request, 'mri/patient_list.html', {'reviews': reviews})

def expertdoctor(request):
    doctors = DoctorInfo.objects.all()
    return render(request, 'mri/expertdoctor.html', {'doctors': doctors})

def doctor(request):
    # Fetch all users (filter by group or is_staff if needed)
    doctors = Registration.objects.all().values('username', 'email')  # Only username and email
    return render(request, 'mri/doctor.html', {'doctors': doctors})


def generate_response(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        message = data.get("message", "")
        response = get_llama_response(message)
        return JsonResponse({"response": response})
    return JsonResponse({"response": "Invalid request."}, status=400)


def custom_password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Fetch user object from Registration or Expert
            user = Registration.objects.filter(email=email).first() or Expert.objects.filter(email=email).first()

            if user:
                # Here, generate and send your custom reset link via email
                # You can store a token and link them to a reset view
                print(f"Send reset link to: {user.email}")
                messages.success(request, "Password reset link has been sent to your email.")
                return redirect("login")
    else:
        form = CustomPasswordResetForm()
    return render(request, "mri/custom_password_reset_form.html", {"form": form})


def predict_tumor(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['image']
        path = default_storage.save('uploads/' + uploaded_file.name, ContentFile(uploaded_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, path)

        annotated_path, boxes = yolo_inference(full_path)

        tumor_count = len(boxes)

        return render(request, 'result.html', {
            'original': settings.MEDIA_URL + path,
            'annotated': settings.MEDIA_URL + os.path.relpath(annotated_path, settings.MEDIA_ROOT),
            'tumor_count': tumor_count,
        })

def delete_mri_record(request, record_id):
    if request.method == "POST":
        record = get_object_or_404(MRIRecord, id=record_id)
        record.delete()
        return JsonResponse({"message": "Record deleted successfully.", "status": "success"})
    return JsonResponse({"error": "Invalid request method."}, status=400)
