#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------#
'''
This module encompasses classes and methods to read and process wave
field related data from stations.
'''
__version__ = "0.5.0"
__author__="Patrik Bohlinger, Norwegian Meteorological Institute"
__maintainer__ = "Patrik Bohlinger"
__email__ = "patrikb@met.no"
__status__ = "operational ARCMFC branch"

# --- import libraries ------------------------------------------------#
'''
List of libraries needed for this class.
'''
# ignore irrelevant warnings from matplotlib for stdout
import warnings
warnings.filterwarnings("ignore")

# all class
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
import argparse
from argparse import RawTextHelpFormatter
import os

# get_altim
import urllib
import gzip
import ftplib
from ftplib import FTP

# read_altim
import netCDF4 as netCDF4

# create_file
import calendar

# libraries for parallel computing
from joblib import Parallel, delayed
import multiprocessing as mp

# bintime
import math

# progress bar
import sys

# get_remote
from dateutil.relativedelta import relativedelta
from copy import deepcopy

import time

# get d22 files
from datetime import datetime

# --- global functions ------------------------------------------------#

# define flatten function for lists
''' fct does the following:
flat_list = [item for sublist in TIME for item in sublist]
or:
for sublist in TIME:
for item in sublist:
flat_list.append(item)
'''
flatten = lambda l: [item for sublist in l for item in sublist]

# ---------------------------------------------------------------------#


def matchtime(sdate,edate,time,basetime=None,timewin=None):
    '''
    fct to obtain the index of the time step closest to the 
    requested time including the respective time stamp(s). 
    Similarily, indices are chosen for the time and defined region.
    '''
    if timewin is None:
        timewin = 0
    # create list of datetime instances
    timelst=[]
    ctime=[]
    cidx=[]
    idx=0
    if (edate is None or sdate==edate):
        for element in time:
            if basetime is None:
                tmp = element
            else:
                tmp = basetime + timedelta(seconds=element)
            timelst.append(tmp)
            # choose closest match within window of win[minutes]
            if (tmp >= sdate-timedelta(minutes=timewin)
            and tmp <= sdate+timedelta(minutes=timewin)):
                ctime.append(tmp)
                cidx.append(idx)
            del tmp
            idx=idx+1
    if (edate is not None and edate!=sdate):
        for element in time:
            if basetime is None:
                tmp = element
            else:
                tmp = basetime + timedelta(seconds=element)
            timelst.append(tmp)
            if (tmp >= sdate-timedelta(minutes=timewin)
            and tmp < edate+timedelta(minutes=timewin)):
                ctime.append(tmp)
                cidx.append(idx)
            del tmp
            idx=idx+1
    return ctime, cidx

def get_loc_idx(init_lats,init_lons,target_lat,target_lon,mask=None):
    from utils import haversine
    distM = np.zeros(init_lats.shape)*np.nan
    for i in range(init_lats.shape[0]):
        for j in range(init_lats.shape[1]):
            if mask is None:
                distM[i,j] = haversine(init_lons[i,j],init_lats[i,j],
                                    target_lon,target_lat)
            else:
                if isinstance(mask[i,j],(np.float32)):
                    distM[i,j] = haversine(init_lons[i,j],init_lats[i,j],
                                    target_lon,target_lat)
    idx,idy = np.where(distM==np.nanmin(distM))
    return idx, idy, distM, init_lats[idx,idy], init_lons[idx,idy]

# --- help ------------------------------------------------------------#
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
This module encompasses classes and methods to read and process wave
field related data from stations.\n
Usage:
from stationmod import station_class as sc
from datetime import datetime, timedelta
sc_obj = sc('ekofiskL',sdate,edate)
        """,
        formatter_class = RawTextHelpFormatter
        )
    args = parser.parse_args()
