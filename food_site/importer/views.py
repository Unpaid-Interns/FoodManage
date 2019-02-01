from django.shortcuts import render
from importer import CSVImport
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.messages import get_messages
import os

importer_module = None

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
        if result_message == "Conflicts exist. Please confirm how to handle them below.":
            messages.add_message(request, messages.INFO, " ", extra_tags="first")
        split_results_messages = result_message.split('\n')
        for message_to_display in split_results_messages:
            messages.add_message(request, messages.INFO, message_to_display, extra_tags="result")
        if result_message == "Conflicts exist. Please confirm how to handle them below.":
            for file_prefix in importer_module.conflict_dict:
                conflict_records_list = importer_module.conflict_dict[file_prefix]
                for conflict_tuple in conflict_records_list:
                    # data = conflict_tuple[0]
                    # TODO: use this later: importer_module.add_data_to_commit_dict(file_prefix, data)
                    # conflict_database_model = conflict_tuple[1]
                    database_record_check_message = conflict_tuple[2]
                    messages.add_message(request, messages.INFO, database_record_check_message, extra_tags="conflict")
        uploaded_file_url = fs.url(filename)
        return render(request, 'importer/uploadView.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'importer/uploadView.html')

def commit_to_database(request):
    pass
