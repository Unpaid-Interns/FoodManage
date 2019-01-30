from django.shortcuts import render
from django.http import HttpResponse
from importer import CSVImportTester
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from importer import CSVImport
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages


# Create your views here.
def index(request):
    # CSVImportTester.run()
    return render(request, 'importer/uploadView.html')
    # return HttpResponse("This is the import view.")


# Upload file
def upload_file(request):
    importer_module = CSVImport()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES['file'])
        importer_module.add_filename(request.FILES['file'])
        importer_module.parse()
        return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        importer_module = CSVImport.CSVImport()
        importer_module.add_filename(filename)
        success, result_message = importer_module.parse()
        print(result_message)
        messages.info(request, result_message)
        uploaded_file_url = fs.url(filename)
        return render(request, 'importer/uploadView.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'importer/uploadView.html')
