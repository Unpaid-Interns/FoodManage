from os import system
from datetime import date

system('pwd')
system('../food_site/manage.py dumpdata > backup')
system('scp backup vcm@vcm-8261.vm.duke.edu:backup-{date}'.format(date=date.today()))
system('rm backup')
