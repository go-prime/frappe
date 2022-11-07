Thank you for contributing to one of Go-prime's projects. To ensure the best code quality please make sure to follow closely the guidelines outlined in this document.
If you have any queries don't hesistate to get in touch via the issues tab.

## Table of Contents
- Setting up your environment
- Coding Standards
- Style Guides
- Branching Strategy/ Naming conventions
- Test requirements
- Pull request guidelines
- Security considerations


### Setting up your environment
- For development on our platform, we recommend using Microsoft VSCode and WSL on Microsoft Windows and VSCode on Linux/Mac.
- For detailed installation guidelines, please refer to the readme found **[here](https://github.com/go-prime/frappe/blob/prime-erp-develop/README.md)**

### Security considerations
- To prevent SQL injection, use the frappe orm to inject variables in raw sql queries instead of using regular python format strings.
  Do this:
  ```
  user = "Administrator"
  frappe.db.sql("select name from tabUser where name = '%s' ", user)
  ```
  Not this:
  ```
  user = "Administrator"
  frappe.db.sql("select name from tabUser where name = '{}' ".format(user))```
- Do not hard code API keys or other sensitive information directly into a project. Instead, use single doctypes to store confirguration data that can be retrieved for use in your code
- Prefer usage of the ORM over SQL for simple queries.
- Whitelisted methods should not have db inserts that ignore a user's permissions as this can allow remote arbitrary code execution 
  For instance:
  ```
  @frappe.whitelist()
  def create_document(values):
    doc = frappe.get_doc(values).insert(ignore_permissions=True)
  return doc
  ```
### Coding standards
- Make sure any business logic in the frontend is also replicated in server side code, to ensure instances of doctypes created programmatically implement this code.
### Branching strategy / Naming conventions
- Our reference branches for all our projects follow the convention of **master** for production and production deployed code and **develop** for testing features and deployment to our dev servers
- Our branching strategy follows the guidelines outlined [here](https://nvie.com/posts/a-successful-git-branching-model/)
- All changes should be branched off from master into work in progress branches and the branches should be suitably labelled. Tagging the branch by the category it belongs to is helpful e.g. feat, fix, patch. The category is followed by a descriptive name of the brach separated by a forward slash for instance:
    `git checkout -b fix/monthly_sales_report`
### Style Guides 
- Our primary technologies are Python, Javascript and SQL. For each we have recommended style guides for syntax.
- Python follows the **[PEP8 style guide](https://peps.python.org/pep-0008/)** and we encourage using a linter such as pylint to ensure the code adhere's to that standard.
- SQL should follow the guidelines provided by the Mozilla foundation located **[here](https://docs.telemetry.mozilla.org/concepts/sql_style.html)**
- For Javascript we prefer the **[AirBnB code guidelines](https://github.com/airbnb/javascript)** for the simple guidelines they provide for writing good js
### Test requirements
- It is imperative that all new features implement unit tests, especially for backend code. Integration, UI tests are currently a nice to have and can be included using Cypress.
- Test data in frappe is persistent between runs so design your tests around that functionality, ensuring teardowns are implemented so that test cases are repeatable and do not need a specific environment to run
- Please use **[this guide](https://frappeframework.com/docs/v13/user/en/introduction)** to get up to speed with testing using our framework
- CI/CD - WIP
### Pull request guidelines
- All pull requests must be accompanied by a suite of passing unit tests that cover at least 80% of the changes.
- All pull requests must first be directed to the develop branch of a project and deployed to a dev server for UAT before production deployment.
- On acceptance, the same branch can then be merged into production.
