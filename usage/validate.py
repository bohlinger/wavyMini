#!/usr/bin/env python
import sys
import os
home = os.path.expanduser("~")
wavypath = home + '/wavyMini/wavyMini'
sys.path.append(wavypath)

from datetime import datetime, timedelta
from satmod import satellite_altimeter as sa
from stationmod import matchtime
from modelmod import get_model
from collocmod import collocate
from validationmod import validate
from copy import deepcopy
from model_specs import model_dict
from ncmod import dumptonc_stats
import argparse
from argparse import RawTextHelpFormatter
from utils import grab_PID

# parser
parser = argparse.ArgumentParser(
    description="""
Validate wave model output against s3a data and dump to monthly nc-file.
If file exists, data is appended.

Usage:
./validate.py -sd 2019100118 -ed 2019100118 -sat c2 -mod SWAN
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
    help="satellite mission [s3a,s3b,c2,j3,al]")
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

model = args.mod

# retrieve PID
grab_PID()

tmpdate = deepcopy(sdate)

#forecasts = [12, 36, 60, 84, 108, 132, 156, 180, 204, 228]
forecasts = [6,12,24,30,36,42,48]

while tmpdate <= edate:
    print(tmpdate)
    for element in forecasts:
        # settings
        fc_date = deepcopy(tmpdate)
        basetime=model_dict[model]['basetime']
        # get model collocated values
        from ncmod import get_coll_ts
        inpath = (args.path + '/CollocationFiles/'
                + args.sat
                + fc_date.strftime('/%Y/%m/'))
        filename_ts=fc_date.strftime(model
                                    + "_vs_"
                                    + args.sat
                                    + "_coll_ts_lt"
                                    + "{:0>3d}".format(element)
                                    + "h_%Y%m.nc")
        print(inpath)
        print(filename_ts)
        try:
            dtime, sHs, mHs = get_coll_ts(inpath + filename_ts)
            del filename_ts
            # find collocations for given model time step and validate
            from stationmod import matchtime
            time_lst = []
            for dt in dtime:
                time_lst.append((dt-basetime).total_seconds())
            ctime,idx = matchtime(tmpdate, tmpdate, time_lst, basetime, timewin=30)
            if len(idx)==0:
                pass
            else:
                results_dict = {'date_matches':dtime[idx],
                        'model_Hs_matches':mHs[idx],
                        'sat_Hs_matches':sHs[idx]}
                valid_dict=validate(results_dict)
                print(valid_dict)
                # dump to nc-file: validation
                outpath=(args.path + '/ValidationFiles/'
                    + args.sat
                    + fc_date.strftime('/%Y/%m/'))
                os.system('mkdir -p ' + outpath)
                title_stat='validation file'
                filename_stat=fc_date.strftime(model
                                        + "_vs_"
                                        + args.sat
                                        + "_val_ts_lt"
                                        + "{:0>3d}".format(element)
                                        + "h_%Y%m.nc")
                time_dt = fc_date
                dumptonc_stats(outpath,filename_stat,title_stat,basetime,
                          time_dt,valid_dict)
        except Exception as e:
            print(e)
    tmpdate = tmpdate + timedelta(hours=6)
