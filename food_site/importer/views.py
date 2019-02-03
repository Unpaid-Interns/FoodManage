from django.shortcuts import render
from importer import CSVImport
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.shortcuts import redirect
from decimal import Decimal
from sku_manage import models
import os


def simple_upload(request):
    try:
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
            serializable_conflict_dict = importer_module.make_serializable_conflict_dict(None)
            request.session['serializable_conflict_dict'] = serializable_conflict_dict
            request.session['result_message'] = result_message
            return redirect("messages/")
        return render(request, 'importer/index.html')
    except:
        return render(request, 'importer/index.html')


def message_displayer(request):
    result_message = request.session.get('result_message')
    serializable_conflict_dict = request.session.get('serializable_conflict_dict')
    importer_module = CSVImport.CSVImport()
    conflict_dict = importer_module.get_conflict_dict_from_serializable(serializable_conflict_dict)
    print(result_message)
    if "Conflicts exist. Please confirm how to handle them below." in result_message:
        messages.add_message(request, messages.INFO, " ", extra_tags="first")
    split_results_messages = result_message.split('\n')
    for message_to_display in split_results_messages:
        messages.add_message(request, messages.INFO, message_to_display, extra_tags="result")
    if "Conflicts exist. Please confirm how to handle them below." in result_message:
        for file_prefix in conflict_dict:
            conflict_records_list = conflict_dict[file_prefix]
            for conflict_tuple in conflict_records_list:
                # data = conflict_tuple[0]
                # conflict_database_model = conflict_tuple[1]
                database_record_check_message = conflict_tuple[2]
                messages.add_message(request, messages.INFO, database_record_check_message, extra_tags="conflict")
    return render(request, 'importer/messages.html')
    # uploaded_file_url = fs.url(filename)
    # return render(request, 'importer/uploadView.html', {
    #     'uploaded_file_url': uploaded_file_url
    # })z


def commit_to_database(request, messagenum):
    offset_for_messagenum = 4
    # print(messagenum)
    # print("commit_to_database")
    # first one = index 4 for messages, ie. messagenum==4 is for index 0
    count = 0
    index = messagenum - offset_for_messagenum
    result_message = request.session.get('result_message')
    serializable_conflict_dict = request.session.get('serializable_conflict_dict')
    importer_module = CSVImport.CSVImport()
    conflict_dict = importer_module.get_conflict_dict_from_serializable(serializable_conflict_dict)
    for file_prefix in conflict_dict:
        conflict_records_list = conflict_dict[file_prefix]
        matching_tuple = None
        for conflict_tuple in conflict_records_list:
            if count == index:
                matching_tuple = conflict_tuple
                data = conflict_tuple[0]
                conflict_database_model = conflict_tuple[1]
                # update conflict database model with data's fields
                if data.__class__.__name__ == "SKUData":
                    conflict_database_model.sku_num = int(data.sku_number)
                    conflict_database_model.name = data.name
                    conflict_database_model.case_upc = Decimal(data.case_upc)
                    conflict_database_model.unit_upc = Decimal(data.unit_upc)
                    conflict_database_model.unit_size = data.unit_size
                    print("Issue is with: " + data.case_count)
                    conflict_database_model.units_per_case = int(data.case_count)
                    temp_product_name_list = models.ProductLine.objects.filter(name=data.product_line)
                    if len(temp_product_name_list) > 0:
                        conflict_database_model.product_line = temp_product_name_list[0]
                    conflict_database_model.comment = data.comment
                elif data.__class__.__name__ == "IngredientData":
                    conflict_database_model.number = int(data.number)
                    conflict_database_model.name = data.name
                    conflict_database_model.vendor_info = data.vendor_info
                    conflict_database_model.package_size = data.package_size
                    conflict_database_model.cost = Decimal(data.cost)
                    conflict_database_model.comment = data.comment
                elif data.__class__.__name__ == "ProductLineData":
                    pass
                elif data.__class__.__name__ == "SKUIngredientData":
                    pass
                conflict_database_model.save()
            count += 1
        if matching_tuple is not None:
            conflict_dict[file_prefix].remove(matching_tuple)
            serializable_conflict_dict = importer_module.make_serializable_conflict_dict(conflict_dict)
            request.session['serializable_conflict_dict'] = serializable_conflict_dict
            if " Successfully overrode database entry(s)." in result_message:
                pass
            else:
                request.session['result_message'] = result_message + " Successfully overrode database entry(s)."
    return redirect("message_displayer")


def commit_all_to_database(request):
    # print("commit_all_to_database")
    result_message = request.session.get('result_message')
    serializable_conflict_dict = request.session.get('serializable_conflict_dict')
    importer_module = CSVImport.CSVImport()
    conflict_dict = importer_module.get_conflict_dict_from_serializable(serializable_conflict_dict)
    for file_prefix in conflict_dict:
        conflict_records_list = conflict_dict[file_prefix]
        matching_tuple = None
        for conflict_tuple in conflict_records_list:
                matching_tuple = conflict_tuple
                data = conflict_tuple[0]
                conflict_database_model = conflict_tuple[1]
                # update conflict database model with data's fields
                if data.__class__.__name__ == "SKUData":
                    conflict_database_model.sku_num = int(data.sku_number)
                    conflict_database_model.name = data.name
                    conflict_database_model.case_upc = Decimal(data.case_upc)
                    conflict_database_model.unit_upc = Decimal(data.unit_upc)
                    conflict_database_model.unit_size = data.unit_size
                    print("Issue is with: " + data.case_count)
                    conflict_database_model.units_per_case = int(data.case_count)
                    temp_product_name_list = models.ProductLine.objects.filter(name=data.product_line)
                    if len(temp_product_name_list) > 0:
                        conflict_database_model.product_line = temp_product_name_list[0]
                    conflict_database_model.comment = data.comment
                elif data.__class__.__name__ == "IngredientData":
                    conflict_database_model.number = int(data.number)
                    conflict_database_model.name = data.name
                    conflict_database_model.vendor_info = data.vendor_info
                    conflict_database_model.package_size = data.package_size
                    conflict_database_model.cost = Decimal(data.cost)
                    conflict_database_model.comment = data.comment
                elif data.__class__.__name__ == "ProductLineData":
                    pass
                elif data.__class__.__name__ == "SKUIngredientData":
                    pass
                conflict_database_model.save()
    request.session['serializable_conflict_dict'] = dict()
    request.session['result_message'] = "All entries committed to database"
    return redirect("message_displayer")
