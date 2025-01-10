from django.shortcuts import render, redirect
from django.contrib import messages
import mimetypes
from tracker.services.aws_service import download_from_s3, upload_to_s3
from .models import UploadedFile, FileDownload
from django.contrib.auth.decorators import login_required
from authusers.models import CompanyUser

@login_required
def dashboard(request):
    print("User::", request.user)
    # company_user = CompanyUser.objects.get(user=request.user)
    try:
        company_user = CompanyUser.objects.get(user=request.user)
    except CompanyUser.DoesNotExist:
        company_user = None  # Handle case where user might not be linked to a CompanyUser
    
    return render(request, 'tracker/dashboard.html' , {'company_user': company_user})

@login_required
def upload_file(request):
    try:
        company_user = CompanyUser.objects.get(user=request.user)
        if request.method == 'POST' and request.FILES.get('file'):
            file = request.FILES['file']
            file_name = file.name
            file_size = file.size  # File size in bytes
            file_type, _ = mimetypes.guess_type(file_name)  # Guess the MIME type

            file_path = f"uploads/{company_user.company.id}/{file_name}"

            # Upload file to S3 and save the file record in the database
            file_url = upload_to_s3(file, file_path)

            if file_url:  # If upload was successful
                if file_size >= 1024 * 1024:
                    formatted_file_size = f"{file_size / (1024 * 1024):.2f} MB"  # Convert to MB
                else:
                    formatted_file_size = f"{file_size / 1024:.2f} KB"  # Convert to KB
                UploadedFile.objects.create(
                    company=company_user.company,
                    user=request.user,
                    file_name=file_name,
                    file_url=file_url,
                    file_type=file_type or 'unknown',  # Default to 'unknown' if MIME type cannot be guessed
                    file_size=formatted_file_size,
                    remarks=request.POST.get('remarks', '')  # Get remarks if provided in form
                )
                messages.success(request, "File uploaded successfully.")
                return redirect('upload_file')
            else:
                messages.error(request, 'No file selected for upload.')
    except Exception as e:
        # Add error message to messages
        messages.error(request, f"An error occurred: {str(e)}")
    return render(request, 'tracker/upload.html')


@login_required
def file_list(request):
    company_user = CompanyUser.objects.get(user=request.user)

    # Retrieve files only for the company of the logged-in user
    uploaded_files = UploadedFile.objects.filter(company=company_user.company)

    return render(request, 'tracker/file_list.html', {'uploaded_files': uploaded_files})



@login_required
def download_file(request, file_id):
    try:
        company_user = CompanyUser.objects.get(user=request.user)
        file = UploadedFile.objects.get(id=file_id)

        # Ensure the user belongs to the same company as the file
        if file.company != company_user.company:
            return render(request, 'error.html', {'message': 'You do not have permission to access this file.'})

        # Log the download action in the FileDownload model
        FileDownload.objects.create(user=request.user, file=file, company=company_user.company)

        # File path in S3 (assumes you stored it with the path like "uploads/company_id/file_name")
        file_path = f"uploads/{company_user.company.id}/{file.file_name}"

        # Use the download_from_s3 function to fetch the file from S3 and send it as a download
        response = download_from_s3(file_path, file.file_name)
        if response:
            return response
        else:
            return render(request, 'error.html', {'message': 'File download failed.'})

    except UploadedFile.DoesNotExist:
        return render(request, 'error.html', {'message': 'File not found.'})
    except Exception as exp:
        print(f"Error in file download: {str(exp)}")
        return render(request, 'error.html', {'message': 'An error occurred during the download process.'})

