#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------#
'''
This module encompasses classes and methods to read and write to netcdf 
files from model, station, or satellite output. I try to mostly follow 
the PEP convention for python code style. Constructive comments on style 
and effecient programming are most welcome!
'''
# --- import libraries ------------------------------------------------#
'''
List of libraries needed for this class. Sorted in categories to serve
effortless orientation. May be combined at some point.
'''
# read files
from netCDF4 import Dataset
import netCDF4

# all class
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
import argparse
from argparse import RawTextHelpFormatter
import os

# specs
from variable_info import var_dict

# progress bar
import sys

# get_remote
from dateutil.relativedelta import relativedelta
from copy import deepcopy

import time

# get necessary paths for module
import pathfinder

# --- global functions ------------------------------------------------#
"""
definition of some global functions
"""
# currently None
# ---------------------------------------------------------------------#


class ncmod():
    '''
    class to write to netcdf files from satellite, station, or model data
    satellite: level 3 data i.e. Hs[time], lat[time], lon[time] 
    station: e.g. Hs[time], lat, lon
    model: e.g. Hs[time,lat,lon], lat[rlat,rlon], lon[rlat,rlon]
    This class should communicate with the satellite, model, and 
    station classes.
    '''
    satpath_lustre = pathfinder.downloadpath
    satpath_ftp_014_001 = pathfinder.satpath_ftp_014_001
    
    from region_specs import region_dict
    from model_specs import model_dict

    def __init__(self,sdate,edate=None,model=None,timewin=None,region=None):
        print ('# ----- ')
        print (" ### Initializing ncmod instance ###")
        print ('# ----- ')
        if region is None:
            model='ARCMFC'
        if timewin is None:
            timewin = int(30)
        if edate is None:
            edate=sdate
            if timewin is None:
                timewin = int(30)
            print ("Requested time: ", str(sdate))
            print (" with timewin: ", str(timewin))
        else:
            print ("Requested time frame: " +
                str(sdate) + " - " + str(edate))
        self.sdate = sdate
        self.edate = edate
        self.model = model
        self.basetime = model_dict[model]['basetime']

def get_nc_time(pathtofile):
    """
    timestep: "first" or "last" time step in nc-file
    pathtofile: complete path to file
    """
    import os.path
    indicator = os.path.isfile(pathtofile)
    if indicator is False:
        dtime = False
    else:
        nc = netCDF4.Dataset(
                    pathtofile,mode='r',
                    )
        time_var = nc.variables['time']
        dtime = netCDF4.num2date(time_var[:],time_var.units)
        nc.close()
    return dtime

def get_nc_ts(pathtofile,varlst):
    import os.path
    indicator = os.path.isfile(pathtofile)
    if indicator is False:
        dtime = False
        sys.exit('File does not exist')
    else:
        vardict = {}
        for name in varlst:
            nc = netCDF4.Dataset(
                pathtofile,mode='r',
                )
            var = nc.variables[name][:]
            vardict[name]=var
        time_var = nc.variables['time']
        dtime = netCDF4.num2date(time_var[:],time_var.units)
        vardict['dtime']=dtime
        nc.close()
    return vardict

def get_coll_ts(pathtofile):
    import os.path
    indicator = os.path.isfile(pathtofile)
    if indicator is False:
        dtime = False
        print('File does not exist')
        return
    else:
        nc = netCDF4.Dataset(
            pathtofile,mode='r',
            )
        time_var = nc.variables['time']
        dtime = netCDF4.num2date(time_var[:],time_var.units)
        sHs = nc.variables['sHs'][:]
        mHs = nc.variables['mHs'][:]
        nc.close()
    return dtime,sHs,mHs

def dumptonc_ts(outpath,filename,title,basetime,results_dict):
    """
    1. check if nc file already exists
    2. - if so use append mode
       - if not create file
    """
    time_dt = results_dict['date_matches']
    # create time vector in seconds since first date
    time = []
    for dt in time_dt:
        time.append((dt-basetime).total_seconds())
    time = np.array(time)
    mHs = results_dict['model_Hs_matches']
    mlons = results_dict['model_lons_matches']
    mlats = results_dict['model_lats_matches']
    sHs = results_dict['sat_Hs_matches']
    slons = results_dict['sat_lons_matches']
    slats = results_dict['sat_lats_matches']
    dists = results_dict['dist_matches']
    
    fullpath = outpath + filename
    print ('Dump data to file: ' + fullpath)
    if os.path.isfile(fullpath):
        nc = netCDF4.Dataset(
                        fullpath,mode='a',
                        clobber=False
                        )
        # variables
        #ncrtime=nc.variables['rtime'][:]
        startidx = len(nc['time'])
        endidx = len(nc['time'])+len(time)
        nc.variables['time'][startidx:endidx] = time[:]
        nc.variables['mHs'][startidx:endidx] = mHs[:]
        nc.variables['mlons'][startidx:endidx] = mlons[:]
        nc.variables['mlats'][startidx:endidx] = mlats[:]
        nc.variables['sHs'][startidx:endidx] = sHs[:]
        nc.variables['slons'][startidx:endidx] = slons[:]
        nc.variables['slats'][startidx:endidx] = slats[:]
        nc.variables['dists'][startidx:endidx] = dists[:]
    else:
        os.system('mkdir -p ' + outpath)
        nc = netCDF4.Dataset(
                        fullpath,mode='w',
#                        format='NETCDF4'
                        )
        nc.title = title
        dimsize = None
        # dimensions
        dimtime = nc.createDimension(
                                'time',
                                size=dimsize
                                )
        # variables
        nctime = nc.createVariable(
                               'time',
                               np.float64,
                               dimensions=('time')
                               )
        ncmlats = nc.createVariable(
                               'mlats',
                               np.float64,
                               dimensions=('time')
                               )
        ncmlons = nc.createVariable(
                               'mlons',
                               np.float64,
                               dimensions=('time')
                               )
        ncmHs = nc.createVariable(
                               'mHs',
                               np.float64,
                               dimensions=('time')
                               )
        ncslats = nc.createVariable(
                               'slats',
                               np.float64,
                               dimensions=('time')
                               )
        ncslons = nc.createVariable(
                               'slons',
                               np.float64,
                               dimensions=('time')
                               )
        ncsHs = nc.createVariable(
                               'sHs',
                               np.float64,
                               dimensions=('time')
                               )
        ncdists = nc.createVariable(
                               'dists',
                               np.float64,
                               dimensions=('time')
                               )
        # generate time for netcdf file
        # time
        nctime.standard_name = 'time matches'
        nctime.long_name = 'associated time steps between model and observation'
        nctime.units = 'seconds since ' + str(basetime)
        nctime[:] = time
        # mHs
        ncmHs.standard_name = 'model Hs'
        ncmHs.long_name = 'significant wave height from wave model'
        ncmHs.units = 'm'
        ncmHs[:] = mHs
        # mlons
        ncmlons.standard_name = 'model lons'
        ncmlons.long_name = 'longitudes of associated model grid points'
        ncmlons.units = 'degrees east'
        ncmlons[:] = mlons
        # mlats
        ncmlats.standard_name = 'model lats'
        ncmlats.long_name = 'latitudes of associated model grid points'
        ncmlats.units = 'degrees north'
        ncmlats[:] = mlats
        # sHs
        ncsHs.standard_name = 'observed Hs'
        ncsHs.long_name = 'significant wave height from wave observation'
        ncsHs.units = 'm'
        ncsHs[:] = sHs
        # slons
        ncslons.standard_name = 'obs lons'
        ncslons.long_name = 'longitudes of observations'
        ncslons.units = 'degrees east'
        ncslons[:] = slons
        # slats
        ncslats.standard_name = 'obs lats'
        ncslats.long_name = 'latitudes of observations'
        ncslats.units = 'degrees north'
        ncslats[:] = slats
        # dists
        ncdists.standard_name = 'dists'
        ncdists.long_name = 'distances between observations and model grids'
        ncdists.units = 'km'
        ncdists[:] = dists
    nc.close()

def dumptonc_stats(outpath,filename,title,basetime,time_dt,valid_dict):
    """
    1. check if nc file already exists
    2. - if so use append mode
       - if not create file
    """
    # create time vector in seconds since first date
    time = np.array((time_dt-basetime).total_seconds())
    mop = np.array(valid_dict['mop'])
    mor = np.array(valid_dict['mor'])
    rmsd = np.array(valid_dict['rmsd'])
    msd = np.array(valid_dict['msd'])
    corr = np.array(valid_dict['corr'])
    mad = np.array(valid_dict['mad'])
    bias = np.array(valid_dict['bias'])
    SI = np.array(valid_dict['SI'][1])
    nov = np.array(valid_dict['nov'])
    fullpath = outpath + filename
    print ('Dump data to file: ' + fullpath)
    if os.path.isfile(fullpath):
        nc = netCDF4.Dataset(
                        fullpath,mode='a',
                        clobber=False
                        )
        # variables
        startidx = len(nc['time'])
        endidx = len(nc['time'])+1
        print(startidx)
        print(endidx)
        nc.variables['time'][startidx:endidx] = time
        nc.variables['mop'][startidx:endidx] = mop
        nc.variables['mor'][startidx:endidx] = mor
        nc.variables['rmsd'][startidx:endidx] = rmsd
        nc.variables['msd'][startidx:endidx] = msd
        nc.variables['corr'][startidx:endidx] = corr
        nc.variables['mad'][startidx:endidx] = mad
        nc.variables['bias'][startidx:endidx] = bias
        nc.variables['SI'][startidx:endidx] = SI
        nc.variables['nov'][startidx:endidx] = nov
    else:
        os.system('mkdir -p ' + outpath)
        nc = netCDF4.Dataset(
                        fullpath,mode='w',
#                        format='NETCDF4'
                        )
        nc.title = title
        dimsize = None
        # dimensions
        dimtime = nc.createDimension(
                                'time',
                                size=dimsize
                                )
        # variables
        nctime = nc.createVariable(
                               'time',
                               np.float64,
                               dimensions=('time')
                               )
        ncmop = nc.createVariable(
                               'mop',
                               np.float64,
                               dimensions=('time')
                               )
        ncmor = nc.createVariable(
                               'mor',
                               np.float64,
                               dimensions=('time')
                               )
        ncrmsd = nc.createVariable(
                               'rmsd',
                               np.float64,
                               dimensions=('time')
                               )
        ncmsd = nc.createVariable(
                               'msd',
                               np.float64,
                               dimensions=('time')
                               )
        nccorr = nc.createVariable(
                               'corr',
                               np.float64,
                               dimensions=('time')
                               )
        ncmad = nc.createVariable(
                               'mad',
                               np.float64,
                               dimensions=('time')
                               )
        ncbias = nc.createVariable(
                               'bias',
                               np.float64,
                               dimensions=('time')
                               )
        ncSI = nc.createVariable(
                               'SI',
                               np.float64,
                               dimensions=('time')
                               )
        ncnov = nc.createVariable(
                               'nov',
                               np.float64,
                               dimensions=('time')
                               )
        # generate time for netcdf file
        # time
        nctime.standard_name = 'time matches'
        nctime.long_name = 'associated time steps between model and observation'
        nctime.units = 'seconds since ' + str(basetime)
        nctime[:] = time
        # mop
        ncmop.standard_name = 'mop'
        ncmop.long_name = 'mean of product (wave model)'
        ncmop.units = 'm'
        ncmop[:] = mop
        # mor
        ncmor.standard_name = 'mor'
        ncmor.long_name = 'mean of reference (observations)'
        ncmor.units = 'm'
        ncmor[:] = mor
        # rmsd
        ncrmsd.standard_name = 'rmsd'
        ncrmsd.long_name = 'root mean square deviation'
        ncrmsd.units = 'm'
        ncrmsd[:] = rmsd
        # msd
        ncmsd.standard_name = 'msd'
        ncmsd.long_name = 'mean square deviation'
        ncmsd.units = 'm^2'
        ncmsd[:] = msd
        # corr
        nccorr.standard_name = 'corr'
        nccorr.long_name = 'correlation coefficient'
        nccorr.units = 'none'
        nccorr[:] = corr
        # mad
        ncmad.standard_name = 'mad'
        ncmad.long_name = 'mean absolute deviation'
        ncmad.units = 'm'
        ncmad[:] = mad
        # bias
        ncbias.standard_name = 'bias'
        ncbias.long_name = 'Bias (mean error)'
        ncbias.units = 'm'
        ncbias[:] = bias
        # SI
        ncSI.standard_name = 'SI'
        ncSI.long_name = 'scatter index'
        ncSI.units = 'none'
        ncSI[:] = SI
        # nov
        ncnov.standard_name = 'nov'
        ncnov.long_name = 'number of values'
        ncnov.units = 'none'
        ncnov[:] = nov
    nc.close()

def dumptonc_sat(sa_obj,outpath,mode=None):
    """
    dump satellite altimetry data to netcdf-file
    """
    sdate=sa_obj.sdate
    edate=sa_obj.edate
    filename = (sa_obj.sat
                + "_"
                + sa_obj.region
                + "_"
                + sdate.strftime("%Y%m%d%H%M%S")
                + "_"
                + edate.strftime("%Y%m%d%H%M%S")
                + ".nc")
    fullpath = outpath + filename
    os.system('mkdir -p ' + outpath)
    print ('Dump altimeter wave from ' 
            + sa_obj.sat 
            + ' data to file: ' + fullpath)
    nc = netCDF4.Dataset(
                    fullpath,mode='w',
                    )
    nc.title = sa_obj.sat + ' altimeter significant wave height'
    timerange=len(sa_obj.ridx)
    dimsize = None
    # dimensions
    dimtime = nc.createDimension(
                            'time',
                            size=dimsize
                            )
    # variables
    nctime = nc.createVariable(
                           'time',
                           np.float64,
                           dimensions=('time')
                           )
    nclatitude = nc.createVariable(
                           'latitude',
                           np.float64,
                           dimensions=('time')
                           )
    nclongitude = nc.createVariable(
                           'longitude',
                           np.float64,
                           dimensions=('time')
                           )
    ncHs = nc.createVariable(
                           'Hs',
                           np.float64,
                           dimensions=('time')
                           )

    # generate time for netcdf file
    basetime=sa_obj.basetime
    nctime.units = 'seconds since 2000-01-01 00:00:00'
    nctime[:] = sa_obj.time
    ncHs.units = 'm'
    ncHs[:] = sa_obj.Hs
    ncHs.standard_name = 'sea_surface_wave_significant_height'
    ncHs.long_name = \
        'Significant wave height estimate from altimeter wave form'
    ncHs.valid_range = 0., 25.
    nclongitude.units = 'degree_east'
    nclongitude[:] = sa_obj.loc[1]
    nclongitude.standard_name = 'longitude'
    nclongitude.valid_min = -180.
    nclongitude.valid_max = 180.
    nclatitude[:] = sa_obj.loc[0]
    nclatitude.standard_name = 'latitude'
    nclatitude.units = 'degree_north'
    nclatitude.valid_min = -90.
    nclatitude.valid_max = 90.
    nc.close()

def dumptonc_ts_pos(outpath,filename,title,basetime,\
                    coll_dict,model,varname):
    """
    1. check if nc file already exists
    2. - if so use append mode
       - if not create file
    """
    time = coll_dict['time']
    var_model = coll_dict[varname]
    lons_model = coll_dict['lons_model']
    lats_model = coll_dict['lats_model']
    lons_pos = coll_dict['lons_pos']
    lats_pos = coll_dict['lats_pos']
    dist = coll_dict['hdist']
    idx = coll_dict['idx']
    idy = coll_dict['idy']
    fullpath = outpath + filename
    print ('Dump data to file: ' + fullpath)
    if os.path.isfile(fullpath):
        nc = netCDF4.Dataset(
                        fullpath,mode='a',
                        clobber=False
                        )
        # variables
        startidx = len(nc['time'])
        endidx = len(nc['time'])+len(time)
        nc.variables['time'][startidx:endidx] = time[:]
#        nc.variables['dist'][startidx:endidx] = dist[:]
        nc.variables[varname][startidx:endidx] = var_model[:]
    else:
        os.system('mkdir -p ' + outpath)
        nc = netCDF4.Dataset(
                        fullpath,mode='w',
#                        format='NETCDF4_CLASSIC'
                        )
        # global attributes
        nc.title = title
#        nc.netcdf_version = "NETCDF4_CLASSIC"
        nc.netcdf_version = "NETCDF4"
        nc.processing_level = "No post-processing performed"
        nc.static_position_station =  ("Latitude: "
                            + "{:.4f}".format(lats_pos[0])
                            + ", Longitude: "
                            + "{:.4f}".format(lons_pos[0]))
        nc.static_position_model =  ("Latitude: "
                            + "{:.4f}".format(lats_model[0])
                            + ", Longitude: "
                            + "{:.4f}".format(lons_model[0]))
        nc.static_collocation_idx =  ("idx: "
                            + str(idx[0])
                            + ", idy: "
                            + str(idy[0]))
        nc.static_collocation_distance =  ("{:.4f}".format(dist[0]) + " km")
        # dimensions
        dimsize = None
        dimtime = nc.createDimension(
                                'time',
                                size=dimsize
                                )
        # variables
        nctime = nc.createVariable(
                               'time',
                               np.float64,
                               dimensions=('time')
                               )
#        ncdist = nc.createVariable(
#                               'dist',
#                               np.float64,
#                               dimensions=('time')
#                               )
        ncvar_model = nc.createVariable(
                               varname,
                               np.float64,
                               dimensions=('time')
                               )
        # generate time for netcdf file
        # time
        nctime.standard_name = var_dict['time']['standard_name']
        nctime.units = var_dict['time']['units'] + ' ' + str(basetime)
        nctime[:] = time
#        # dist
#        ncdist.standard_name = 'collocation_distance'
#        ncdist.units = 'km'
#        ncdist[:] = dist
        # var_model
        ncvar_model.standard_name = var_dict[varname]['standard_name']
        ncvar_model.units = var_dict[varname]['units']
        ncvar_model.valid_range = var_dict[varname]['valid_range'][0], \
                                  var_dict[varname]['valid_range'][1]
        ncvar_model[:] = var_model
    nc.close()
