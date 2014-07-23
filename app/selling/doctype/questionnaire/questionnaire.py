# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl


	def get_address_details(self):
		#webnotes.errprint("in the getaddr")
		ret = {}
		det = webnotes.conn.sql("""select address_line1,address_line2,city,state,pincode,country,email_id,phone 
			from `tabAddress` where lead = %s""", self.doc.lead_name,debug=1)
		if det:
			ret = {
				'address_line1': det and det[0][0] or '',
				'address_line2': det and det[0][1] or '',
				'city': det and det[0][2] or '',
				'state': det and det[0][3] or '',
				'pincode': det and det[0][4] or '',
				'country': det and det[0][5] or '',
				'email':det and det[0][6] or '',
				'phone' :det and det[0][7] or ''
			}
		return ret

	def on_update(self):
		webnotes.conn.sql("""Update `tabOpportunity` 
			set questionnaire='%s' where opportunity_ref='%s' """%(self.doc.name,self.doc.opportunity_ref))
		webnotes.conn.commit()
