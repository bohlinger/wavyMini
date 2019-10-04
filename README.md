# wavyMini Vietnam

### Main developer and moderation:
Patrik Bohlinger, Norwegian Meteorological Institute, patrikb@met.no

## Purpose
Example tailored to Vietnam workshop comprising:  
1. downloading satellite data  
2. quicklook examples  
3. usage examples on collocation and validation  

## Getting Started
### Installing wavyMini (aready done on your laptop)
1. First download or clone the wavyMini github repository: https://github.com/bohlinger/wavyMini  
Info on how-to clone a repository:
https://help.github.com/en/articles/cloning-a-repository  
2. To make it consistent please use as target location your home directory e.g.: ~/wavyMini.

### HELP
Executable files usually have help function which can be read using e.g.:
./executable.py -h

### Preparations
1. Store your credentials for Copernicus in ~/.netrc:  
```
machine nrt.cmems-du.eu   login USER   password PASSWORD
```
2. Satellite altimetry data must be downloaded. For this we can use the satellite module satmod.py and an example program called download.py, both located in the  ~/wavyMini/wavyMini directory. Type ./download -h to read instructions. You can download data for the satellite types: s3a, s3b, al, c2, j3. For example type:  
```
./download.py -sat s3a -sd 2019093000 -ed 2019100400 -nproc 4 -path /home/vietadm/wavyMini/data/altimetry/
```
3. SWAN model output must be provided for collocation and validation. E.g. copy your SWAN files to ~/wavyMini/data/SWAN/. The filename format and path of model output must be specified in the model_specs.py e.g: SWAN2019093012.nc.

### Quicklook examples ~/wavyMini/wavyMini
1. browse for satellite data and show footprints on map for one time step:
```
./check_sat.py -sat c2 -reg Vietnam -sd 2019100118 --show
```
2. browse for satellite data and show footprints on map for time period:
```
./check_sat.py -sat c2 -reg Vietnam -sd 2019100118 -ed 2019100318 --show
```
3. same as above but now dump data to netcdf-file
```
./check_sat.py -sat c2 -reg Vietnam -sd 2019100118 -ed 2019100318 -dump /home/vietadm/wavyMini/data/altimetry/quickdump/
```
4. browse for satellite data, collocate and show footprints and model for one time step:
```
./check_sat.py -sat c2 -mod SWAN -reg Vietnam -sd 2019100118 -lt 30 -twin 30 --col --show
```

### Usage examples ~/wavyMini/usage
1. Collocation and systematically dump to netcdf-file:
```
./collocate.py -sd 2019093012 -ed 2019100318 -sat c2 -mod SWAN -reg Vietnam
```
2. Validation and systematically dump to netcdf-file:
```
./validate.py -sd 2019093012 -ed 2019100318 -sat c2 -mod SWAN
```
3. Plotting basic validation figures:
```
./figures.py -sd 201910 -sat c2 -mod SWAN
```
