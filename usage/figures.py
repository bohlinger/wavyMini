#!/usr/bin/env python
import sys
import os
home = os.path.expanduser("~")
wavypath = home + '/wavyMini/wavyMini'
sys.path.append(wavypath)

from graphicsmod import make_val_ts_fig_arcmfc, make_val_scatter_fig_arcmfc
from ncmod import get_coll_stats, get_coll_ts
from datetime import datetime, timedelta
import argparse
from argparse import RawTextHelpFormatter
from utils import grab_PID

# parser
parser = argparse.ArgumentParser(
    description="""
Plot simple validation figures.

Usage:
./figures.py -sd 2019100118 -ed 2019100118 -sat c2 -mod SWAN
    """,
    formatter_class = RawTextHelpFormatter
    )
parser.add_argument("-sd", metavar='startdate',
    help="start date of time period")
parser.add_argument("-ed", metavar='enddate',
    help="end date of time period")
parser.add_argument("-mod", metavar='model',
    help="wave model")
parser.add_argument("-sat", metavar='satellite',
    help="satellite mission")
parser.add_argument("-path", metavar='destination',
    help="destination of collocated data")

args = parser.parse_args()

now = datetime.now()

if args.sd is None:
    sdate = datetime(now.year,now.month,now.day)-timedelta(days=1)
else:
    sdate = datetime(int(args.sd[0:4]),int(args.sd[4:6]),
                int(args.sd[6:8]),int(args.sd[8:10]))
if args.ed is None:
    edate = datetime(now.year,now.month,now.day)-timedelta(hours=1)
else:
    edate = datetime(int(args.ed[0:4]),int(args.ed[4:6]),
                int(args.ed[6:8]),int(args.ed[8:10]))

if args.path is None:
    args.path = home + '/wavyMini/data'

# settings
fc_date = datetime.now()
forecasts = [0,6,12,18,24,30,36,42,48]
val_names = ['rmsd','bias','corr','SI','nov']

args.mod = 'SWAN'
args.sat = 'c2'

# Get stats ts
dtime_lst = []
rmsd_lst = []
bias_lst = []
corr_lst = []
SI_lst = []
nov_lst = []
for element in forecasts:
    try:
        inpath=(args.path + '/ValidationFiles/'
            + args.sat
            + fc_date.strftime('/%Y/%m/'))
        filename_stats = fc_date.strftime(args.mod
                                + "_vs_"
                                + args.sat
                                + "_val_ts_lt"
                                + "{:0>3d}".format(element)
                                + "h_%Y%m.nc")
        valid_dict, dtime = get_coll_stats(inpath + filename_stats)
        rmsd_lst.append(valid_dict['rmsd'])
        bias_lst.append(valid_dict['bias'])
        corr_lst.append(valid_dict['corr'])
        SI_lst.append(valid_dict['SI'])
        nov_lst.append(valid_dict['nov'])
        dtime_lst.append(dtime)
    except Exception as e:
        print(e)

valid_dict_lst = {'rmsd':rmsd_lst,
                  'bias':bias_lst,
                  'corr':corr_lst,
                  'SI':SI_lst,
                  'nov':nov_lst}

# Make ts-plots
for val_name in val_names:
    filename_fig = fc_date.strftime("fig_val" 
                            + "_ts_" + val_name
                            + "_%Y%m.png")
    ts = valid_dict_lst[val_name]
    make_val_ts_fig_arcmfc(val_name,ts,dtime_lst,filename_fig,forecasts)

# Get collocation ts
dtime_lst = []
sHs_lst = []
mHs_lst = []
for element in forecasts:
    try:
        inpath=(args.path + '/CollocationFiles/'
            + args.sat
            + fc_date.strftime('/%Y/%m/'))
        filename_coll = fc_date.strftime(args.mod
                                + "_vs_"
                                + sat
                                + "_coll_ts_lt"
                                + "{:0>3d}".format(element)
                                + "h_%Y%m.nc")
        dtime, sHs, mHs = get_coll_ts(inpath + filename_coll)
        dtime_lst.append(dtime)
        sHs_lst.append(sHs)
        mHs_lst.append(mHs)
    except Exception as e:
        print(e)

# Make scatter-plots
for i in range(len(forecasts)):
    filename_fig = fc_date.strftime("fig_val_scatter_lt"
                            + "{:0>3d}".format(forecasts[i])
                            + "h_%Y%m.png")
    make_val_scatter_fig_arcmfc(mHs_lst[i],sHs_lst[i],filename_fig,forecasts,i)

# clean up
outpath=(args.path + '/ValidationFigures/'
        + args.sat + '/'
        + fc_date.strftime('%Y') + '/' + fc_date.strftime('%m') + '/')
cmd = 'mkdir -p ' + outpath
os.system(cmd)
cmd = 'mv *fig_val*.png ' + outpath
os.system(cmd)
