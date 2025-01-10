from django.db import models
from django.contrib.auth.models import User
from authusers.models import Company

class UploadedFile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    file_type = models.CharField(max_length=50)
    file_size = models.CharField(max_length=50)
    remarks = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class FileDownload(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)
