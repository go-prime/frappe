from __future__ import unicode_literals
from frappe import _

def get_data():
	import frappe
	tiles = frappe.get_list("Module Tile", 
		ignore_permissions=True, 
		filters={'module': 'Tools'},
		order_by="tile_index asc")
	if tiles:
		return [frappe.get_doc("Module Tile", tile['name']).as_module_dict() for tile in tiles]

	return [
		{
			"label": _("Tools"),
			"icon": "octicon octicon-briefcase",
			"items": [
				{
					"type": "doctype",
					"name": "ToDo",
					"label": _("To Do"),
					"description": _("Documents assigned to you and by you."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Event",
					"label": _("Calendar"),
					"link": "List/Event/Calendar",
					"description": _("Event and other calendars."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Note",
					"description": _("Private and public Notes."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "File",
					"label": _("Files"),
				},
				{
					"type": "page",
					"label": _("Chat"),
					"name": "chat",
					"description": _("Chat messages and other notifications."),
					"data_doctype": "Communication"
				},
				{
					"type": "page",
					"label": _("Activity"),
					"name": "activity",
					"description": _("Activity log of all users."),
				},
			]
		},
		{
			'label': _('Email'),
			'items': [
				{
					"type": "doctype",
					"name": "Newsletter",
					"description": _("Newsletters to contacts, leads."),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Email Group",
					"description": _("Email Group List"),
				},
			]
		}
	]
