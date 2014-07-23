cur_frm.cscript.send = function(doc,dt,dn) {
	//console.log("in send of the compose.js");
	get_server_fields('send_fin','','',doc,dt,dn);
	//console.log("after server")
	setTimeout(function(){cur_frm.cscript.send_email();},4000);
}		

cur_frm.cscript.send_email= function() {
	//console.log("in the send email of js");
	return wn.call({
		method:"core.doctype.communication.communication.make",
		args: {
			sender: [wn.user_info(user).fullname, wn.boot.profile.email],
			recipients:cur_frm.doc.to,
			subject: cur_frm.doc.subject,
			content: cur_frm.doc.content,
			doctype: cur_frm.doc.doctype,
			name:cur_frm.doc.name,
			// send_me_a_copy: form_values.send_me_a_copy,
			send_email:"True",
			// print_html: print_html,
			communication_medium:"Email" ,
			sent_or_received:"Sent"
			// attachments: selected_attachments
		},
		// btn: btn,
		callback: function(r) {
			if(!r.exc) {
				// if(form_values.send_email)
					msgprint("Email sent to ");
				// me.dialog.hide();
				// cur_frm.reload_doc();
			} else {
				// msgprint("There were errors while sending email. Please try again.")
			}
		}
	});
}

// cur_frm.cscript.save_as_draft= function() {
// 	console.log("in the send email of js");
// 	return wn.call({
// 		method:"emails.doctype.compose_mail.compose_mail.save_as_draft",

// 	});
// }
