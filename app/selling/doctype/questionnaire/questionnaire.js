cur_frm.cscript.is_customer = function(doc,cdt,cdn){
	//console.log(doc.is_customer);
	if(doc.is_customer==1){
	console.log("doc.is_customer");
	set_field_permlevel('client_name',0);
	set_field_permlevel('lead_name', 1);
	refresh_field('client_name');
	refresh_field('lead_name');
	}
	else{
	 console.log("not doc.is_customer");
        set_field_permlevel('client_name',1); 
        set_field_permlevel('lead_name', 0);   
        refresh_field('client_name');
        refresh_field('lead_name');

	}	
}
cur_frm.cscript.onload = function(doc, dt, dn){
  console.log("in the onload");
  return get_server_fields('get_address_details','','',doc,dt,dn);
}
