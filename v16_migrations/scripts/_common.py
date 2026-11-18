"""Shared helpers for the frappe fork-data export / trim / import scripts.

Written to run unchanged on every Frappe version from v12 (Python 3.6) to v16,
so only plain SQL against information_schema is used for schema checks.

Run every script from the bench's `sites` directory with the bench's Python:

    cd ~/frappe-bench/sites
    ../env/bin/python /path/to/v16_migrations/scripts/<script>.py --site <site> ...
"""
from __future__ import print_function, unicode_literals

import datetime
import decimal
import json
import os
import re

# Columns that exist only because of the prime-erp frappe fork's DocType JSON
# and would be orphaned (and later trimmed) once upstream Frappe replaces the fork.
# `custom_date_filters_display` (HTML) is not listed: it has no column.
FORK_COLUMNS = [
	("Auto Email Report", "naming"),
	("Auto Email Report", "custom_date_filters"),
]

# The frappe fork changes no column types, so nothing is narrowed by upstream
# (the erpnext tool's TYPE_CHANGED_COLUMNS / fit_narrowed_columns.py have no
# frappe equivalent).
TYPE_CHANGED_COLUMNS = []

# Standard columns that never correspond to a DocField.
BASE_COLUMNS = {
	"name", "creation", "modified", "modified_by", "owner", "docstatus", "idx",
	"parent", "parentfield", "parenttype", "doctype",
}

EXPORT_SUFFIX = ".json"


def connect(site, sites_path="."):
	import frappe

	frappe.init(site=site, sites_path=sites_path)
	frappe.connect()
	return frappe


def table(doctype):
	return "tab" + doctype


def qi(identifier):
	"""Quote a MariaDB identifier."""
	return "`" + identifier.replace("`", "``") + "`"


def table_columns(frappe, doctype):
	"""{column_name: column_type} straight from information_schema."""
	rows = frappe.db.sql(
		"""select column_name, column_type from information_schema.columns
		where table_schema = database() and table_name = %s""",
		(table(doctype),),
	)
	return {r[0]: r[1] for r in rows}


def table_exists(frappe, doctype):
	return bool(frappe.db.sql(
		"""select 1 from information_schema.tables
		where table_schema = database() and table_name = %s""",
		(table(doctype),),
	))


def meta_has_field(frappe, doctype, fieldname):
	meta = frappe.get_meta(doctype, cached=False)
	return bool(meta.get_field(fieldname))


def meta_fieldnames_with_value(frappe, doctype):
	meta = frappe.get_meta(doctype, cached=False)
	return set(meta.get_fieldnames_with_value())


def find_orphan_columns(frappe):
	"""Columns present in a table but absent from the current DocType meta
	(core JSON + Custom Fields). Mirrors frappe.model.meta.trim_table()."""
	orphans = []
	for dt in frappe.get_all("DocType", filters={"issingle": 0}, fields=["name"]):
		doctype = dt.name if hasattr(dt, "name") else dt["name"]
		if not table_exists(frappe, doctype):
			continue
		try:
			meta = frappe.get_meta(doctype, cached=False)
			if getattr(meta, "is_virtual", 0):
				continue
			fields = set(meta.get_fieldnames_with_value())
		except Exception as e:  # broken meta on a half-upgraded site
			print("  ! skipping {}: {}".format(doctype, e))
			continue
		for col in table_columns(frappe, doctype):
			if col in BASE_COLUMNS or col.startswith("_") or col in fields:
				continue
			orphans.append((doctype, col))
	return orphans


def export_filename(doctype, fieldname):
	safe = re.sub(r"[^A-Za-z0-9_]+", "_", doctype).strip("_").lower()
	return "{}--{}{}".format(safe, fieldname, EXPORT_SUFFIX)


def to_json_value(value):
	if isinstance(value, decimal.Decimal):
		return str(value)
	if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
		return value.isoformat()
	if isinstance(value, datetime.timedelta):
		return str(value)
	if isinstance(value, bytes):
		return value.decode("utf-8", "replace")
	return value


def read_exports(directory):
	for fn in sorted(os.listdir(directory)):
		if fn.endswith(EXPORT_SUFFIX) and "--" in fn:
			path = os.path.join(directory, fn)
			with open(path) as f:
				yield path, json.load(f)


def count_non_null(frappe, doctype, fieldname):
	return frappe.db.sql(
		"select count(*) from {} where {} is not null".format(qi(table(doctype)), qi(fieldname))
	)[0][0]
