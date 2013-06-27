# Deploying on EC2

## Setting up AMI

### Basic stuff

1. Launch Amazon Linux 64 bit, m2.xlarge
2. Connect: `ssh -i phd.pem ec2-user@ec2-54-216-58-27.eu-west-1.compute.amazonaws.com`
3. Update: `sudo yum update`

### Install cvxopt

```
# Install basic build stuff: http://toomuchdata.com/2012/06/25/how-to-install-python-2-7-3-on-centos-6-2/
sudo yum groupinstall "Development tools"
sudo yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel

# Install dependency for cvxopt
sudo yum install lapack-devel python-devel

# Install pip and then cvxopt
sudo curl http://python-distribute.org/distribute_setup.py | sudo python
sudo curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python
sudo pip install cvxopt

# Test
python # and then 'import cvxopt'
```

### Install PostgreSQL, PL/Python and PostGIS

Install PostgreSQL, loosely based on [this](http://loc2log.ucoz.com/blog/installing_postgresql_at_amazon_ec2/2012-03-24-1).

```
# Install PostgreSQL
sudo yum install postgresql postgresql-libs postgresql-server postgresql-contrib
sudo service postgresql initdb
sudo service postgresql start

# Test
sudo service postgresql status
# or 
ps aux | grep postgres

# Set to start on boot
sudo chkconfig postgresql on
```

Install PostGIS with dependencies:

```
sudo yum install postgresql-devel
```

Create database and install extensions:

```
# PL/Python
sudo yum install postgresql-plpython.noarch

# Create database cvl_paper
sudo su postgres  # postgres user automatically created by postgres package installer
psql
create database cvl_paper;
# Hit ^D to exit pg client

# Add PL/Python and PostGIS to cvl_paper database
psql -d cvl_paper # still as user postgres
create extension plpythonu;
create extension postgis;
# Test that PL/Python and cvxopt works
DO $$ import cvxopt $$ LANGUAGE plpythonu;  # should print "DO"
# Hit ^D to exit pg client
```

