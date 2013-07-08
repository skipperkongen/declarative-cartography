# Creating the 30 million points synthetic dataset

```sql
create table synthetic_points_30m AS
select ogc_fid, wkb_geometry, "type" from osm_tourism_points;

insert into synthetic_points_30m
(select ogc_fid, st_translate(wkb_geometry, random()*10000, random()*10000), "type" from synthetic_points_30m);

insert into synthetic_points_30m
(select ogc_fid, st_translate(wkb_geometry, random()*10000, random()*10000), "type" from synthetic_points_30m);

insert into synthetic_points_30m
(select ogc_fid, st_translate(wkb_geometry, random()*10000, random()*10000), "type" from synthetic_points_30m);

insert into synthetic_points_30m
(select ogc_fid, st_translate(wkb_geometry, random()*10000, random()*10000), "type" from synthetic_points_30m);

insert into synthetic_points_30m
(select ogc_fid, st_translate(wkb_geometry, random()*10000, random()*10000), "type" from synthetic_points_30m);

insert into synthetic_points_30m
(select ogc_fid, st_translate(wkb_geometry, random()*10000, random()*10000), "type" from synthetic_points_30m);

CREATE INDEX synthetic_pt_30m_geom_gist ON synthetic_pt_30m USING GIST (wkb_geometry);

VACCUM ANALYZE synthetic_pt_30m;
```