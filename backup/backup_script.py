import os
import datetime

debug = False

file_prefix = "backup-"
default_backup_folder_name = "daily"
path = os.path.expanduser("~")
daily_limit = 7
weekly_limit = 4
monthly_limit = 12


def create_backup():
    success, file = get_file()
    if not success:
        print("ERROR: File not found.")
        return
    os.rename(path + "/" + file, path + "/hypo_backups/" + default_backup_folder_name + "/" + file)
    move_backups_as_needed()


def move_backups_as_needed():
    daily_num, weekly_num, monthy_num = get_directory_lengths()
    if daily_num > daily_limit:
        if not move_daily_to_weekly():
            os.remove(path + "/hypo_backups/daily/" + get_oldest_daily())

    daily_num, weekly_num, monthy_num = get_directory_lengths()
    if weekly_num > weekly_limit:
        move_weekly_to_monthly()
        if not move_daily_to_weekly():
            print("deleting from weekly: " + get_weekly("oldest"))
            os.remove(path + "/hypo_backups/weekly/" + get_weekly("oldest"))

    daily_num, weekly_num, monthy_num = get_directory_lengths()
    if monthy_num > monthly_limit:
        remove_oldest_monthly()


def get_oldest_daily():
    file = None
    for i in os.listdir(path + "/hypo_backups/daily"):
        if 'backup-' in i:
            if file is None:
                file = i
            else:
                if get_date_from_filename(i) < get_date_from_filename(file):
                    file = i
    return file


def get_weekly(newest_or_oldest):
    file = None
    for i in os.listdir(path + "/hypo_backups/weekly"):
        if 'backup-' in i:
            if file is None:
                file = i
            else:
                if newest_or_oldest == "oldest":
                    if get_date_from_filename(i) < get_date_from_filename(file):
                        file = i
                else:
                    if get_date_from_filename(i) > get_date_from_filename(file):
                        file = i
    return file


def get_monthly(newest_or_oldest):
    file = None
    for i in os.listdir(path + "/hypo_backups/monthly"):
        if 'backup-' in i:
            if file is None:
                file = i
            else:
                if newest_or_oldest == "oldest":
                    if get_date_from_filename(i) < get_date_from_filename(file):
                        file = i
                else:
                    if get_date_from_filename(i) > get_date_from_filename(file):
                        file = i
    return file


def move_daily_to_weekly():
    oldest_daily_file = get_oldest_daily()
    newest_weekly_file = get_weekly("newest")
    move = False
    if oldest_daily_file is not None:
        if newest_weekly_file is not None:
            delta = get_date_from_filename(oldest_daily_file) - get_date_from_filename(newest_weekly_file)
            if delta.days > 6:
                move = True
        else:
            move = True
    if move:
        os.rename(path + "/hypo_backups/daily/" + oldest_daily_file, path + "/hypo_backups/weekly/" + oldest_daily_file)
    return move


def move_weekly_to_monthly():
    oldest_weekly_file = get_weekly("oldest")
    newest_monthly_file = get_monthly("newest")
    move = False
    if oldest_weekly_file is not None:
        if newest_monthly_file is not None:
            delta_months = (get_date_from_filename(oldest_weekly_file).year
                            - get_date_from_filename(newest_monthly_file).year) * 12 \
                           + get_date_from_filename(oldest_weekly_file).month \
                           - get_date_from_filename(newest_monthly_file).month
            print(oldest_weekly_file)
            print(newest_monthly_file)
            print(delta_months)
            print()
            if delta_months > 0:
                move = True
        else:
            print(oldest_weekly_file)
            print(newest_monthly_file)
            print("neweset monthly NONE")
            print()
            move = True
    if move:

        os.rename(path + "/hypo_backups/weekly/" + oldest_weekly_file, path
                  + "/hypo_backups/monthly/" + oldest_weekly_file)
    return move


def remove_oldest_monthly():
    file = get_monthly("oldest")
    if file is not None:
        os.remove(path + "/hypo_backups/monthly/" + file)


def get_directory_lengths():
    daily_num = 0
    weekly_num = 0
    monthy_num = 0
    for _ in os.listdir(path + "/hypo_backups/daily"):
        daily_num += 1
    for _ in os.listdir(path + "/hypo_backups/weekly"):
        weekly_num += 1
    for _ in os.listdir(path + "/hypo_backups/monthly"):
        monthy_num += 1
    return daily_num-1, weekly_num-1, monthy_num-1


def get_file():
    files = []
    for i in os.listdir(path):
        if os.path.isfile(os.path.join(path, i)) and 'backup-' in i:
            files.append(i)
    if len(files) > 0:
        return True, files[0]
    else:
        return False, None


# format will be 'backup-2019-03-22'
def get_date_from_filename(filename):
    date_string = filename[len(file_prefix):]
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    return date


def test():
    today = datetime.datetime.today()
    for i in range(0, 400):
        f = open(path + "/backup-" + str((today + datetime.timedelta(days=i)).date()), "w+")
        f.close()
        # print("calling backup for: " + str("backup-" + str((today + datetime.timedelta(days=i)).date())))
        create_backup()
    delete_test_files()


def delete_test_files():
    files = []
    for i in os.listdir(path):
        if os.path.isfile(os.path.join(path, i)) and 'backup-' in i:
            files.append(i)
    if len(files) > 0:
        for file in files:
            os.remove(path + "/" + file)
    else:
        return False, None


#test()
create_backup()
