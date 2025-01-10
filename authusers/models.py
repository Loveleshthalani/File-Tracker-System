from django.db import models
from django.contrib.auth.models import User, Group, Permission
import enum
class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class RoleEnum(enum.Enum):
    Admin = "Admin"
    Manager = "Manager"
    Viewer = "Viewer"

class CompanyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=50,
                            choices=[(tag.name, tag.value) for tag in RoleEnum]
                            )  # Admin, Manager, Employee
    
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"
