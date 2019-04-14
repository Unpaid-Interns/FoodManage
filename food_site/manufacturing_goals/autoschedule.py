from datetime import datetime, time, timedelta
from django.utils import timezone
from sku_manage import models as data_models
from manufacturing_goals import models as mfg_models


def autoschedule(start_time, stop_time, manufacturingqtys_to_be_scheduled, current_user):
    # print("***********************************************************")
    # print("***********************************************************")
    # print("***********************************************************")
    start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
    stop_time = timezone.make_aware(stop_time, timezone.get_current_timezone())
    tz = start_time.tzinfo
    valid_manufacturing_lines = data_models.ManufacturingLine.objects.filter(plantmanager__user=current_user)
    if current_user.is_superuser:
        # print("USER IS ADMIN")
        valid_manufacturing_lines = data_models.ManufacturingLine.objects.all()
    if len(valid_manufacturing_lines) < 1:
        return False, "ERROR: Plant Manager user does not have any Manufacturing Lines associated with them.", \
               None, None
    manufacturingqtys_to_be_scheduled = check_ties_for_mfgqty_to_be_scheduled(manufacturingqtys_to_be_scheduled.order_by("goal__deadline"))
    scheduled_items, unscheduled_items = create_schedule(start_time, stop_time, manufacturingqtys_to_be_scheduled,
                                      valid_manufacturing_lines, current_user, tz)
    # print_schedule(start_time, stop_time, valid_manufacturing_lines, scheduled_items, unscheduled_items)
    if len(unscheduled_items) < 1:
        return True, "SUCCESS: Schedule created without error. All items scheduled.", scheduled_items, None
    else:
        message_string = "WARNING: Schedule created but not all items were scheduled. See unscheduled items below:\n"
        for mfgqty in unscheduled_items:
            message_string += "SKU#: " + str(mfgqty.sku.sku_num) + ", SKU Name: " + str(mfgqty.sku.name) \
                              + ", Goal: "+ str(mfgqty.goal.name) + "\n"
        return True, message_string, scheduled_items, unscheduled_items


def create_schedule(start_time, stop_time, manufacturingqtys_to_be_scheduled, valid_manufacturing_lines, current_user,
                    tz):
    new_scheduled_items = []
    unscheduled_items = []
    mfgqty_to_available_lines = {}

    # get available lines for each mfgQty
    for mfgqty in manufacturingqtys_to_be_scheduled:
        valid_lines_for_mfgqty = get_mfglines_for_sku(mfgqty.sku, valid_manufacturing_lines)
        mfgqty_to_available_lines[mfgqty] = valid_lines_for_mfgqty

    # pick line
    for mfgqty in manufacturingqtys_to_be_scheduled:
        print(mfgqty.sku.name)
        duration = mfgqty_duration(mfgqty)
        chosen_line = None
        earliest_start_time = None
        add_to_schedule = True
        # check all available lines for earliest start time
        for line in mfgqty_to_available_lines[mfgqty]:
            if chosen_line is not None:
                continue

            # get items already scheduled on line
            # previously_scheduled_items = \
            #     (mfg_models.ScheduleItem.objects.filter(mfgline=line) + new_scheduled_items).order_by("start")

            # get already scheduled items
            previously_scheduled_items = mfg_models.ScheduleItem.objects.filter(mfgline=line).order_by("start")
            temp_prev_schuled_items = []
            for item in previously_scheduled_items:
                if item.start is not None:
                    temp_prev_schuled_items.append(item)
            previously_scheduled_items = temp_prev_schuled_items

            # if nothing scheduled on this line, check if it fits in given time
            if len(previously_scheduled_items) < 1:
                if stop_time - start_time >= duration:
                    # print("Scheduling at start time because line is empty and there is adequate time.")
                    earliest_start_time = start_time
                    chosen_line = line
                    continue
                else:
                    # print("MFGQTY DOESN'T FIT ON LINE: ", line)
                    # print("DURATION of MFGQTY GOAL: ", duration)
                    # print("AVAILABLE TIME: ", stop_time - start_time)
                    add_to_schedule = False
                    continue

            # check if earliest start time is the beginning of time on that line
            if previously_scheduled_items[0].start - start_time >= duration:
                # print("Scheduling at beginning of start time since there is time between first scheduled item and start time.")
                earliest_start_time = start_time
                chosen_line = line
                continue

            # otherwise, must check in between already scheduled items on that line
            for index in range(0, len(previously_scheduled_items) - 2):
                next_item_start = previously_scheduled_items[index+1].start
                item_end = previously_scheduled_items[index].end()
                if next_item_start - item_end >= duration:
                    if earliest_start_time is None:
                        # print("Scheduling between lines.")
                        earliest_start_time = item_end
                        chosen_line = line
                    else:
                        if item_end < earliest_start_time:
                            # print("Scheduling between lines.")
                            earliest_start_time = item_end
                            chosen_line = line

            # lastly, check if can schedule at end
            last_end_time = previously_scheduled_items[len(previously_scheduled_items)-1].end()
            if stop_time - last_end_time >= duration:
                if earliest_start_time is None:
                    # print("Scheduling at end of time between last scheduled item and end of deadline.")
                    earliest_start_time = last_end_time
                    chosen_line = line
                else:
                    if last_end_time < earliest_start_time:
                        # print("Scheduling at end of time between last scheduled item and end of deadline.")
                        earliest_start_time = last_end_time
                        chosen_line = line


        # print("CHOSEN LINE:")
        # print(chosen_line)

        if add_to_schedule and (chosen_line is not None) and finishes_before_deadline(mfgqty, earliest_start_time):
            new_schedule_item = create_schedule_item(mfgqty, chosen_line, earliest_start_time, current_user)
            new_scheduled_items.append(new_schedule_item)
            # test for ability to do this
            # print("Scheduled:")
            # print(new_schedule_item.mfgqty.sku.sku_num)
            # print(new_schedule_item.start)
            new_schedule_item.save()
        else:
            # print("Unscheduled")
            # print(mfgqty.sku.name)
            unscheduled_items.append(mfgqty)
        print()

    return new_scheduled_items, unscheduled_items


def get_mfglines_for_sku(sku, valid_manufacturing_lines):
    # not SkuMfgLine?
    lines = data_models.ManufacturingLine.objects.filter(skumfgline__sku=sku)
    valid_lines_for_mfgqty = []
    for line in lines:
        if line in valid_manufacturing_lines:
            valid_lines_for_mfgqty.append(line)
    return valid_lines_for_mfgqty


def create_schedule_item(mfgqty, mfgline, start, provisional_user):
    return mfg_models.ScheduleItem(mfgqty=mfgqty, mfgline=mfgline, start=start,
                                   provisional_user=provisional_user)


def check_ties_for_mfgqty_to_be_scheduled(manufacturingqtys_to_be_scheduled):
    manufacturingqtys_to_be_scheduled = list(manufacturingqtys_to_be_scheduled)
    no_conflicts = False
    while not no_conflicts:
        no_conflicts = True
        # copy?
        manufacturingqtys_to_be_scheduled_copy = manufacturingqtys_to_be_scheduled
        prev_duration = None
        prev_deadline = None
        index = 0
        for mfgqty in manufacturingqtys_to_be_scheduled_copy:
            deadline = mfgqty.goal.deadline
            duration = mfgqty_duration(mfgqty)
            if prev_deadline is None or prev_duration is None:
                prev_deadline = mfgqty.goal.deadline
                prev_duration = duration
                index += 1
                continue
            if deadline == prev_deadline:
                if duration < prev_duration:
                    no_conflicts = False
                    manufacturingqtys_to_be_scheduled[index], manufacturingqtys_to_be_scheduled[index - 1] = \
                        manufacturingqtys_to_be_scheduled[index - 1], manufacturingqtys_to_be_scheduled[index]
            index += 1
    return manufacturingqtys_to_be_scheduled


def mfgqty_duration(mfgqty):
    return timedelta(hours=(mfgqty.caseqty / mfgqty.sku.mfg_rate))


def finishes_before_deadline(mfgqty, start_time):
    duration = mfgqty_duration(mfgqty)
    deadline = mfgqty.goal.deadline
    return start_time + duration <= deadline


def print_schedule(start_time, end_time, valid_mfg_lines, new_scheduled_items, unscheduled_items):
    print("----------------------------------------------------------------------------")
    print("----------------------------------------------------------------------------")
    print("Overall start time: " + str(start_time))
    print("  Overall end time: " + str(end_time))
    print("TOTAL TIME ALLOWED: " + str(end_time - start_time))
    for line in valid_mfg_lines:
        print("----------------------------------------------------------------------------")
        # scheduled_items = (mfg_models.ScheduleItem.objects.filter(mfgline=line) + new_scheduled_items).order_by("start")
        scheduled_items = mfg_models.ScheduleItem.objects.filter(mfgline=line).order_by("start")
        print("Line = " + line.name)
        if len(scheduled_items) < 1:
            print()
            print("Line is empty.")
        for item in scheduled_items:
            print()
            print("SKU#: " + str(item.mfgqty.sku.sku_num))
            print("Start: " + str(item.start))
            print("End: " + str(item.end()))
    print("----------------------------------------------------------------------------")
    print("----------------------------------------------------------------------------")
    print("MfgQty's not scheduled:")
    if len(unscheduled_items) < 1:
        print()
        print("All scheduled.")
    for mfgqty in unscheduled_items:
        print()
        print("SKU#: " + str(mfgqty.sku.sku_num))
        print("Duration: " + str(mfgqty_duration(mfgqty)))
        print("Lines:")
        lines = data_models.ManufacturingLine.objects.filter(skumfgline__sku=mfgqty.sku)
        for line in lines:
            if line in valid_mfg_lines:
                print("line = " + line.name)
    print("----------------------------------------------------------------------------")
    print("----------------------------------------------------------------------------")
