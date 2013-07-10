# Data for CVL

Data has been uploaded to S3

* https://s3-eu-west-1.amazonaws.com/cvl-datasets/pnt_7k_airports.tar.bz2
* https://s3-eu-west-1.amazonaws.com/cvl-datasets/pnt_500k_tourism.tar.bz2
* https://s3-eu-west-1.amazonaws.com/cvl-datasets/pol_30k_dai.tar.bz2
* https://s3-eu-west-1.amazonaws.com/cvl-datasets/lin_100k_usrivers.tar.bz2
* https://s3-eu-west-1.amazonaws.com/cvl-datasets/pnt_30m_synthetic.tar.bz2

Also, datasets have now been imported into PostgreSQL database on Amazon EC2 instance (AMI: ).


## Getting the data

Download file:

```
wget URL
```

Extract file:

```
tar xjvf *.tar.bz2
```

Load data into DB:

```
/usr/local/bin/ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=cvl_paper" -t_srs "epsg:3857" NAME_OF_FILE.shp
``` 

