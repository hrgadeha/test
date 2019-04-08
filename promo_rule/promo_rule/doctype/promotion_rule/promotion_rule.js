// Copyright (c) 2018, taherkhalil52@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Promotion rule', {
	refresh: function(frm) {
		frm.fields_dict["base_type"].get_query = function(doc){
			return {
				query:"promo_rule.promo_rule.doctype.promotion_rule.promotion_rule.type_query" 
			}
		},
		frm.fields_dict["target_type"].get_query = function(doc){
			return {
				query:"promo_rule.promo_rule.doctype.promotion_rule.promotion_rule.type_query" 
			}
		}		

	}

});
