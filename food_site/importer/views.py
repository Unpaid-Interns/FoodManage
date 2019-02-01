from django.shortcuts import render
from importer import CSVImport
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.shortcuts import redirect
import os


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
        serializable_conflict_dict = importer_module.make_serializable_conflict_dict()
        for item in serializable_conflict_dict:
            print(item)
            print(serializable_conflict_dict[item])
        request.session['serializable_conflict_dict'] = serializable_conflict_dict
        request.session['result_message'] = result_message
        return redirect("messages/")
    return render(request, 'importer/index.html')


def message_displayer(request):
    result_message = request.session.get('result_message')
    serializable_conflict_dict = request.session.get('serializable_conflict_dict')
    importer_module = CSVImport.CSVImport()
    conflict_dict = importer_module.get_conflict_dict_from_serializable(serializable_conflict_dict)
    print(result_message)
    # if result_message == "Conflicts exist. Please confirm how to handle them below.":
    #     messages.add_message(request, messages.INFO, " ", extra_tags="first")
    split_results_messages = result_message.split('\n')
    for message_to_display in split_results_messages:
        messages.add_message(request, messages.INFO, message_to_display, extra_tags="result")
    if result_message == "Conflicts exist. Please confirm how to handle them below.":
        for file_prefix in conflict_dict:
            conflict_records_list = conflict_dict[file_prefix]
            for conflict_tuple in conflict_records_list:
                # data = conflict_tuple[0]
                # TODO: use this later: importer_module.add_data_to_commit_dict(file_prefix, data)
                # conflict_database_model = conflict_tuple[1]
                database_record_check_message = conflict_tuple[2]
                messages.add_message(request, messages.INFO, database_record_check_message, extra_tags="conflict")
    return render(request, 'importer/messages.html')
    # uploaded_file_url = fs.url(filename)
    # return render(request, 'importer/uploadView.html', {
    #     'uploaded_file_url': uploaded_file_url
    # })z


def commit_to_database(request, messagenum):
    print(messagenum)
    print("commit_to_database")
    return redirect("message_displayer")

def commit_all_to_database(request):
    print("commit_all_to_database")
    return redirect("message_displayer")
