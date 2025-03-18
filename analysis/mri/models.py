from django.db import models

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
