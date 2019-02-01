from django.shortcuts import render
from importer import CSVImport
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.messages import get_messages
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
        success, result_message,  = importer_module.parse()
        print(result_message)
        os.remove(filename)
        split_results_messages = result_message.split('\n')
        for message_to_display in split_results_messages:
            messages.add_message(request, messages.INFO, message_to_display, extra_tags="result")
        if result_message == "Conflicts exist. Please confirm how to handle them below.":
            for file_prefix in importer_module.conflict_dict:
                # TODO
                pass
                # messages.add_message(request, messages.INFO, "TEST MESSAGE", extra_tags="conflict")
        uploaded_file_url = fs.url(filename)
        return render(request, 'importer/uploadView.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'importer/uploadView.html')
