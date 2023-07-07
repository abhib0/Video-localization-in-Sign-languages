from django.shortcuts import render, redirect 
from django.http import HttpResponse
from .forms import UploadFileForm
from .models import MyModel
import sys
from subprocess import run, PIPE
import os
from django.conf import settings
import mimetypes
from django.shortcuts import render, redirect
from pytube import *
import yt_dlp
import ssl 
ssl._create_default_https_context = ssl._create_unverified_context  
from pytube import YouTube

from example import func
import random
# Create your views here.
def home(request):
    return render(request, 'signlanguage.html',{})


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():  # Validate the form
            file = request.FILES.get('file')  # Use .get() to avoid KeyError
            if file:
                file_name = 'one.mp4'
                file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                mymodel = MyModel.objects.create(file=file_path)
                mymodel.save()
                message = "Hello, World!"
                ans = func(message)
                random_number = random.randint(1000, 9999)
                return render(request, 'signlanguage.html', {'filename': file_name, 'msg': ans, 'random_number': random_number})
    else:
        form = UploadFileForm()
    return render(request, 'signlanguage.html', {'form' : form})


def index(request):
    if request.method == 'POST':
          
        link = request.POST['link']
        output_folder = '/Users/anishasinghoberoi/django-webapp/signlanguage/static/vids'
        output_filename = 'one.mp4' 
        output_path = os.path.join(output_folder, output_filename)
        if os.path.exists(output_path):
            os.remove(output_path)

        ydl_opts = {
            'format': 'best', 
            'outtmpl': output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        return render(request, 'signlanguage2.html', {'msg':'Video downloaded','filename': 'one.mp4',})
            
    return render(request, 'signlanguage2.html', {'msg':''})
   





def display_video(request):
    video = MyModel.objects.last()  # Retrieve the latest uploaded video
    return render(request, 'signlanguge.html', {'video': video})

def reporting(request):
	return request

def external(request):
    inp='hello'
    out = run(sys.executable,['util.py', inp], shell = False, stdout = PIPE)
    print(out)
    return render(request,'signlanguage.html', {'data1':out})



def download_file(request, filename=''):
    if filename != '':
        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Define the full file path
        filepath = BASE_DIR + '/docs/Files/' + filename
        # Open the file for reading content
        path = open(filepath, 'rb')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response
    else:
        # Load the template
        return render(request, 'signlanguage.html')
