# prime-erp frappe → upstream Frappe v16 migration

This is the frappe counterpart of `erpnext/v16_migration`. Run the two together, because they share one export directory. This folder isn't part of the `frappe` Python package, so nothing in it runs on `bench migrate` while it lives in this repo.

```
v16_migrations/
  goprime_erp/custom/*.json   Custom Fields + Property Setters → copy into goprime/goprime_erp/custom/ on v16
  scripts/
    export_fork_data.py       dump fork-only / orphan column data to JSON (never overwrites)
    trim_fork_columns.py      drop exported orphan columns (dry run unless --execute)
    import_fork_data.py       write the data back on v16 (dry run unless --execute, idempotent)
```

The scripts are the erpnext tool's scripts with frappe's column list in `_common.py`. There is no `fit_narrowed_columns.py`, because the frappe fork changes no column types.

Run every script from the bench's `sites` directory with the bench's Python:

```bash
cd ~/frappe-bench/sites
../env/bin/python /path/to/v16_migrations/scripts/<script>.py --site SITE ...
```

## What the fork changes in the database

The fork was compared against upstream `v12.3.0`, the version it reports. Only two DocType JSONs differ. The fork adds no DocTypes, no patches, and no code that creates fields at runtime.

| DocType | Change | Handled by |
|---|---|---|
| Auto Email Report | new field `naming` (Data, reqd, set only once): the fork names reports from it | Custom Field + export/import |
| Auto Email Report | new field `custom_date_filters` (Text, hidden): report filters set to today on each send | Custom Field + export/import |
| Auto Email Report | new field `custom_date_filters_display` (HTML) | Custom Field (no column, so no data) |
| Auto Email Report | `naming` first, the two date-filter fields after `filter_meta` | `field_order` Property Setter |
| Email Account | `enable_automatic_linking` description shortened (removed the erpnext.com link) | not carried over: v16 has no description there and uses `documentation_url` instead |

v16's Auto Email Report has none of these fieldnames, so the Custom Fields don't clash. The `field_order` setter is built from v16's own order. v16 places any field it doesn't list by `insert_after`, so future upstream fields still show up.

## Runbook

Each step below slots into the same-numbered step of the erpnext runbook. Use the **same** `--out` / `--in` directory for both tools. The export file names (`auto_email_report--naming.json`, …) don't collide with erpnext's.

### 1. Export on the fork (prime-erp frappe still installed)

```bash
../env/bin/python .../v16_migrations/scripts/export_fork_data.py --site SITE --out ~/fork-export
```

### 2. Switch frappe to upstream v12, together with erpnext

```bash
cd ~/frappe-bench/apps/frappe
git remote add upstream https://github.com/frappe/frappe.git
git fetch upstream version-12
git checkout -B version-12 upstream/version-12
cd ~/frappe-bench && bench --site SITE migrate && bench build
```

### 3. Export orphans

The erpnext tool's `--orphans-only` run covers the whole site, frappe tables included, so one run of either tool is enough. Columns already exported in step 1 are skipped.

### 4. Trim

```bash
../env/bin/python .../v16_migrations/scripts/trim_fork_columns.py --site SITE --in ~/fork-export            # review
../env/bin/python .../v16_migrations/scripts/trim_fork_columns.py --site SITE --in ~/fork-export --execute
```

Either tool's trim works on every export in the directory, so this does the same thing as the erpnext trim. Run one of them.

### 5. Upgrade to v16

Nothing extra for frappe. Follow the erpnext runbook.

### 6. Install the customisations

Copy `goprime_erp/custom/auto_email_report.json` into `goprime/goprime_erp/custom/` on goprime's v16 branch, alongside the erpnext files, then run `bench --site SITE migrate`.

### 7. Import

```bash
../env/bin/python .../v16_migrations/scripts/import_fork_data.py --site SITE --in ~/fork-export            # review counts
../env/bin/python .../v16_migrations/scripts/import_fork_data.py --site SITE --in ~/fork-export --execute
../env/bin/python .../v16_migrations/scripts/import_fork_data.py --site SITE --in ~/fork-export            # should show 0 to write
```

Use `--only "Auto Email Report.naming"` (repeatable) to limit the import to frappe's columns. Without it, the import restores every export in the directory, erpnext's included, which is harmless because the import is idempotent.

## Behaviour notes

- **Existing report names don't change.** The scripts never touch `name`. `naming` is only written back onto rows matched by name.
- **`naming` is required.** In step 1, if the `naming` count is lower than the number of Auto Email Reports, those reports were created before the fork added the field. After the import they will fail validation on their next save. Fill them on v16 with:

  ```sql
  update `tabAuto Email Report` set naming = name where naming is null;
  ```
- **Only the schema and data move.** The fork's Python code that uses these fields isn't carried over. On v16, goprime has to provide it, for example with `override_doctype_class`:
  - `autoname` from `naming`: upstream v16 names reports from `report` and still adds a number to duplicate names.
  - `custom_date_filters` handling in `prepare_dynamic_filters`, plus the JS that fills it in.
- **Other fork code is out of scope here.** That includes naming-series mapping in `frappe/model/naming.py`, the `modified_by` override in `document.py`, `frappe.read_only_mode`, desk/list UI, and the scheduler moves. None of it stores data in its own columns. `Naming Series Mapping` is a goprime DocType.
