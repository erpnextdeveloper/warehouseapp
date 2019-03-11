from __future__ import unicode_literals
import frappe
from frappe.utils import cint, get_gravatar, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day,flt
from frappe import throw, msgprint, _
from frappe.utils.password import update_password as _update_password
from frappe.desk.notifications import clear_notifications
from frappe.utils.user import get_system_managers
import frappe.permissions
import frappe.share
import re
import string
import random
import json
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import collections
import math
import logging



@frappe.whitelist()
def getLastPackageNumber(customer,warehouse):
	last_no=frappe.db.sql("""select package_no,name from `tabPacking Slips` where customer=%s and warehouse=%s  order by  creation desc limit 1""",(customer,warehouse))
	if last_no:
		if not last_no[0][1]==None:
			pack_doc=frappe.get_doc("Packing Slips",last_no[0][1])
			if int(pack_doc.is_delivery_note)==1:
				return 1
			else:
				return int(last_no[0][0])+1
	else:
		return 1




@frappe.whitelist()
def getItemCode(brand,barcode,print_format,name):
	if print_format=="Item Barcode" or print_format=="90x240":
		item_code=frappe.get_all("Item Barcode",filters={"brand":brand,"barcode":barcode},fields=["name"])
		if not len(item_code)==0:
			#frappe.msgprint(str(item_code[0]["name"]))
			frappe.db.set_value("Packing",name,"item_code",item_code[0]["name"])
			frappe.db.set_value("Packing",name,"barcode",barcode)
			return item_code[0]["name"]
		else:
			frappe.throw("Barcode Not Avaible For This Brand")
	else:
		return barcode


@frappe.whitelist()
def assignSalesOrderInDelivery(delivery_id):
	doc=frappe.get_doc("Delivery Note",delivery_id)
	sales_order_list=frappe.db.sql("""select name from `tabSales Order` where customer=%s and status in('To Deliver','To Deliver and Bill')""",doc.customer)
	#return sales_order_list
	for row in sales_order_list:
		sales_order_data=frappe.get_doc("Sales Order",row[0])
		#return row[0]
		for delivery_item in doc.items:
			for order_item in sales_order_data.items:
				check_item=frappe.get_doc("Delivery Note Item",delivery_item.name)
				if check_item.against_sales_order==None:
					if order_item.item_code==delivery_item.item_code:
						if int(order_item.qty)>=int(delivery_item.qty):
							frappe.db.sql("""update `tabSales Order Item` set delivered_qty=%s where name=%s""",(delivery_item.qty,order_item.name))
							delivery_update=frappe.get_doc("Delivery Note Item",delivery_item.name)
							delivery_update.against_sales_order=row[0]
							delivery_update.save()
						else:
							frappe.db.sql("""update `tabSales Order Item` set delivered_qty=%s where name=%s""",(order_item.qty,order_item.name))	
							qty_diff=int(delivery_item.qty)-int(order_item.qty)
							delivery_update=frappe.get_doc("Delivery Note Item",delivery_item.name)
							delivery_update.against_sales_order=row[0]
							so_detail=order_item.name
							delivery_update.save()
							data_del=frappe.get_doc("Delivery Note",delivery_item.parent)
							idx_len=len(data_del.items)+1
							#deli_item=frappe.get_doc({
						#			"doctype":"Delivery Note Item",
						#			"name":"New Delivery Note Item 1",
						#			"item_code":str(delivery_item.item_code),
						#			"qty":str(qty_diff),
						#			"parent":str(doc.name),
						#			"parenttype": "Delivery Note",
						#			"parentfield": "items",
						#			"uom":str(delivery_item.uom),
						#			"item_name":str(delivery_item.item_name),
						#			"rate":str(delivery_item.rate),
						#			"conversion_factor":delivery_item.conversion_factor,
						#			"idx":idx_len
						#			})
						
						#deli_item.insert()
		doc_final=frappe.get_doc("Delivery Note",delivery_id)
		doc_final.submit()



@frappe.whitelist()
def assignSalesOrderInDelivery1(delivery_id):
	doc=frappe.get_doc("Delivery Note",delivery_id)
	sales_order_list=frappe.db.sql("""select name from `tabSales Order` where customer=%s and status in('To Deliver','To Deliver and Bill')""",doc.customer)
	#return sales_order_list
	#return sales_order_list
	for row in sales_order_list:
		sales_order_data=frappe.get_doc("Sales Order",row[0])
		#return row[0]
		for order_item in sales_order_data.items:
			doc_delivery=frappe.get_doc("Delivery Note",delivery_id)
			for delivery_item in doc_delivery.items:
				check_item=frappe.get_doc("Delivery Note Item",delivery_item.name)
				if check_item.against_sales_order==None:
					if order_item.item_code==delivery_item.item_code:
						if int(order_item.qty)>=int(delivery_item.qty):
							if int(order_item.qty)==int(order_item.delivered_qty):
								continue
							else:

								frappe.db.sql("""update `tabSales Order Item` set delivered_qty=%s where name=%s""",(delivery_item.qty,order_item.name))
								#delivery_update=frappe.get_doc("Delivery Note Item",delivery_item.name)
								#delivery_update.against_sales_order=row[0]
								#delivery_update.save()
								frappe.db.sql("""update `tabDelivery Note Item` set against_sales_order=%s,so_detail=%s where name=%s""",(order_item.parent,order_item.name,delivery_item.name))
								del_doc_change=frappe.get_doc("Delivery Note",delivery_item.parent)
								del_doc_change.save()
						else:
							if int(order_item.qty)==int(order_item.delivered_qty):
								continue
							else:
								del_qty=int(order_item.qty)-int(order_item.delivered_qty)
								frappe.db.sql("""update `tabSales Order Item` set delivered_qty=%s where name=%s""",(del_qty,order_item.name))	
								qty_diff=int(delivery_item.qty)-int(del_qty)
								#delivery_update=frappe.get_doc("Delivery Note Item",delivery_item.name)
								frappe.db.sql("""update `tabDelivery Note Item` set against_sales_order=%s,so_detail=%s where name=%s""",(order_item.parent,order_item.name,delivery_item.name))
								#delivery_update.against_sales_order=row[0]
								#so_detail=order_item.name
								#delivery_update.save()
								data_del=frappe.get_doc("Delivery Note",delivery_item.parent)
								idx_len=len(data_del.items)+1
								update_del_item=frappe.get_doc("Delivery Note Item",delivery_item.name)
								update_del_item.qty=del_qty
								update_del_item.save()
								deli_item=frappe.get_doc({
										"doctype":"Delivery Note Item",
										"name":"New Delivery Note Item 1",
										"item_code":str(delivery_item.item_code),
										"qty":str(qty_diff),
										"parent":str(doc.name),
										"parenttype": "Delivery Note",
										"parentfield": "items",
										"uom":str(delivery_item.uom),
										"item_name":str(delivery_item.item_name),
										"rate":str(delivery_item.rate),
										"conversion_factor":delivery_item.conversion_factor,
										"idx":idx_len,
										"warehouse":delivery_item.warehouse,
										"cost_center":delivery_item.cost_center
										})
						
								deli_item.insert()
								del_doc_change=frappe.get_doc("Delivery Note",delivery_item.parent)
								del_doc_change.save()
		doc_final=frappe.get_doc("Delivery Note",delivery_id)
		doc_final.save()
		

@frappe.whitelist()
def getAddressName(warehouse):
	add_name=frappe.db.sql("""select ta.name from `tabAddress` as ta inner join `tabDynamic Link` as dl on ta.name=dl.parent where dl.link_name=%s""",warehouse)
	if add_name:
		if not add_name[0][0]==None:
			return add_name[0][0]
		else:
			frappe.throw("{0} Address Not Found".format(warehouse))
	else:
		frappe.throw("{0} Address Not Found".format(warehouse))

@frappe.whitelist()
def updatePackingSlip(name):
	frappe.db.set_value("Packing Slips",name,"is_delivery_note",1)


@frappe.whitelist()
def addImageLink():
	doc=frappe.get_all("Item",filters={'disabled':0},fields=["name"])
	for row in doc:
		frappe.db.set_value("Item",row.name,"custom_image",'files/'+str(row.name)+'.jpg')


@frappe.whitelist()
def getItemCodeForIB(brand,barcode,name):
	item_code=frappe.get_all("Brand Wise Barcode",filters={"brand":brand,"barcode":barcode},fields=["name"])
	if not len(item_code)==0:
		#frappe.msgprint(str(item_code[0]["name"]))
		frappe.db.set_value("Box Barcode 100x100",name,"item_code",item_code[0]["name"])
		addChildEntry(name,'Box Barcode 100x100',item_code[0]["name"])
		return item_code[0]["name"]
	else:
		frappe.throw("Barcode Not Avaible For This Brand")

def addChildEntry(name,doctype,item):
	doc=frappe.get_doc(doctype,name)
	check_duplicate=frappe.db.sql("""select name from `tabPacking Items` where parent=%s and item=%s""",(name,item))
	if len(check_duplicate)>=1:
		get_child_doc=frappe.get_doc("Packing Items",check_duplicate[0][0])
		get_child_doc.qty=flt(get_child_doc.qty)+flt(1)
		get_child_doc.save()
	else:
		child_item=frappe.get_doc(dict(
			doctype="Packing Items",
			source_warehouse=doc.source_warehouse,
			target_warehouse=doc.target_warehouse,
			item=item,
			qty=1,
			parent=doc.name,
			parenttype=doc.doctype,
			parentfield="packing_items",
			idx=len(doc.packing_items)+1
		)).insert()
	

@frappe.whitelist()
def getItemCodeForGB(brand,barcode,name):
	item_code=frappe.get_all("Brand Wise Barcode",filters={"brand":brand,"barcode":barcode},fields=["name"])
	if not len(item_code)==0:
		#frappe.msgprint(str(item_code[0]["name"]))
		frappe.db.set_value("Godrej Barcode 90x240",name,"item_code",item_code[0]["name"])
		addChildEntry(name,'Godrej Barcode 90x240',item_code[0]["name"])
		return item_code[0]["name"]
	else:
		frappe.throw("Barcode Not Avaible For This Brand")


@frappe.whitelist()
def getItemCodeForSB(barcode,name):
	item_code=frappe.get_all("Item",filters={"name":barcode},fields=["name"])
	if not len(item_code)==0:
		#frappe.msgprint(str(item_code[0]["name"]))
		frappe.db.set_value("Small Barcode 10x100",name,"item_code",item_code[0]["name"])
		addChildEntry(name,'Small Barcode 10x100',item_code[0]["name"])
		return item_code[0]["name"]
	else:
		frappe.throw("Barcode Not Avaible In Item Master")


@frappe.whitelist()
def getWarehouse():
	warehouse=frappe.get_list("Warehouse",filters={},fields=["name"])
	return warehouse


@frappe.whitelist()
def makeStockEntry(name,doctype):
	doc=frappe.get_doc(doctype,name)
	for row in doc.packing_items:
		if not row.source_warehouse:
			msg="Source Warehouse Is Mandatory For Row: "+str(row.idx)
			frappe.throw(msg) 
		if not row.target_warehouse:
			msg="Target Warehouse Is Mandatory For Row: "+str(row.idx)
			frappe.throw(msg) 
	
	message=''
	for row in doc.packing_items:
		result=make_stock_entry(row.item,row.source_warehouse,row.target_warehouse,row.qty)
		message=message+' '+str(result)
	frappe.msgprint("Stock Entry Created :"+str(message))




@frappe.whitelist()
def make_stock_entry(item_code,s_warehouse,t_warehouse,qty=None):
	bom_no=getBOMNo(item_code)
	stock_entry = frappe.new_doc("Stock Entry")
	stock_entry.purpose ="Manufacture"
	stock_entry.company = frappe.defaults.get_global_default("company")
	stock_entry.from_bom = 1
	stock_entry.bom_no = bom_no
	stock_entry.fg_completed_qty = qty
	stock_entry.from_warehouse= s_warehouse
	stock_entry.to_warehouse = t_warehouse
	stock_entry.get_items()
	res=stock_entry.insert()
	res.submit()
	return res.name
	





def getBOMNo(item_code):
	bom=frappe.get_all("BOM",filters={"item":item_code,"is_default":1},fields=["name"])
	if bom:
		return bom[0].name

	else:
		msg="BOM Not Available For Item:"+str(item_code)
		frappe.throw(msg)
	







