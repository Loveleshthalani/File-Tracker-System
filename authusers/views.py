from django.shortcuts import render, redirect

from authusers.forms import CompanyForm
from django.contrib import messages
from .models import Company, CompanyUser, RoleEnum
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

def superuser_required(user):
    return user.is_superuser

# View to create a new company
@user_passes_test(superuser_required)
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_company')
    else:
        form = CompanyForm()

    return render(request, 'authusers/create_company.html', {'form': form})

# View to add a user to a company
def add_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        company_id = request.POST['company']
        role = request.POST['role']
        company = Company.objects.get(id=company_id)

        user = User.objects.create_user(username=username, password=password)
        CompanyUser.objects.create(user=user, company=company, role=role)
        messages.success(request, "User Added successfully!.")
        return redirect('add_user')
    if request.user.is_superuser:
        companies = Company.objects.all()
    else:
        companyid= CompanyUser.objects.filter(user_id=request.user.id).values_list('company_id', flat=True).first()
        companies = Company.objects.filter(id=companyid)

    users = User.objects.select_related('companyuser').order_by('id').values(
    'id', 'username', 'email', 'companyuser__company__name'
    )
        
    roles = [(role.name, role.value) for role in RoleEnum] 
    return render(request, 'authusers/add_user.html', {'companies': companies, 'roles':roles, 'users': users})

def logout():
    pass