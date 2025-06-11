frappe.ui.form.on('Auto Email Report', {
	refresh: function(frm) {
		if(frm.doc.report_type !== 'Report Builder') {
			if(frm.script_setup_for !== frm.doc.report && !frm.doc.__islocal) {
				frappe.call({
					method:"frappe.desk.query_report.get_script",
					args: {
						report_name: frm.doc.report
					},
					callback: function(r) {
						frappe.dom.eval(r.message.script || "");
						frm.script_setup_for = frm.doc.report;
						frm.trigger('show_filters');
					}
				});
			} else {
				frm.trigger('show_filters');
			}
		}
		if(!frm.is_new()) {
			frm.add_custom_button(__('Download'), function() {
				var w = window.open(
					frappe.urllib.get_full_url(
						"/api/method/frappe.email.doctype.auto_email_report.auto_email_report.download?"
						+"name="+encodeURIComponent(frm.doc.name)));
				if(!w) {
					frappe.msgprint(__("Please enable pop-ups"));
					return;
				}
			});
			frm.add_custom_button(__('Send Now'), function() {
				frappe.call({
					method: 'frappe.email.doctype.auto_email_report.auto_email_report.send_now',
					args: {name: frm.doc.name},
					callback: function() {
						frappe.msgprint(__('Scheduled to send'));
					}
				});
			});
		} else {
			if(!frm.doc.user) {
				frm.set_value('user', frappe.session.user);
			}
			if(!frm.doc.email_to) {
				frm.set_value('email_to', frappe.session.user);
			}
		}
	},
	report: function(frm) {
		frm.set_value('filters', '');
	},
	show_filters: function(frm) {
		// Clear and build the main filters table
		var wrapper = $(frm.get_field('filters_display').wrapper);
		wrapper.empty();
		if(frm.doc.report_type === 'Custom Report' || (frm.doc.report_type !== 'Report Builder'
			&& frappe.query_reports[frm.doc.report]
			&& frappe.query_reports[frm.doc.report].filters)) {

			// make a table to show filters
			var table = $('<table class="table table-bordered" style="cursor:pointer; margin:0px;"><thead>\
				<tr><th style="width: 50%">'+__('Filter')+'</th><th>'+__('Value')+'</th></tr>\
				</thead><tbody></tbody></table>').appendTo(wrapper);
			$('<p class="text-muted small">' + __("Click table to edit") + '</p>').appendTo(wrapper);

			var filters = JSON.parse(frm.doc.filters || '{}');

			let report_filters;
			if (frm.doc.report_type === 'Custom Report'
				&& frappe.query_reports[frm.doc.reference_report]
				&& frappe.query_reports[frm.doc.reference_report].filters) {
				report_filters = frappe.query_reports[frm.doc.reference_report].filters;
			} else {
				report_filters = frappe.query_reports[frm.doc.report].filters;
			}

			if(report_filters && report_filters.length > 0) {
				frm.set_value('filter_meta', JSON.stringify(report_filters));
				if (frm.is_dirty()) {
					frm.save();
				}
			}

			var report_filters_list = [];
			$.each(report_filters, function(key, val){
				// Remove "Break" fieldtype from the filters
				if(val.fieldtype != 'Break') {
					report_filters_list.push(val);
				}
			});
			report_filters = report_filters_list;

			report_filters.forEach(function(f) {
				$('<tr><td>' + f.label + '</td><td>'+ frappe.format(filters[f.fieldname], f) +'</td></tr>')
					.appendTo(table.find('tbody'));
			});

			table.on('click', function() {
				var dialog = new frappe.ui.Dialog({
					fields: report_filters,
					primary_action: function() {
						var values = this.get_values();
						if(values) {
							this.hide();
							frm.set_value('filters', JSON.stringify(values));
							frm.trigger('show_filters');
						}
					}
				});
				dialog.show();
				dialog.set_values(filters);
			});

			// Populate dynamic date field selection for from/to date fields
			let date_fields = report_filters
				.filter(df => df.fieldtype === 'Date')
				.map(df => ({ label: df.label, value: df.fieldname }));
			frm.set_df_property('from_date_field', 'options', date_fields);
			frm.set_df_property('to_date_field', 'options', date_fields);
			frm.toggle_display('dynamic_report_filters_section', date_fields.length > 0);

			// *** New: Build the custom date filters table ***
			// This table will be rendered in the HTML field "custom_date_filters_display"
			// It lists each date field with a checkbox. When checked, the field's name is stored
			// in the text field "custom_date_filters" as a comma-separated list.
			var custom_wrapper = $(frm.get_field('custom_date_filters_display').wrapper);
			custom_wrapper.empty();
			if(date_fields.length > 0) {
				var custom_table = $('<table class="table table-bordered" style="cursor:pointer; margin:0px;"><thead>\
					<tr><th style="width: 50%">'+__('Field Name')+'</th><th>'+__('Include')+'</th></tr>\
					</thead><tbody></tbody></table>').appendTo(custom_wrapper);
				// Parse current custom_date_filters (assumed to be comma-separated)
				var custom_date_filters_list = frm.doc.custom_date_filters ? frm.doc.custom_date_filters.split(',') : [];
				date_fields.forEach(function(df) {
					var isChecked = custom_date_filters_list.indexOf(df.value) > -1;
					var row = $('<tr><td>' + df.label + '</td><td><input type="checkbox" data-field="'+ df.value +'" ' + (isChecked ? 'checked' : '') + '></td></tr>');
					custom_table.find('tbody').append(row);
				});
				// When any checkbox is changed, update the custom_date_filters text field
				custom_table.find('input[type="checkbox"]').on('change', function() {
					var selected = [];
					custom_table.find('input[type="checkbox"]').each(function() {
						if ($(this).is(':checked')) {
							selected.push($(this).attr('data-field'));
						}
					});
					frm.set_value('custom_date_filters', selected.join(','));
				});
			}
		}
	}
});
