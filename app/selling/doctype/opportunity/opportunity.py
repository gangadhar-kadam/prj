# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes

from webnotes.utils import cstr, cint
from webnotes.model.doc import Document, make_autoname
from utilities.transaction_base import get_address_display 
from webnotes.model.bean import getlist
from webnotes import msgprint, _

from webnotes.model.doc import addchild	
from utilities.transaction_base import TransactionBase

class DocType(TransactionBase):
	def __init__(self,doc,doclist):
		self.doc = doc
		self.doclist = doclist
		self.fname = 'enq_details'
		self.tname = 'Opportunity Item'
		
		self._prev = webnotes._dict({
			"contact_date": webnotes.conn.get_value("Opportunity", self.doc.name, "contact_date") if \
				(not cint(self.doc.fields.get("__islocal"))) else None,
			"contact_by": webnotes.conn.get_value("Opportunity", self.doc.name, "contact_by") if \
				(not cint(self.doc.fields.get("__islocal"))) else None,
		})
		
	def get_item_details(self, item_code):
		item = webnotes.conn.sql("""select item_name, stock_uom, description_html, description, item_group, brand
			from `tabItem` where name = %s""", item_code, as_dict=1)
		ret = {
			'item_name': item and item[0]['item_name'] or '',
			'uom': item and item[0]['stock_uom'] or '',
			'description': item and item[0]['description_html'] or item[0]['description'] or '',
			'item_group': item and item[0]['item_group'] or '',
			'brand': item and item[0]['brand'] or ''
		}
		return ret

	def get_cust_address(self,name):
		details = webnotes.conn.sql("select customer_name, address, territory, customer_group from `tabCustomer` where name = '%s' and docstatus != 2" %(name), as_dict = 1)
		if details:
			ret = {
				'customer_name':	details and details[0]['customer_name'] or '',
				'address'	:	details and details[0]['address'] or '',
				'territory'			 :	details and details[0]['territory'] or '',
				'customer_group'		:	details and details[0]['customer_group'] or ''
			}
			# ********** get primary contact details (this is done separately coz. , in case there is no primary contact thn it would not be able to fetch customer details in case of join query)

			contact_det = webnotes.conn.sql("select contact_name, contact_no, email_id from `tabContact` where customer = '%s' and is_customer = 1 and is_primary_contact = 'Yes' and docstatus != 2" %(name), as_dict = 1)

			ret['contact_person'] = contact_det and contact_det[0]['contact_name'] or ''
			ret['contact_no']		 = contact_det and contact_det[0]['contact_no'] or ''
			ret['email_id']			 = contact_det and contact_det[0]['email_id'] or ''
		
			return ret
		else:
			msgprint("Customer : %s does not exist in system." % (name))
			raise Exception
			
	def on_update(self):
  		self.doc.opportunity_ref=self.doc.name
		self.add_calendar_event()
		self.get_leadcomm_detail()
		self.set_addr()
		self.doc.save()

	def autoname(self):
		self.doc.name = make_autoname('OPPT.######')
#		if self.doc.lead:
#			address_details = webnotes.conn.sql("select address_title, address_type from tabAddress where lead = '%s'"%(self.doc.lead),as_list=1)
#			if address_details:
#				for address in address_details:
#					if address[1] == 'Job Location':
#						self.doc.name = make_autoname(self.set_addr())
#					else:
						# self.doc.name = make_autoname('OPPT.#######')
#						self.doc.name = make_autoname(address[1] + '-'+ address[0])
#			else:
#				self.doc.name = make_autoname('OPPT.######')

	def get_leadcomm_detail(self):
		check_communication_exist=webnotes.conn.sql("select name from `tabCommunication` where parent='%s'"%(self.doc.name))
		if not check_communication_exist:
			if self.doc.lead:
				res=webnotes.conn.sql("select name from `tabCommunication` where parent='%s'"%(self.doc.lead))
				for name in res:
					#webnotes.errprint(name)
				 	content=webnotes.conn.sql("select * from `tabCommunication` where name='%s'"%(name[0]),as_dict=1)
					if content:
						for data in content:
							d=Document('Communication')
							d.content=data.content
							d.parent=self.doc.name
							d.parenttype='Opportunity'
							d.idx=data.idx
							d.docstatus=data.docstatus
							d.parentfield=data.parentfield
							d.sender=data.sender
							d.recipients=data.recipients
							d.sent_or_received=data.sent_or_received
							d.communication_medium=data.communication_medium
							d.subject=data.subject
							d.save()

	def set_addr(self):
		if self.doc.lead:
			job_location=webnotes.conn.sql("select name,address_type from `tabAddress` where lead='%s'"%(self.doc.lead),as_list=1)
			if job_location:
				for address in job_location:
					if address[1]=='Job Location':
						self.doc.customer_address=address[0]
						self.doc.address_display=get_address_display(self.doc.customer_address)
					else:
						self.doc.customer_address=address[0]
						self.doc.address_display=get_address_display(self.doc.customer_address)	

			return self.doc.address_display

	def get_stages_labels(self):
		stages_list=['RFR','CRFR','RFL','CRFL']
		for stg in stages_list:
			ch = addchild(self.doc, 'stages_history','Stages History', self.doclist)
			ch.type=stg
			# ch.date=today
			#webnotes.errprint(ch)




	def add_calendar_event(self, opts=None, force=False):
		if not opts:
			opts = webnotes._dict()
		
		opts.description = ""
		
		if self.doc.customer:
			if self.doc.contact_person:
				opts.description = 'Contact '+cstr(self.doc.contact_person)
			else:
				opts.description = 'Contact customer '+cstr(self.doc.customer)
		elif self.doc.lead:
			if self.doc.contact_display:
				opts.description = 'Contact '+cstr(self.doc.contact_display)
			else:
				opts.description = 'Contact lead '+cstr(self.doc.lead)
				
		opts.subject = opts.description
		opts.description += '. By : ' + cstr(self.doc.contact_by)
		
		if self.doc.to_discuss:
			opts.description += ' To Discuss : ' + cstr(self.doc.to_discuss)
		
		super(DocType, self).add_calendar_event(opts, force)

	def validate_item_details(self):
		if not getlist(self.doclist, 'enquiry_details'):
			msgprint("Please select items for which enquiry needs to be made")
			raise Exception

	def validate_lead_cust(self):
		if self.doc.enquiry_from == 'Lead' and not self.doc.lead:
			msgprint("Lead Id is mandatory if 'Opportunity From' is selected as Lead", raise_exception=1)
		elif self.doc.enquiry_from == 'Customer' and not self.doc.customer:
			msgprint("Customer is mandatory if 'Opportunity From' is selected as Customer", raise_exception=1)

	def validate(self):
		self.set_status()
		self.validate_item_details()
		self.validate_uom_is_integer("uom", "qty")
		self.validate_lead_cust()
		
		from accounts.utils import validate_fiscal_year
		validate_fiscal_year(self.doc.transaction_date, self.doc.fiscal_year, "Opportunity Date")

	def on_submit(self):
		if self.doc.lead:
			webnotes.bean("Lead", self.doc.lead).get_controller().set_status(update=True)
	
	def on_cancel(self):
		if self.has_quotation():
			webnotes.throw(_("Cannot Cancel Opportunity as Quotation Exists"))
		self.set_status(update=True)
		
	def declare_enquiry_lost(self,arg):
		if not self.has_quotation():
			webnotes.conn.set(self.doc, 'status', 'Lost')
			webnotes.conn.set(self.doc, 'order_lost_reason', arg)
		else:
			webnotes.throw(_("Cannot declare as lost, because Quotation has been made."))

	def on_trash(self):
		self.delete_events()
		
	def has_quotation(self):
		return webnotes.conn.get_value("Quotation Item", {"prevdoc_docname": self.doc.name, "docstatus": 1})
		
@webnotes.whitelist()
def make_quotation(source_name, target_doclist=None):
	from webnotes.model.mapper import get_mapped_doclist
	
	def set_missing_values(source, target):
		quotation = webnotes.bean(target)
		quotation.run_method("onload_post_render")
		quotation.run_method("calculate_taxes_and_totals")
	
	doclist = get_mapped_doclist("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Quotation", 
			"field_map": {
				"enquiry_from": "quotation_to", 
				"enquiry_type": "order_type", 
				"name": "enq_no", 
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		}, 
		"Opportunity Item": {
			"doctype": "Quotation Item", 
			"field_map": {
				"client_name": "client_name", 
				"contact_person": "contact_person"
				# "uom": "stock_uom"
			},
			"add_if_empty": True
		}
	}, target_doclist, set_missing_values)
		
	return [d.fields for d in doclist]

@webnotes.whitelist()
def make_quetionnaire(source_name, target_doclist=None):
	#webnotes.errprint("in the make_quetionnaire")
	from webnotes.model.mapper import get_mapped_doclist
		
	doclist = get_mapped_doclist("Opportunity", source_name, 
		{"Opportunity": {
			"doctype": "Questionnaire",
			"field_map": {
				"lead": "lead_name",
				"customer_address": "site_address"
				},
			"validation": {
				"docstatus": ["=", 0]
			}
			

			}
		}, target_doclist)
		
	return [d if isinstance(d, dict) else d.fields for d in doclist]
