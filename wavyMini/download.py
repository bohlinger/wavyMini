#!/usr/bin/env python
import time
from datetime import datetime, timedelta
from satmod import get_remotefiles
from pathfinder import downloadpath, satpath_ftp_014_001
import argparse
from argparse import RawTextHelpFormatter

# parser
parser = argparse.ArgumentParser(
    description="""
Download satellite netcdf from Copernicus DU.

Usage:
./download.py
./download.py -sat s3a -sd 2019090100 -ed 2019090200
    """,
    formatter_class = RawTextHelpFormatter
    )
parser.add_argument("-sd", metavar='startdate',
    help="start date of time period to be downloaded")
parser.add_argument("-ed", metavar='enddate',
    help="end date of time period to be downloaded")
parser.add_argument("-sat", metavar='satellite',
    help="source satellite mission")
parser.add_argument("-path", metavar='path',
    help="destination for downloaded data")
parser.add_argument("-nproc", metavar='nproc',
    help="number of simultaneous processes",type = int)

args = parser.parse_args()

now=datetime.now()
if args.sat is None:
    sat = 's3a'
else:
    sat = args.sat
if args.sd is None:
    sdate = datetime(now.year,now.month,now.day,now.hour)-timedelta(days=1)
else:
    sdate = datetime(int(args.sd[0:4]),int(args.sd[4:6]),
                int(args.sd[6:8]),int(args.sd[8:10]))

if args.ed is None:
    edate = datetime(now.year,now.month,now.day,now.hour,now.minute)
else:
    edate = datetime(int(args.ed[0:4]),int(args.ed[4:6]),
                int(args.ed[6:8]),int(args.ed[8:10]))

if args.path is None:
    targetpath = "tmp_wavyData/"
else:
    targetpath = args.path

if args.nproc is None:
    nproc = 1
else: 
    nproc = args.nproc

satpath = satpath_ftp_014_001 + sat
destination = targetpath + sat + '/'
print('source: ' + satpath)
print('destination: ' + destination)
start_time = time.time()
sa_obj = get_remotefiles(satpath, destination,
                        sdate,edate,timewin=30,
                        corenum=nproc,download=True)
time1 = time.time() - start_time
print("Time used for collecting data: ", time1, " seconds")
