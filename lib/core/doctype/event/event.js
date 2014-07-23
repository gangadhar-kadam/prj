// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt 

cur_frm.cscript.repeat_on = function(doc, cdt, cdn) {
	if(doc.repeat_on==="Every Day") {
		$.each(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], function(i,v) {
			cur_frm.set_value(v, 1);
		})
	}
}

cur_frm.cscript.refresh = function(doc, cdt, cdn) {

}


cur_frm.cscript.generate_credentials = function(doc, dt ,dn){
	return wn.call({
		method: "core.doctype.event.event.sync_google_event",
		args: {
			"client_id":doc.client_id, 
			"client_secret":doc.client_secret, 
			"app_name":doc.app_name,
			"verification_code": cur_frm.doc.token_for_calendar
		},
		callback:function(r){
			cur_frm.set_value('credentails', r.message.final_credentials)
			refresh_field('credentails')
		}
	});
}

