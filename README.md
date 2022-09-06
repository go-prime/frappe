<div align="center">
    <img src=".github/frappe-framework-logo.png" height="150">
    <h1>
        <a href="https://frappe.io">
            frappe
        </a>
    </h1>
</div>


Full-stack web application framework that uses Python and MariaDB on the server side and a tightly integrated client side library. Built for [ERPNext](https://erpnext.com)

# Table of Contents
- [](#)
    - [Website](#website)
    - [License](#license)

## Installation

[Install via Frappe Bench](https://github.com/frappe/bench)

### 1. Install Bench

Follow [**this**](https://computingforgeeks.com/how-to-install-erpnext-erp-system-on-ubuntu/) guide from Josphat Mutai to install erpnext on your Ubuntu 18.04 server/environment.

#### TLDR
---
- Setup python environment  
    `sudo apt update`  
    `sudo apt -y install vim libffi-dev python3-pip python3-dev  python3-testresources libssl-dev wkhtmltopdf`
- Setup node  
    `sudo curl --silent --location https://deb.nodesource.com/setup_12.x | sudo bash -`  
    `sudo apt -y install gcc g++ make nodejs redis-server`  
    `sudo npm install -g yarn`  
- Setup nginx  
    `$ sudo apt -y install nginx`
- Setup mariadb  
    `sudo apt install mariadb-server`  
    Change the authentication plugin  
    `$ sudo mysql -u root`  

    > `USE mysql;`  
    > `UPDATE user SET plugin='mysql_native_password' WHERE User='root';`  
    > `FLUSH PRIVILEGES;`  
    > `EXIT;`  
    
    Setup the mariadb configuration to work with frappe  
    `$ sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf`

    > [mysqld]  
    > character-set-client-handshake = FALSE  
    > character-set-server = utf8mb4  
    > collation_server = utf8mb4_unicode_ci  
    >   
    > [mysql]  
    > default-character-set = utf8mb4  
    
    `$ sudo nano /etc/mysql/my.cnf`  
    
    > [mysqld]  
    > innodb-file-format=barracuda  
    > innodb-file-per-table=1  
    > innodb-large-prefix=1  
    > character-set-client-handshake = FALSE  
    > character-set-server = utf8mb4  
    > collation-server = utf8mb4_unicode_ci  
    >  
    > [mysql]  
    > default-character-set = utf8mb4  

    Restart Mariadb  
    `sudo systemctl restart mariadb`  

    Set Mariadb root password (assuming no password exists on the installation)  
    `mysqladmin -u root password newpass`  

- Install the bench tool
    Assuming the application will be used on an account named **erpnext**
    `sudo useradd -m -s /bin/bash erpnext`  
    `sudo passwd erpnext`  
    `sudo usermod -aG sudo erpnext`  
    Update the path  
    `sudo su - erpnext`  
    `tee -a ~/.bashrc<<EOF`  
    `PATH=\$PATH:~/.local/bin/`  
    `EOF`  

    `source ~/.bashrc`  

    Setup the bench directory  
    `sudo mkdir /srv/bench`  
    `sudo chown -R erpnext /srv/bench`  
    `sudo su - erpnext`  
    `cd /srv/bench`  

    Install bench  
    `pip3 install frappe-bench`  

### 2. Install Frappe 
`cd /srv/bench`  
To install frappe(**Make sure to install version-12**):  
`bench init --frappe-branch version-12 erpnext`

### 3. Install apps
Create your site first  
You will be prompted to enter the root password  for mariadb  
`cd erpnext`  
`bench new-site <site_name>`  

For each app you want to install:
- Clone it from it's repository, specifying the branch you want cloned
    `bench get-app <app_name> --branch <branch_name> <github_url>`  
- Install it onto the site in question
    `bench --site <site_name> install-app <app_name>`

### 4. Replace third-party frappe with forked version 
- Backup the current frappe installation  
  `cd /srv/bench/apps/`  
  `cp -r frappe frappe_bkup`  
- Manually clone the forked version of frappe  
  `git clone --branch prime-erp-master --depth 1 https://github.com/go-prime/frappe.git`  
- Copy the node_modules folder from the backup frappe and delete the original frappe folder
  `cp -r frappe_bkup/node_modules frappe`  
  `rm -rf frappe`
- Migrate your app  
  `bench migrate`  
- Build the js and css bundles  
  `bench build`  

### 6. Troubleshooting
- WIP
## Website

For details and documentation, see the website
[https://frappe.io](https://frappe.io)

## License
This repository has been released under the [MIT License](LICENSE).
