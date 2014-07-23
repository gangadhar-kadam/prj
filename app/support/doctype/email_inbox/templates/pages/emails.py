# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.utils import cint, formatdate

no_cache = True

def get_context():
	return {
		"title": "My Emails",
		"method": "support.doctype.email_inbox.templates.pages.emails.get_emails",
		"icon": "icon-ticket",
		"empty_list_message": "No Emails Raised",
		"page": "email"
	}

@webnotes.whitelist()
def get_emails(start=0):
	emails = webnotes.conn.sql("""select name, subject, status, creation 
		from `tabEmail Inbox` where raised_by=%s 
		order by modified desc
		limit %s, 20""", (webnotes.session.user, cint(start)), as_dict=True)
	for t in emails:
		t.creation = formatdate(t.creation)
	
	return emails
	
@webnotes.whitelist()
def make_new_email(subject, message):
	if not (subject and message):
		raise webnotes.throw(_("Please write something in subject and message!"))
		
	from support.doctype.email_inbox.get_support_emails import add_email_communication
	email = add_email_communication(subject, message, webnotes.session.user)
	
	return email.doc.name