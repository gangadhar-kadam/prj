wn.module_page["Emails"] = [
	{
		title: wn._("Top"),
		top: true,
		icon: "icon-copy",
		items: [
			{
				label: wn._("Inbox"),
				description : wn._("Emails in Gmail Inbox."),
				doctype:"Email Inbox"
			},
			{
				label: wn._("Compose Mail"),
				description: wn._("For Composing new Mail "),
				doctype:"Compose Mail"
			},
			{
				label: wn._("Sent Mail"),
				description: wn._("Emails in Gmail Inbox."),
				doctype:"Sent Mail"
			},
		]
	},
]

pscript['onload_emails'] = function(wrapper) {
	wn.views.moduleview.make(wrapper, "Emails");
}

