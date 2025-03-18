from django.contrib import admin
from django.urls import path, include
from mri import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin page
    path('', views.login_user, name='login'),  # Root path for login view
    path('home/', views.home, name='home'),    # Path for the home page
    path('register/', views.register_user, name='register'),  # Path for the register page
    path('mri/', include(('mri.urls', 'mri'), namespace='mri')), # Include URLs from the mri app
    path("submit_correction/", views.submit_correction, name="submit_correction"),
    path('process-mri-form/', views.process_mri_form, name='process_mri_form'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
