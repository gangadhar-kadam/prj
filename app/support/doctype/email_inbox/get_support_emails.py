#opyright (c) 2013, Web notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.utils import cstr, cint, decode_dict, today
from webnotes.utils.email_lib import sendmail		
from webnotes.utils.email_lib.receive2 import IMAPMailbox
from core.doctype.communication.communication import make
from webnotes.model.doc import Document
from webnotes.sessions import Session

import webnotes.profile
from webnotes import conf
# from webnotes.sessions import session

class SupportEMailbox(IMAPMailbox):
	def setup(self, args=None):

		self.m_settings = args or webnotes._dict({
			# "use_ssl": self.email_settings.support_use_ssl,
			# "host": self.email_settings.support_host,
			"username": res[0][0],
			"access_token": res[0][1]
		})
		# print 'self.settings.username'+self.m_settings.username
		# print 'self.settings.access_token'+self.m_settings.access_tok

	def process_message(self, mail,email_id,email_uid,email_type):
		thread_id = mail.get_thread_id()
		# print email_type
		new_email = False
		print 'in process_message'
		# print email_type

		if not (thread_id and webnotes.conn.exists("Email Inbox", thread_id)):
			new_email = True
		# print 'mail.subject'
		if email_type =='Inbox':
			print "in the if Inbox"
			email = add_email_communication(mail.subject, mail.content, mail.from_email,mail.date,email_id,email_uid,
			docname=None if new_email else thread_id, mail=mail)
		else:
			print "in the Sent"
			sent_email = add_sent_email_communication(mail.subject, mail.content, mail.from_email,mail.date,email_id,email_uid,
			docname=None if new_email else thread_id, mail=mail)
	
	def send_auto_reply(self, d):
		signature = self.email_settings.fields.get('support_signature') or ''
		response = self.email_settings.fields.get('support_autoreply') or ("""
A new Ticket has been raised for your query. If you have any additional information, please
reply back to this mail.
		
We will get back to you as soon as possible
----------------------
Original Query:

""" + d.description + "\n----------------------\n" + cstr(signature))

		sendmail(\
			recipients = [cstr(d.raised_by)], \
			sender = cstr(self.email_settings.fields.get('support_email')), \
			subject = '['+cstr(d.name)+'] ' + cstr(d.subject), \
			msg = cstr(response))
			
def get_support_emails():
	print 'in get support email'
	#if cint(webnotes.conn.get_value('Email Settings', None, 'sync_support_mails')):
	print 'in if loop'
	SupportEMailbox()
		
def add_email_communication(subject, content, sender, email_date,email_id,email_uid,docname=None, mail=None):

	print 'in email communtn method'
	print subject
	print"------------------------------------------------------"
	print sender
	print"------------------------------------------------------"
	print content
	print"------------email from profile------------------------------------------"
	# print 'mail.content_type'
	# print mail.content_type
	# email_name = webnotes.conn.get("Profile", {"email": email})
	# print email_name
	if docname:
		email = webnotes.bean("Email Inbox", docname)
		#email.doc.status = 'Open'
		email.ignore_permissions = True
		email.doc.save()
	else:

		email = webnotes.bean([decode_dict({
			"doctype":"Email Inbox",
			"description": content,
			"subject": subject,
			"raised_by": sender,
			"content_type": mail.content_type if mail else None,
			"status": "Open",
			"owner":email_id,
			"email_date":email_date,
			"email_uid":email_uid,
			"Flag":"Unread"
			
		})])
		email.ignore_permissions = True
		email.insert()
		print 'email object'
		print email.doc.name	
	
	make(content=content, sender=sender, subject = subject,
		doctype="Email Inbox", name=email.doc.name,
		date=mail.date if mail else today(), sent_or_received="Received")

	if mail:
		print "in the mail"
		mail.save_attachments_in_doc(email.doc)
		
	return email



			
def add_sent_email_communication(subject, content, sender, email_date,email_id,email_uid,docname=None, mail=None):

	print 'in sent  email communtn method'
	print subject
	print"------------------------------------------------------"
	print sender
	print"------------------------------------------------------"
	print content
	print"-----------sent email from profile------------------------------------------"
	print 'mail.content_type'
	print mail.content_type
	print email_id
	print email_date
	print email_uid

	# email_name = webnotes.conn.get("Profile", {"email": email})
	# print email_name
	if docname:
		print "in the if"
		email = webnotes.bean("Sent Mail", docname)
		# email.doc.status = 'Open'
		email.ignore_permissions = True
		email.doc.save()
	else:
		print "elase"
		try:
			email = webnotes.bean([decode_dict({
				"doctype":"Sent Mail",
				"description": content,
				"subject": subject,
				"raised_by": sender,
				"content_type": mail.content_type if mail else None,
				"owner":email_id,
				"email_date":email_date,
				"email_uid":email_uid,
				"Flag":"Unread"
				
		})])
		except Exception, e:
			print e
			raise
		# print "after"
		# print email
		# print email.name

		email.ignore_permissions = True
		email.insert()
		print 'email object'
		print email.doc.name	
	
	make(content=content, sender=sender, subject = subject,
		doctype="Sent Mail", name=email.doc.name,
		date=mail.date if mail else today(), sent_or_received="Sent")

	if mail:
		print "in the mail"
		mail.save_attachments_in_doc(email.doc)
		
	return email


