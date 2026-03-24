from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager

class Registration(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    
    def __str__(self):
        return self.username
    
class MRIImage(models.Model):
    image = models.ImageField(upload_to="mri_uploads/")
    image_base64 = models.TextField(blank=True, null=True)
    ai_prediction = models.CharField(max_length=100)
    confidence = models.FloatField(blank=True, null=True)
    corrected_label = models.CharField(max_length=100, blank=True, null=True)  # Doctor’s correction
    reviewed_by_doctor = models.BooleanField(default=False)  # Indicates if corrected

    def __str__(self):
        return f"Prediction: {self.ai_prediction} | Corrected: {self.corrected_label if self.corrected_label else 'N/A'}" 

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Expert(models.Model):  # Changed from Registration to Expert
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords

    def __str__(self):
        return self.username


class DoctorInfo(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    experience = models.IntegerField()
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    city_state = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='doctor_profiles/', null=True, blank=True)


    def __str__(self):
        return self.name


class MRIRecord(models.Model):
    patient_name = models.CharField(max_length=255)
    patient_age = models.IntegerField()
    patient_weight = models.FloatField()
    blood_group = models.CharField(max_length=5)
    gender = models.CharField(max_length=10)
    doctor_name = models.CharField(max_length=255)
    medical_type = models.CharField(max_length=255)
    medical_problem = models.TextField()
    prediction = models.CharField(max_length=255)
    tumor_status = models.CharField(max_length=255)
    mri_image = models.ImageField(upload_to="mri_images/", blank=True, null=True)
    recommendation = models.TextField(null=True, blank=True)
    precaution = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient_name} - {self.prediction}"

class ReviewLog(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    mri_record = models.ForeignKey(MRIRecord, on_delete=models.CASCADE)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expert.username} reviewed {self.mri_record.patient_name}"

class CompleteReview(models.Model):
    patient_name = models.CharField(max_length=100)
    patient_age = models.IntegerField()
    gender = models.CharField(max_length=10)
    patient_mobile = models.CharField(max_length=15)
    patient_email = models.EmailField()
    prediction = models.CharField(max_length=100)
    tumor_status = models.CharField(max_length=100)
    doctor_name = models.CharField(max_length=100)
    medical_type = models.CharField(max_length=255)
    medical_problem = models.TextField()
    recommendation = models.TextField(blank=True, null=True)
    precaution = models.TextField(blank=True, null=True)
    mri_image = models.ImageField(upload_to='mri_completed/', null=True, blank=True)

    def __str__(self):
        return f"{self.patient_name} - {self.prediction}"




