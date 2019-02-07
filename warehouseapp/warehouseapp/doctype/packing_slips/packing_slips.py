# -*- coding: utf-8 -*-
# Copyright (c) 2018, salesreportsetting and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model import no_value_fields
from frappe.model.document import Document
from frappe.utils import cint, flt
import datetime
import random


class PackingSlips(Document):
	def autoname(self):
		
		#if int(self.package_no)==1:
			
		names = frappe.db.sql_list("""select name from `tabPacking Slips`""")
		mydate= datetime.date.today()
		date=datetime.datetime(mydate.year,mydate.month,mydate.day)
		year_prefix=frappe.db.get_value("Year",mydate.year,"prefix")
		month_prefix=frappe.db.get_value("Month",date.strftime("%B"),"prefix")
		idx = self.package_no

		self.name = 'MB-'+str(year_prefix)+str(month_prefix)+'-'+str(self.id_generator()) + ('-%.3i' % idx)

	def id_generator(self):
		num=''.join(random.choice('0123456789') for _ in range(6))
		check_num=frappe.db.sql("""select name from `tabRandom Number Generator` where name=%s""",num)
		if len(check_num)>=1:
			self.id_generator()
		else:
			return num
