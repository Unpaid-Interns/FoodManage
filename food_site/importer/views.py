from django.shortcuts import render
from importer import CSVImport
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.shortcuts import redirect
from decimal import Decimal
from sku_manage import models
from django.http import HttpResponse
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
            success, conflicts_exist, result_message = importer_module.import_csv()
            #print(result_message)
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
    # print(result_message)
    if "Conflicts exist. Please confirm how to handle them below." in result_message:
        messages.add_message(request, messages.INFO, " ", extra_tags="first")
    split_results_messages = result_message.split('\n')
    for message_to_display in split_results_messages:
        print(message_to_display)
        if (not conflict_dict) and ("Conflicts exist. Please confirm how to handle them below." in message_to_display):
            continue
        messages.add_message(request, messages.INFO, message_to_display, extra_tags="result")
    if "Conflicts exist. Please confirm how to handle them below." in result_message:
        for file_prefix in conflict_dict:
            # print(file_prefix + " in message_displayer")
            conflict_records_list = conflict_dict[file_prefix]
            for conflict_tuple in conflict_records_list:
                # data = conflict_tuple[0]
                # conflict_database_model = conflict_tuple[1]
                database_record_check_message = conflict_tuple[2]
                # print(conflict_tuple[2] + " in message_displayer")
                messages.add_message(request, messages.INFO, database_record_check_message, extra_tags="conflict")
    return render(request, 'importer/messages.html')


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
                shortnames_array = conflict_tuple[3]
                # update conflict database model with data's fields
                if data.__class__.__name__ == "SKU":
                    conflict_database_model.sku_num = data.sku_num
                    conflict_database_model.name = data.name
                    conflict_database_model.case_upc = data.case_upc
                    conflict_database_model.unit_upc = data.unit_upc
                    conflict_database_model.unit_size = data.unit_size
                    conflict_database_model.units_per_case = data.units_per_case
                    temp_product_name_list = models.ProductLine.objects.filter(name=data.product_line.name)
                    if len(temp_product_name_list) > 0:
                        conflict_database_model.product_line = temp_product_name_list[0]
                    temp_formula_list = models.Formula.objects.filter(number=data.formula.number)
                    if len(temp_formula_list) > 0:
                        conflict_database_model.formula = temp_formula_list[0]
                    conflict_database_model.formula_scale = data.formula_scale
                    conflict_database_model.mfg_rate = data.mfg_rate
                    conflict_database_model.mfg_setup_cost = data.mfg_setup_cost
                    conflict_database_model.mfg_run_cost = data.mfg_run_cost
                    conflict_database_model.comment = data.comment
                    fix_mfg_lines(conflict_database_model, shortnames_array)
                elif data.__class__.__name__ == "Ingredient":
                    conflict_database_model.number = data.number
                    conflict_database_model.name = data.name
                    conflict_database_model.vendor_info = data.vendor_info
                    conflict_database_model.package_size = data.package_size
                    conflict_database_model.package_size_units = data.package_size_units
                    conflict_database_model.cost = data.cost
                    conflict_database_model.comment = data.comment
                elif data.__class__.__name__ == "ProductLine":
                    pass
                elif data.__class__.__name__ == "IngredientQty":
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
            shortnames_array = conflict_tuple[3]
            # update conflict database model with data's fields
            if data.__class__.__name__ == "SKU":
                conflict_database_model.sku_num = data.sku_num
                conflict_database_model.name = data.name
                conflict_database_model.case_upc = data.case_upc
                conflict_database_model.unit_upc = data.unit_upc
                conflict_database_model.unit_size = data.unit_size
                conflict_database_model.units_per_case = data.units_per_case
                temp_product_name_list = models.ProductLine.objects.filter(name=data.product_line.name)
                if len(temp_product_name_list) > 0:
                    conflict_database_model.product_line = temp_product_name_list[0]
                temp_formula_list = models.Formula.objects.filter(number=data.formula.number)
                if len(temp_formula_list) > 0:
                    conflict_database_model.formula = temp_formula_list[0]
                conflict_database_model.formula_scale = data.formula_scale
                conflict_database_model.mfg_rate = data.mfg_rate
                conflict_database_model.mfg_setup_cost = data.mfg_setup_cost
                conflict_database_model.mfg_run_cost = data.mfg_run_cost
                conflict_database_model.comment = data.comment
                conflict_database_model.save()
                fix_mfg_lines(conflict_database_model, shortnames_array)
            elif data.__class__.__name__ == "Ingredient":
                conflict_database_model.number = data.number
                conflict_database_model.name = data.name
                conflict_database_model.vendor_info = data.vendor_info
                conflict_database_model.package_size = data.package_size
                conflict_database_model.package_size_units = data.package_size_units
                conflict_database_model.cost = data.cost
                conflict_database_model.comment = data.comment
                conflict_database_model.save()
            elif data.__class__.__name__ == "ProductLine":
                pass
            elif data.__class__.__name__ == "IngredientQty":
                pass
    request.session['serializable_conflict_dict'] = dict()
    request.session['result_message'] = "All entries committed to database"
    return redirect("message_displayer")


def fix_mfg_lines(sku, shortnames_array):
    # Delete all Sku_Mfg_Line's associated with SKU
    models.SkuMfgLine.objects.filter(sku__sku_num=sku.sku_num).delete()

    # Create all Sku_Mfg_Line's again
    sku_mfg_line_array = []
    for ml_shortname in shortnames_array:
        if ml_shortname == "":
            continue
        _, chosen_mfg_line = CSVImport.make_sku_mfg_line(ml_shortname, sku)
        sku_mfg_line_array.append(chosen_mfg_line)
    if len(sku_mfg_line_array) > 0:
        models.SkuMfgLine.objects.bulk_create(sku_mfg_line_array)


def info(request):
    image_data = open('importer/import_instructions.pdf', 'rb').read()
    return HttpResponse(image_data, content_type='application/pdf')
    # return render(request, 'importer/help.html')
