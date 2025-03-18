from django.urls import path
from . import views

app_name = 'mri'  # Register the namespace

urlpatterns = [
    path('home/', views.home, name='home'),          # Home page URL
    path('login/', views.login_user, name='login'),  # Login page URL
    path('register/', views.register_user, name='register'),  # Register page URL
    path("process-form/", views.process_form, name="process_form"),
    path('logout/', views.logout_user, name='logout'),
    #path('generate-response/', views.chatbot_view, name='generate_response'),
    path("submit_correction/", views.submit_correction, name="submit_correction"),
    path('process-mri-form/', views.process_mri_form, name='process_mri_form'),
]
