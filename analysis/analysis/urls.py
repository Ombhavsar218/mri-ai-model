from django.contrib import admin
from django.urls import path, include
from mri import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),  # Admin page
    path('login/', views.login_user, name='login'),  # Root path for login view
    path('home/', views.home, name='home'),    # Path for the home page
    path('register/', views.register_user, name='register'),  # Path for the register page
    path('mri/', include(('mri.urls', 'mri'), namespace='mri')), # Include URLs from the mri app
    path("submit_correction/", views.submit_correction, name="submit_correction"),
    path('process-mri-form/', views.process_mri_form, name='process_mri_form'),
    path('', views.dashboard, name='dashboard'),
    path('expert-login/', views.expert_login, name='expertlogin'),
    path('expert-reg/', views.expert_register, name='expertreg1'),
    path('expert-dashboard/', views.expert_dashboard, name='expertdashboard'),
    path('info-form/', views.info_form, name='infoform'),
    path("send_to_expert/", views.send_to_expert, name="send_to_expert"),
    path("submit_recommendation/", views.submit_recommendation, name="submit_recommendation"),
    path("submit_precaution/", views.submit_precaution, name="submit_precaution"),
    path('checkings/', views.all_mri_records, name='checkings'),
    path('record/<int:record_id>/', views.record_detail, name='record_detail'),
    path('record/<int:record_id>/print/', views.print_mri_report, name='print_mri_report'),
    path('record/<int:record_id>/pdf/', views.download_mri_pdf, name='download_mri_pdf'),
    path('patients/', views.patient_list, name='patient_list'),
    path('expertdoctor/', views.expertdoctor, name='expertdoctor'),
    path('doctor/', views.doctor, name='doctor'),
    path("generate-response", views.generate_response, name="generate_response"),
    #path("password-reset/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset_form.html"), name="password_reset"),
    #path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    #path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), name="password_reset_confirm"),
    #path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
    path("password-reset/", views.custom_password_reset_request, name="custom-password-reset"),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
