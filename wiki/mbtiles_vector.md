# Using MBTiles for vector

[MBTiles](http://www.mapbox.com/developers/mbtiles/) were designed to hold raster data. The same [specification](https://github.com/mapbox/mbtiles-spec) can be easily modified for vector data, either to produce "index tiles" or "vector tiles". See [Gaffuri, Towards Web Mapping with Vector Data](http://link.springer.com/chapter/10.1007/978-3-642-33024-7_7) for definitions of these concepts.

[specification](https://github.com/mapbox/mbtiles-spec) requires data to be stored in an SQLite database. There is nothing wrong with using a different database, as none of the features used are specific to SQLite. One could even use a non-relational database such as [TightDB](http://www.tightdb.com/).