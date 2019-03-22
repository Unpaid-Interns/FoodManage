from os import system
from datetime import date

system('../food-site/manage.py dumpdata > backup')
system('scp backup vcm@vcm-8261.vm.duke.edu:backup-{date}'.format(date=date.today()))
system('rm backup')
