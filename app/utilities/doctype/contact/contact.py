# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.utils import cstr, extract_email_id

from utilities.transaction_base import TransactionBase
import pickle

import atom.data
import gdata.data
import gdata.contacts.client
import gdata.contacts.data
from gdata.auth import OAuthSignatureMethod, OAuthToken, OAuthInputParams
import pickle
import urlparse
import gdata.gauth
import gdata.contacts.client
import urllib2

class DocType(TransactionBase):
	def __init__(self, doc, doclist=[]):
		self.doc = doc
		self.doclist = doclist


	def on_update(self):
		prepare_data(self.doc)



	def on_communication(self, comm):
		if webnotes.conn.get_value("Profile", extract_email_id(comm.sender), "user_type")=="System User":
			status = "Replied"
		else:
			status = "Open"
			
		webnotes.conn.set(self.doc, 'status', status)


		

	def autoname(self):
		# concat first and last name
		self.doc.name = " ".join(filter(None, 
			[cstr(self.doc.fields.get(f)).strip() for f in ["first_name", "last_name"]]))
		
		# concat party name if reqd
		for fieldname in ("customer", "supplier", "sales_partner"):
			if self.doc.fields.get(fieldname):
				self.doc.name = self.doc.name + "-" + cstr(self.doc.fields.get(fieldname)).strip()
				break
		
	def validate(self):
		self.set_status()
		self.validate_primary_contact()

	def validate_primary_contact(self):
		if self.doc.is_primary_contact == 1:
			if self.doc.customer:
				webnotes.conn.sql("update tabContact set is_primary_contact=0 where customer = '%s'" % (self.doc.customer))
			elif self.doc.supplier:
				webnotes.conn.sql("update tabContact set is_primary_contact=0 where supplier = '%s'" % (self.doc.supplier))	
			elif self.doc.sales_partner:
				webnotes.conn.sql("update tabContact set is_primary_contact=0 where sales_partner = '%s'" % (self.doc.sales_partner))
		else:
			if self.doc.customer:
				if not webnotes.conn.sql("select name from tabContact where is_primary_contact=1 and customer = '%s'" % (self.doc.customer)):
					self.doc.is_primary_contact = 1
			elif self.doc.supplier:
				if not webnotes.conn.sql("select name from tabContact where is_primary_contact=1 and supplier = '%s'" % (self.doc.supplier)):
					self.doc.is_primary_contact = 1
			elif self.doc.sales_partner:
				if not webnotes.conn.sql("select name from tabContact where is_primary_contact=1 and sales_partner = '%s'" % (self.doc.sales_partner)):
					self.doc.is_primary_contact = 1

	def on_trash(self):
		webnotes.conn.sql("""update `tabSupport Ticket` set contact='' where contact=%s""",
			self.doc.name)



def prepare_data(self):
	""" prepare dict """
	if self.last_name:
		name = self.first_name 
		# name = self.first_name + ' ' + self.last_name
		last_name = self.last_name
	else:
		name = self.first_name
	info = {'full_name': name+' '+last_name,'name':name,'last_name':last_name, 'email':self.email_id, 'phone': self.phone, 'id':self.contact_id}
	webnotes.errprint("contct_id")
	webnotes.errprint(self.contact_id)
	if self.contact_id:
		update_contact(info)
	else:
		create_contact_on_google(self, info)

def create_contact_on_google(self, info):

	client=get_client_obj()

	#create contact in google
	new_contact = gdata.contacts.data.ContactEntry()

	# Set the contact's name.
	new_contact.name = gdata.data.Name( given_name=gdata.data.GivenName(text=info['name']), family_name=gdata.data.FamilyName(text=info['last_name']),
		full_name=gdata.data.FullName(text=info['full_name']))

	new_contact.content = atom.data.Content(text='Notes')

	# Set the contact's email addresses.
	new_contact.email.append(gdata.data.Email(address=info['email'],  primary='true', rel=gdata.data.WORK_REL, display_name=info['name']))

	# Set the contact's phone numbers.
	new_contact.phone_number.append(gdata.data.PhoneNumber(text=info['phone'], rel=gdata.data.WORK_REL, primay='true'))

	contact_entry = client.CreateContact(new_contact)
	webnotes.errprint("Contact's ID: %s" % contact_entry.id.text)

	webnotes.conn.set_value("Contact",self.name,"contact_id", contact_entry.id.text)


def update_contact(info):
	webnotes.errprint("in the update")
	client=get_client_obj()
	url = urllib2.unquote(info['id'].replace('base','full'))
	webnotes.errprint(url)
	contact_entry = client.GetContact(url)
	contact_entry.name.full_name.text = info['full_name']
	contact_entry.name.given_name.text = info['name']
	contact_entry.name.family_name.text = info['last_name']
	# contact_entry.email=info['email']
	# contact_entry.phone_number=info['phone']
	try:
		updated_contact = client.Update(contact_entry)
		webnotes.errprint('Updated: %s' % updated_contact.updated.text)

	except  gdata.client.RequestError, e:
		if e.status == 412:
			pass


def get_client_obj():
	user_agent='GContact'
	webnotes.errprint("in the get_client_obj")
	# with open(user_name+".pickle") as pickle_file:
	with open("client.pickle") as pickle_file:
		auth_token = pickle.load(pickle_file)
	client = gdata.contacts.client.ContactsClient(source=user_agent)
	auth_token.authorize(client)
	return client	

@webnotes.whitelist()
def read_contact():

	with open('client.pickle') as pickle_file:
		client = pickle.load(pickle_file)

	query = gdata.contacts.client.ContactsQuery(max_results=300, showdeleted='True', updated_min=None, updated_max=None)

	# to rerieve contacts from google
	feed = client.get_contacts(query=query)
	lst=[]
	for contact in feed.entry:
		try:
			contact_id=contact.id.text
			if contact.name:
				
				first_name=contact.name.given_name.text
				last_name=contact.name.family_name.text
				
			for email in contact.email:
				if email.primary and email.primary == 'true':
					e=email.address
					#webnotes.errprint(e)
			for phone_number in contact.phone_number:
				num=phone_number.text
			#lst.append(first_name+' '+last_name+'  id --- '+contact_id)
			contactlist=webnotes.conn.sql("select name from `tabContact`", as_list=1)
			#webnotes.errprint(contactlist)
			
			fname=[]
			fupdate=[]
			if contact.name:
				fname.append(contact.name.full_name.text)
				#webnotes.errprint(fname)
				qry= webnotes.conn.sql("select modified from `tabContact` where name= %s ",(contact.name.full_name.text) , as_list=1)
				fupdate.append(contact.updated.text)
				if fname not in contactlist:
					webnotes.errprint("in document")
					d = Document("Contact")
					d.contact_id=contact_id
					d.first_name=first_name
					d.last_name=last_name
					d.phone=num
					d.email_id=e
					d.save()
					webnotes.errprint(d.name)
				elif fupdate > qry:
					webnotes.errprint("in contact update")
					r=webnotes.conn.sql("update `tabContact` set first_name=%s, last_name=%s, email_id=%s, phone=%s where name=%s",(contact.name.given_name.text,contact.name.family_name.text,e,num,contact.name.full_name.text))
					webnotes.errprint("contact Updated...")
		except gdata.client.Unauthorized, err:
			webnotes.errprint(err.message)
		#webnotes.errprint(lst)		
