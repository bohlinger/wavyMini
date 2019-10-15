# wavyMini Vietnam

### Main developer and moderation:
Patrik Bohlinger, Norwegian Meteorological Institute, patrikb@met.no

## Purpose
Package to aid wave model validation using satellite altimetry. This example is tailored to the Vietnam workshop comprising:  
1. downloading satellite data  
2. quicklook examples  
3. usage examples on collocation and validation  

## Additional info
For this version much of the code has been removed to keep mostly only what is necessary for the Vietnam workshop. Some code rests and zombies remain for practical reasons. The collocation method follows Bohlinger et al. (2019): https://www.sciencedirect.com/science/article/pii/S1463500319300435. The satellite data is obtained from http://marine.copernicus.eu/services-portfolio/access-to-products/?option=com_csw&view=details&product_id=WAVE_GLO_WAV_L3_SWH_NRT_OBSERVATIONS_014_001. In the end of this exercise validation figures are produced comparable to http://cmems.met.no/ARC-MFC/WaveValidation/index.html.

## Getting Started
### Installing wavyMini (aready done on your laptop)
1. First download or clone the wavyMini github repository: https://github.com/bohlinger/wavyMini  
Info on how-to clone a repository:
https://help.github.com/en/articles/cloning-a-repository  
2. To make it consistent please use as target location your home directory e.g.: ~/wavyMini.
3. Information on data, both observations and wave model output, needs to be given and stored in the files ~/wavyMini/pathfinder.py and ~/wavyMini/model_specs.py. Please adjust these files according to your plans.

### HELP
Executable files usually have help function which can be read using e.g.:
./executable.py -h

### Preparations
1. Store your credentials for Copernicus in ~/.netrc:  
```
machine nrt.cmems-du.eu   login USER   password PASSWORD
```
For security reasons, the .netrc-file needs to have limited rights other than for the administrator. Correct the file rights if necessary e.g. with
```
chmod 700 .netrc
```
2. Satellite altimetry data must be downloaded. For this we can use the satellite module satmod.py and an example program called download.py, both located in the  ~/wavyMini/wavyMini directory. Type ./download.py -h to read instructions. You can download data for the satellite types: s3a, s3b, al, c2, j3. For example type:  
```
./download.py -sat c2 -sd 2019093000 -ed 2019100400 -nproc 4 -path /home/vietadm/wavyMini/data/altimetry/
```
Available satellites are:
- s3a (Sentinel 3A)
- s3b (Sentinel 3B)
- c2 (Cryosat2)
- j3 (Jason3)
- al (SARAL/AltiKa)
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
./check_sat.py -sat c2 -mod SWAN -reg Vietnam -sd 2019100118 -lt 30 -twin 30 -col --show
```
5. 
use multiple satellite missions in one line e.g. all of them:
```
./check_sat.py -sat all -mod SWAN -reg Vietnam -sd 2019100118 -lt 30 -twin 30 -col --show
```
or list of stellites:
```
./check_sat.py -sat multi -l s3a,c2,al -mod SWAN -reg Vietnam -sd 2019100118 -lt 30 -twin 30 -col --show
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
./figures.py -d 201910 -sat c2 -mod SWAN
```
