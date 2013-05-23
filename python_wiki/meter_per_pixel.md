# Meter per pixel (EPSG:3857)

Function that returns number of meters per pixel for different zoom-levels (z) in EPSG:3857 (WebMercator). Default tile-size is 256x256.

```python
def meter_per_pixel_3857(z, tilesize=256.0):
	assert z >= 0
	level0_meter = 20037508.34 * 2
	return (level0_meter / 2**z) / tilesize
```

Example usage:

```python
>>> meter_per_pixel_3857(3)
19567.87923828125
```
