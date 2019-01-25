# -*- coding: utf-8 -*-
# Copyright (c) 2018, salesreportsetting and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model import no_value_fields
from frappe.model.document import Document
from frappe.utils import cint, flt
import datetime


class PackingSlips(Document):
	def autoname(self):
		
		#if int(self.package_no)==1:
			
		names = frappe.db.sql_list("""select name from `tabPacking Slips`""")
		mydate= datetime.date.today()
		date=datetime.datetime(mydate.year,mydate.month,mydate.day)
		year_prefix=frappe.db.get_value("Year",mydate.year,"prefix")
		month_prefix=frappe.db.get_value("Month",date.strftime("%B"),"prefix")

		if names:
			# name can be BOM/ITEM/001, BOM/ITEM/001-1, BOM-ITEM-001, BOM-ITEM-001-1

			# split by item
			#names = [name.split(self.product_code)[-1][1:] for name in names]

			# split by (-) if cancelled
			names = [cint(name.split('/')[-1]) for name in names]

			idx = max(names) + 1
		else:
			idx = 1

		self.name = 'PKG/'+str(self.customer)+'/'+str(year_prefix)+'/'+str(month_prefix)+'/'+str(self.package_no) + ('/%.3i' % idx)
