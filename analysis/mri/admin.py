from django.contrib import admin
from .models import Registration,MRIImage,Expert,DoctorInfo,MRIRecord,ReviewLog,CompleteReview

admin.site.register(Registration)
admin.site.register(MRIImage)
admin.site.register(Expert)
admin.site.register(DoctorInfo)
admin.site.register(MRIRecord)
admin.site.register(ReviewLog)
admin.site.register(CompleteReview)