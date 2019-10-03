"""
file to specify model specifications such that models can be added 
and data can be imported easily
"""

from datetime import datetime, timedelta

model_dict={
        'mwam3':
            {'Hs':'VHM0',
            'lons':'longitude',
            'lats':'latitude',
            'rotlons':'rlon',
            'rotlats':'rlat',
            'time': 'time',
            'path_template':('/lustre/storeB/immutable/' +
                           'archive/projects/metproduction/' +
                           'DNMI_WAVE/%Y/%m/%d/'),
            'path':('/lustre/storeB/immutable/archive/' +
                    'projects/metproduction/DNMI_WAVE/'),
            #'file_template':'MyWave_wam3_WAVE_%Y%m%dT%HZ.nc',
            'file_template':'MyWave_wam3_WAVE_%Y%m%dT%HZ.nc',
            'basetime':datetime(1970,1,1),
            'units_time':'seconds since 1970-01-01 00:00:00',
            'delta_t':'0000-00-00 (01:00:00)',
            'proj4':( "+proj=ob_tran +o_proj=longlat +lon_0=-40"
                    + " +o_lat_p=25 +R=6.371e+06 +no_defs")
            },
        'SWAN':
            {'Hs':'hs',
            'lons':'longitude',
            'lats':'latitude',
            'time': 'time',
            'path_template':('/home/vietadm/wavy/data/SWAN/'),
            'path':('/home/vietadm/wavy/data/SWAN/'),
            'file_template':'SWAN%Y%m%d%H.nc',
            'basetime':datetime(1970,1,1),
            'units_time':'seconds since 1970-01-01 00:00:00',
            'proj4':None
            }
        }
