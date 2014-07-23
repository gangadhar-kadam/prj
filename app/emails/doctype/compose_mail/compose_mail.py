# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.utils.email_lib import sendmail
# from core.doctype.communication.communication import make
from webnotes.model.doc import Document
from webnotes.sessions import Session
from core.doctype.communication.communication import make
# from webnotes.sessions import user


class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl


	def save_as_draft(self):
		webnotes.errprint("in the save_as_draft")
		self.doc.flag='Draft'
		self.doc.save()
		# pass

	#def add_attachment(self):
		#webnotes.errprint("in the add")
				# pass		
	def send_fin(self):
		#webnotes.errprint("in the py file")
		self.doc.flag='Sent'
		self.doc.save()
		webnotes.conn.sql("""Update `tabCompose Mail` set docstatus='2' where name='%s'"""%(self.doc.name))
		webnotes.conn.sql('commit')
		self.doc.docstatus=2
		return "hi"


# @webnotes.whitelist()
# def save_as_draft():
# 	webnotes.errprint("in the save_as_draft")
# 	self.doc.flag='Draft'
# 	self.doc.save()




