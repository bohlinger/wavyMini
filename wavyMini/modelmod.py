#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------#
'''
This module encompasses classes and methods to read and process wave
field from model output. 
'''
# --- import libraries ------------------------------------------------#
'''
List of libraries needed for this class.
'''
import sys

# read files
import netCDF4
from netCDF4 import Dataset

# all class
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
import argparse
from argparse import RawTextHelpFormatter
import os
import math

# progress bar
from utils import progress, hour_rounder

# get_remote
from dateutil.relativedelta import relativedelta
from copy import deepcopy

import time

# get necessary paths for module
import pathfinder

# import outsorced specs
from model_specs import model_dict

# matchtime fct
from stationmod import matchtime

# --- global functions ------------------------------------------------#
"""
definition of some global functions.
"""
# currently None
# ---------------------------------------------------------------------#


class model_class():
    '''
    class to read and process model data 
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
        print (" ### Initializing modelmod instance ###")
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

def check_date(model,fc_date=None,init_date=None,leadtime=None):
    """
    ARCMFC3 12 hourly (00h, 12h); naming convention +6h for bulletin
    """
    if model == 'ARCMFC3':
        multsix = int(leadtime/12)
        restsix = leadtime%12
        if ((fc_date - timedelta(hours=leadtime)).hour != 0 and
            (fc_date - timedelta(hours=leadtime)).hour !=12):
            sys.exit('error: --> leadtime is not available')
        if leadtime>228:
            sys.exit('error: --> Leadtime must be less than 228')
        if leadtime is None:
            pass
        else:
            tmp_date = (fc_date
                       - timedelta(hours=multsix*12)
                       - timedelta(hours=restsix))
    else: tmp_date = fc_date
    #(datetime(2019,10,1,18)-timedelta(hours=30)).hour
    return tmp_date

def make_filename(simmode=None,model=None,datein=None,
    expname=None,fc_date=None,init_date=None,leadtime=None):
    filetemplate = 'file_template'
    if simmode == 'fc':
        if model == 'SWAN':
            filename = (model_dict[model]['path']
              + init_date.strftime(model_dict[model][filetemplate]))
    elif simmode == 'cont':
        pass
    return filename

def get_model_filepathlst(simmode=None,model=None,sdate=None,edate=None,
    expname=None,fc_date=None,init_date=None,leadtime=None):
    if (model in model_dict.keys()):
        filestr = make_filename(simmode=simmode,model=model,
                        fc_date=fc_date,init_date=init_date,
                        leadtime=leadtime)
        filepathlst = [filestr]
    return filepathlst

def get_model_fc_mode(filestr=None,model=None,fc_date=None,
    init_date=None,leadtime=None,varname=None):
    """ 
    fct to get model data
    """
    from utils import haversine
    import glob
    print ("Get model data according to selected date ....")
    print(filestr)
    f = netCDF4.Dataset(filestr,'r')
    model_lons = f.variables[model_dict[model]['lons']][:]
    model_lats = f.variables[model_dict[model]['lats']][:]
    model_time = f.variables[model_dict[model]['time']][:]
    # Hs [time,lat,lon]
    if (varname == 'Hs' or varname is None):
        model_Hs = f.variables[model_dict[model]['Hs']][:].squeeze()
    else: 
        model_Hs = f.variables[model_dict[model][varname]][:].squeeze()
    f.close()
    model_basetime = model_dict[model]['basetime']
    model_time_dt=[]
    for element in model_time:
        element = float(element)
        model_time_dt.append(model_basetime
                + timedelta(seconds=element))
    model_time_dt_valid = [model_time_dt[model_time_dt.index(fc_date)]]
    model_time_valid = [model_time[model_time_dt.index(fc_date)]]
    if len(model_Hs.shape)>2:
        model_Hs_valid = model_Hs[model_time_dt.index(fc_date),:,:].squeeze()
    else:
        model_Hs_valid = model_Hs[:,:].squeeze()
    return model_Hs_valid, model_lats, model_lons, model_time_valid,\
         model_time_dt_valid

def get_model(simmode=None,model=None,sdate=None,edate=None,
    fc_date=None,init_date=None,leadtime=None,expname=None,
    sa_obj=None,timewin=None,varname=None):
    """ 
    Get model data.
    """
    if sa_obj is not None:
        sdate = sa_obj.sdate
        edate = sa_obj.edate
    if timewin is None:
        timewin = int(30)
    if (simmode == 'fc'):
        filepathlst = get_model_filepathlst(simmode=simmode,model=model,
                            fc_date=fc_date,init_date=init_date,
                            leadtime=leadtime)
        for element in filepathlst:
            model_Hs, \
            model_lats, \
            model_lons, \
            model_time, \
            model_time_dt = \
            get_model_fc_mode(filestr=element,model=model,
                    fc_date=fc_date,init_date=init_date,
                    leadtime=leadtime,varname=varname)
            model_Hs_lst, \
            model_time_lst, \
            model_time_dt_lst = [],[],[]
            for i in range(len(model_time)):
                model_Hs_lst.append(model_Hs)
                model_time_lst.append(model_time[i])
                model_time_dt_lst.append(model_time_dt[i])
        model_Hs = np.array(model_Hs_lst)
    return model_Hs, model_lats, model_lons, model_time_lst, \
           model_time_dt_lst
