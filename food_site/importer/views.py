from django.shortcuts import render
from importer import CSVImport
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import os


# Create your views here.
def index(request):
    return render(request, 'importer/uploadView.html')


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        importer_module = CSVImport.CSVImport()
        importer_module.clear_filenames()
        importer_module.add_filename(filename)
        success, result_message = importer_module.parse()
        print(result_message)
        os.remove(filename)
        messages.info(request, result_message)
        uploaded_file_url = fs.url(filename)
        return render(request, 'importer/uploadView.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'importer/uploadView.html')
