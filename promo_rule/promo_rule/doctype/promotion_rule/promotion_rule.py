# -*- coding: utf-8 -*-
# Copyright (c) 2018, taherkhalil52@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os, json
import copy
from frappe.utils import cstr
from frappe import utils
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from unidecode import unidecode
from frappe.model.document import Document


class Promotionrule(Document):
	pass

base_brand_present ={} #to store if a base brand is present 
base_ig_present = {}  #to store if a base item group is present
brandlist = {}  #to store number of items belonging to same brand in cart
iglist={}   #to store number of items belonging to same item group in cart
igamount={} #to store total price amount of items in same item group
brandamout ={} #to store total price amount of items in with same brand
min_amount_list ={}  #to store all the items prices in a brand to find out the one with minimum amount
discount =0 

@frappe.whitelist(allow_guest=True)
def apply_promo_rule(name,items,pos_profile):
	doc = json.loads(name)
	# frappe.errprint(pos_profile)
	global base_ig_present
	global base_brand_present
	global brandlist
	global iglist
	global igamount
	global brandamout
	global min_amount_list
	# global discount
	brandlist = {}  #reset all the global variable on each call
	iglist={}
	igamount={}
	brandamout ={}
	min_amount_list ={}
	base_ig_present = {} 
	base_brand_present ={} 
	discount = 0
	dis =0
	promo_list = frappe.db.sql("select name from `tabPromotion rule` ORDER BY `priority` DESC", as_list=1)
	promorules = [x[0] for x in promo_list]
	frappe.errprint(promorules)

	for x in doc['items']:    #count  amount of all  of the  brands and item group in cart  
		if x['item_group'] not in igamount:
			igamount[x['item_group']] =x['amount']
		else:
			igamount[x['item_group']]=igamount.get(x['item_group'], 0) + x['amount']
		if x['brand'] not in brandamout:
			brandamout[x['brand']] = x['amount']
		else:
			brandamout[x['brand']] = brandamout.get(x['brand'], 0) + x['amount']


	for x in doc['items']:    #count quantity of  all  of the  brands and item group in cart  
		if x['item_group'] not in iglist:
			iglist[x['item_group']] =x['qty']
		else:
			iglist[x['item_group']]=iglist.get(x['item_group'], 0) + x['qty']
		if x['brand'] not in brandlist:
			brandlist[x['brand']] = x['qty']
		else:
			brandlist[x['brand']] = brandlist.get(x['brand'], 0) + x['qty']

	for x in doc['items']:
		for pro in promorules:    #check in all promo rules if its applicable to that item .
			p = frappe.get_doc("Promotion rule", pro)
			# frappe.errprint(p.pos_profile_table )
			poslist = {}
			for pp in p.pos_profile_table:
				poslist[pp.pos_profiles] =pp.pos_profiles
			if pos_profile not in poslist:
				continue
			if p.to_date < now_datetime().date() or p.from_date > now_datetime().date() or not p.is_active:
				# frappe.errprint(now_datetime().date())
				# frappe.errprint(get_datetime(p.to_date))
				# frappe.errprint('date condition not satisfied')
				continue
				
			if p.base_type == "Item Group" and p.target_type == "Item Group":
				igtotal(x,p)
				# if x['item_group'] in base_ig_present and iglist.get(x['item_group'], 0) >= p.target_qty :
				# 	x['discount_percentage'] = p.discount_percentage
			if p.base_type == "Brand" and p.target_type == "Brand":
				brandtotal(x,p)
				# if x['brand'] in base_brand_present and brandlist.get(x['brand'], 0) >= p.target_qty:
				# 	x['discount_percentage'] = p.discount_percentage
			if p.base_type == "Item Group" and p.target_type == "Brand":
				igtotal(x,p)
				# if x['brand'] in base_ig_present and brandlist.get(x['brand'], 0) >= p.target_qty:
				# 	x['discount_percentage'] = p.discount_percentage
			if p.base_type == "Brand" and p.target_type == "Item Group": 
				brandtotal(x,p)
				# if x['item_group'] in base_brand_present and iglist.get(x['item_group'], 0) >= p.target_qty :
				# 	x['discount_percentage'] = p.discount_percentage

	for x in doc['items']:
		if x['item_group'] in base_ig_present or x['item_group'] in base_brand_present:
			frappe.errprint("in for item group in tgt")
			tgt = x['item_group']
			if base_ig_present.get(x['item_group']):
				promo = base_ig_present.get(x['item_group'])
			else:
				promo = base_brand_present.get(x['item_group'])
			p = frappe.get_doc("Promotion rule",promo)
			target_type = p.target_type
			frappe.errprint(target_type)
			calculate_min_of_group(tgt,promo,doc,target_type)
		if x['brand'] in base_brand_present or x['brand'] in base_ig_present:
			frappe.errprint("in for brand in tgt")
			tgt = x['brand']
			frappe.errprint(tgt)
			if base_brand_present.get(x['brand']):
				promo = base_brand_present.get(x['brand'])
			else:
				promo = base_ig_present.get(x['brand'])
			frappe.errprint(promo)
			p = frappe.get_doc("Promotion rule",promo)
			target_type = p.target_type
			calculate_min_of_group(tgt,promo,doc,target_type)


	for m in min_amount_list:
		dis = dis + min_amount_list.get(m,0)

	return dis

def igtotal(x,p):
	if p.by_amount:
		# frappe.errprint("by amount")
		#if base and target are same , then existing should be greater than min, else it will apply on same item 
		if p.base == p.target and x['item_group'] == p.base and p.is_active and igamount.get(x['item_group'], 0) > p.min_amount:
			if p.target not in base_ig_present:
				base_ig_present[p.target] = p.name

		elif p.base != p.target and x['item_group'] == p.base and p.is_active and igamount.get(x['item_group'], 0) >= p.min_amount:
			if p.target not in base_ig_present:
				base_ig_present[p.target] = p.name
				
	else:
		#if base and target are same , then existing should be greater than min, else it will apply on same item 
		if p.base == p.target and x['item_group'] == p.base and p.is_active and iglist.get(x['item_group'], 0) > p.base_qty:
			if p.target not in base_ig_present:
				base_ig_present[p.target] = p.name
		elif p.base != p.target and x['item_group'] == p.base and p.is_active and iglist.get(x['item_group'], 0) >= p.base_qty:
			if p.target not in base_ig_present:
				base_ig_present[p.target] =p.name
				frappe.errprint(base_ig_present)
				
def brandtotal(x,p):

	if p.by_amount:
		if p.base == p.target and x['brand'] == p.base and p.is_active and brandamout.get(x['brand'], 0) > p.min_amount:
			if p.target not in base_brand_present:
				base_brand_present[p.target] = p.name

		elif p.base != p.target and x['brand'] == p.base and p.is_active and brandamout.get(x['brand'], 0) >= p.min_amount:
			if p.target not in base_brand_present:
				base_brand_present[p.target]=p.name
	else:
		if p.base == p.target and x['brand'] == p.base and p.is_active and brandlist.get(x['brand'], 0) > p.base_qty:
			if p.target not in base_brand_present:
				base_brand_present[p.target] = p.name

		if p.base != p.target and x['brand'] == p.base and p.is_active and brandlist.get(x['brand'], 0) >= p.base_qty:
			if p.target not in base_brand_present:
				base_brand_present[p.target] = p.name

def calculate_min_of_group(tgt,promo,doc,target_type):
	p = frappe.get_doc("Promotion rule",promo)
	temp_dict ={}
	global discount
	if target_type == "Item Group":
		for x in doc['items']:
			if x['item_group'] == tgt:
				temp_dict[x['item_code']] = x['rate']

		min_amount_item =min(temp_dict, key=temp_dict.get)
		frappe.errprint(min_amount_item)
		for x in doc['items']:
			frappe.errprint(x['item_code'])
			if x['item_code'] == min_amount_item and x['qty'] <=p.target_qty:
				frappe.errprint("if satisfied")
				discount = float(x['rate'] * p.discount_percentage * x ['qty']/ 100)
				frappe.errprint(discount)
				alt_dis =copy.deepcopy(discount)
			elif x['item_code'] == min_amount_item and x['qty'] > p.target_qty:
				frappe.errprint("elif came")
				discount = float(x['rate'] * p.discount_percentage * p.target_qty/ 100)
				alt_dis =copy.deepcopy(discount)
			frappe.errprint(discount)
			if x['item_code'] == min_amount_item and x ["item_code"] not in min_amount_list:
 				min_amount_list[min_amount_item] = alt_dis
 			frappe.errprint(min_amount_list)
		
	else:
		for x in doc['items']:
			if x['brand'] == tgt:
				temp_dict[x['item_code']] = x['rate']
		
		min_amount_item =min(temp_dict, key=temp_dict.get)

		for x in doc['items']:
			if x['item_code'] == min_amount_item and x['qty'] <=p.target_qty:
				discount = float(x['rate'] * p.discount_percentage * x ['qty']/ 100)
				alt_dis =copy.deepcopy(discount)
				frappe.errprint(discount)
				frappe.errprint(alt_dis)
			elif x['item_code'] == min_amount_item and x['qty'] > p.target_qty:
				discount = float(x['rate'] * p.discount_percentage * p.target_qty/ 100)
				alt_dis =copy.deepcopy(discount)
			frappe.errprint('target is brand')	
			frappe.errprint(discount)
			if x['item_code'] == min_amount_item and x ["item_code"] not in min_amount_list:
 				min_amount_list[min_amount_item] = alt_dis
 			# elif x['item_code'] == min_amount_item and x ["item_code"] in min_amount_list:
 			# 	min_amount_list[min_amount_item] = alt_dis + min_amount_list.get(min_amount_item,0)

		# min_amount_list[min_amount_item] =alt_dis

@frappe.whitelist()
def type_query(doctype, txt, searchfield, start, page_len, filters):
	query = frappe.db.sql(""" select name from  tabDocType where name = "Brand" or name = "Item Group" """)
	return query
