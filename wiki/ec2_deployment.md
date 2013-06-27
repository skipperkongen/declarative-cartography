# Create an Amazon EC2 AMI for CVL tests

http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/creating-snapshot-s3-linux.html

## Step 1: Customizing an Amazon Linux AMI

I've used a hi-mem instance with Amazon Linux as the baseline. It is configured with software and data to run tests for CVL.

### Launching the instance

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
# Install PG headers
sudo yum install postgresql-devel

# Install GEOS
wget http://download.osgeo.org/geos/geos-3.3.8.tar.bz2
tar xjvf geos-3.3.8.tar.bz2
cd geos-3.3.8
./configure && make && sudo make install


# Install Proj.4
cd ..
wget http://download.osgeo.org/proj/proj-4.8.0.tar.gz
wget http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz
tar xzvf proj-4.8.0.tar.gz
cd proj-4.8.0/nad
tar xzvf ../../proj-datumgrid-1.5.tar.gz
cd ..
./configure && make & sudo make install

# Install GDAL
cd ..
wget http://download.osgeo.org/gdal/gdal-1.9.2.tar.gz
tar xzvf gdal-1.9.2.tar.gz
cd gdal-1.9.2
./configure && make && sudo make install

# Install LibXML2
cd ..
wget ftp://xmlsoft.org/libxml2/libxml2-2.9.1.tar.gz
tar xzvf libxml2-2.9.1.tar.gz 
cd libxml2-2.9.1
./configure && make && sudo make install

# Install JSON-C
cd ..
wget https://s3.amazonaws.com/json-c_releases/releases/json-c-0.9.tar.gz
tar xzvf json-c-0.9.tar.gz 
cd json-c-0.9
./configure && make && sudo make install

# Update library path
sudo su
echo '/usr/local/lib' >> /etc/ld.so.conf.d/geostuff.conf
ldconfig -v | less # check that e.g. geos is in the list
exit

# Install PostGIS
cd ..
wget http://download.osgeo.org/postgis/source/postgis-2.0.3.tar.gz
tar xzvf postgis-2.0.3.tar.gz
cd postgis-2.0.3
./configure && make && sudo make install

# Install PL/Python
sudo yum install postgresql-plpython.noarch
```

### Create database and install extensions:

Now all the software needed is installed. Now create the database with proper extensions (PL/Python and PostGIS):

```
# Create database cvl_paper
sudo su postgres  # postgres user automatically created by postgres package installer
psql
create database cvl_paper;
# Hit ^D to exit pg client

# Reconnect and add extensions
psql -d cvl_paper # still as user postgres
create extension plpythonu;
create extension postgis;
# Test that PL/Python and cvxopt works
DO $$ import cvxopt $$ LANGUAGE plpythonu;  # should print "DO"
# Test that PostGIS works (or at least is installed)
SELECT ST_Intersects(null, null);
```

Configure authentication and tuning:

```
# Set a password for postgres (required for ogr2ogr)
ALTER USER postgres WITH PASSWORD 'postgres';
# Hit ^D to exit pg client

# Configure authentication for local network connections
vi /var/lib/pgsql9/data/pg_hba.conf
# Set authentication to trust for local network connections

# High memory settings
vi /var/lib/pgsql9/data/postgresql.conf
# new settings:
# shared_buffers = 10GB
# work_mem = 500MB

# Restart server
pg_ctl -d /var/lib/pgsql9/data -l /var/log/postgres.log restart
```

### Install CVL

```
# As user postgres, sudo su postgres...
cd /var/lib/pgsql9  # homedir of postgres user
git clone https://github.com/skipperkongen/phd_cvl.git
```

Add data to database

```
cd phd_cvl/data
/usr/local/bin/ogr2ogr -f PostgreSQL PG:"host=localhost user=postgres password=postgres dbname=cvl_paper" -t_srs "epsg:3857" openflights_airports.shp
/usr/local/bin/ogr2ogr -f PostgreSQL PG:"host=localhost user=postgres password=postgres dbname=cvl_paper" -t_srs "epsg:3857" openflights_airports.shp
```
