from datetime import datetime, time, timedelta
from sku_manage import models as data_models
from manufacturing_goals import models as mfg_models


def autoschedule(start_time, stop_time, manufacturingqtys_to_be_scheduled, current_user):
    valid_manufacturing_lines = data_models.ManufacturingLine.objects.filter(plantmanager__user=current_user)
    if len(valid_manufacturing_lines) > 1:
        return False, "ERROR: Plant Manager user does not have any Manufacturing Lines associated with them.", None
    manufacturingqtys_to_be_scheduled = check_ties_for_mfgqty_to_be_scheduled(manufacturingqtys_to_be_scheduled.order_by("goal__deadline"))
    scheduled_items = create_schedule(start_time, stop_time, manufacturingqtys_to_be_scheduled,
                                      valid_manufacturing_lines, current_user)
    print_schedule(valid_manufacturing_lines, scheduled_items)
    return True, "SUCCESS: Schedule created without error.", scheduled_items


def create_schedule(start_time,stop_time, manufacturingqtys_to_be_scheduled, valid_manufacturing_lines, current_user):
    new_scheduled_items = []
    mfgqty_to_available_lines = {}

    # get available lines for each mfgQty
    for mfgqty in manufacturingqtys_to_be_scheduled:
        valid_lines_for_mfgqty = get_mfglines_for_sku(mfgqty.sku, valid_manufacturing_lines)
        mfgqty_to_available_lines[mfgqty] = valid_lines_for_mfgqty

    # pick line
    for mfgqty in manufacturingqtys_to_be_scheduled:
        duration = mfgqty_duration(mfgqty)
        chosen_line = None
        earliest_start_time = None
        # check all available lines for earliest start time
        for line in mfgqty_to_available_lines[mfgqty]:
            # get items already scheduled on line
            previously_scheduled_items = \
                (mfg_models.ScheduleItem.objects.filter(mfgline=line) + new_scheduled_items).order_by("start")

            # if nothing scheduled on this line, check if it fits in given time
            if len(previously_scheduled_items) < 1:
                if start_time - stop_time >= duration:
                    earliest_start_time = start_time
                    chosen_line = line
                    continue

            # check if earliest start time is the beginning of time on that line
            if previously_scheduled_items[0].start - start_time >= duration:
                earliest_start_time = start_time
                chosen_line = line
                continue

            # otherwise, must check in between already scheduled items on that line
            for index in range(0, len(previously_scheduled_items) - 2):
                next_item_start = previously_scheduled_items[index+1].start
                item_end = previously_scheduled_items[index].end()
                if next_item_start - item_end >= duration:
                    if item_end < earliest_start_time:
                        earliest_start_time = item_end
                        chosen_line = line

            # lastly, check if can schedule at end
            last_end_time = previously_scheduled_items[len(previously_scheduled_items)-1].end()
            if last_end_time - stop_time >= duration:
                if last_end_time < earliest_start_time:
                    earliest_start_time = last_end_time
                    chosen_line = line

        if chosen_line is None:
            continue
        new_schedule_item = create_schedule_item(mfgqty, chosen_line, earliest_start_time, current_user)
        new_scheduled_items.append(new_schedule_item)
    return new_scheduled_items


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
    no_conflicts = False
    while not no_conflicts:
        no_conflicts = True
        manufacturingqtys_to_be_scheduled_copy = manufacturingqtys_to_be_scheduled.copy()
        prev_duration = None
        prev_deadline = None
        index = 0
        for mfgqty in manufacturingqtys_to_be_scheduled_copy():
            deadline = mfgqty.goal.deadline
            duration = mfgqty_duration(mfgqty)
            if prev_deadline is None or prev_duration is None:
                prev_deadline = mfgqty.goal.deadline
                prev_duration = duration
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


def print_schedule(valid_mfg_lines, new_scheduled_items):
    for line in valid_mfg_lines:
        print("----------------------------------------------------------------------------")
        scheduled_items = (mfg_models.ScheduleItem.objects.filter(mfgline=line) + new_scheduled_items).order_by("start")
        print("Line = " + line.name)
        for item in scheduled_items:
            print()
            print("SKU#: " + str(item.mfgqty.sku.sku_num))
            print("Start: " + str(item.start))
            print("End: " + str(item.end()))
