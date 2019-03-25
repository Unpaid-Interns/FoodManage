from background_task import background
from sku_manage.models import SKU
from .models import SalesRecord, Customer
from datetime import date, timedelta, datetime
from decimal import Decimal
import time
import urllib


@background(schedule=1)
def scrape():
	for skuo in SKU.objects.all():
		sku = skuo.sku_num
		for year in range(1999,date.today().year+1):
			time.sleep(.2)
			url = 'http://hypomeals-sales.colab.duke.edu:8080/?sku='+str(sku)+'&year='+str(year)
			dat = urllib.request.urlopen(url)
			for line in dat.readlines():
				line = str(line)
				if '<tr>' in line and '<td>' in line:
					cur = line.split('<td>')
					cust = None
					ppc = cur[7][0:(len(cur[7])-3)]
					if Customer.objects.filter(name=cur[5],number=cur[4]).exists():
						cust = Customer.objects.filter(name=cur[5],number=cur[4])[0]
					else:
						cust = Customer.objects.create(name=cur[5],number=cur[4])
					if SalesRecord.objects.filter(
						sku = skuo,
						date = date(year=int(cur[1]), month=1, day=1)+timedelta(days=(int(cur[3])-1)*7),
						customer = cust,
						cases_sold = int(cur[6]),
						price_per_case = Decimal(ppc)
						).exists():
						continue
					srec = SalesRecord.objects.create(
						sku = skuo,
						date = date(year=int(cur[1]), month=1, day=1)+timedelta(days=(int(cur[3])-1)*7),
						customer = cust,
						cases_sold = int(cur[6]),
						price_per_case = Decimal(ppc)
						)
	return

