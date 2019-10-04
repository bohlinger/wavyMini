#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------#
'''
This module encompasses classes and methods to read and process wave
field related data from satellites.
'''
# --- import libraries ------------------------------------------------#
'''
List of libraries needed for this class.
'''
# progress bar and other stuff
import sys

# all class
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
import argparse
from argparse import RawTextHelpFormatter
import os

# get_altim
if sys.version_info <= (3, 0):
    from urllib import urlretrieve, urlcleanup # python2
else:
    from urllib.request import urlretrieve, urlcleanup # python3
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

# get_remote
from dateutil.relativedelta import relativedelta
from copy import deepcopy

import time

# get necessary paths for module
import pathfinder

# region spec
from region_specs import poly_dict, region_dict
# --- global functions ------------------------------------------------#

def progress(count, total, status=''):
    "from: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3"
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def credentials_from_netrc():
    import netrc
    import os.path
    # get user home path
    usrhome = os.getenv("HOME")
    netrc = netrc.netrc()
    remoteHostName = "nrt.cmems-du.eu"
    user = netrc.authenticators(remoteHostName)[0]
    pw = netrc.authenticators(remoteHostName)[2]
    return user, pw

def credentials_from_txt():
    import os.path
    print("try local file credentials.txt")
    # get user home path
    usrhome = os.getenv("HOME")
    my_dict = {}
    with open(usrhome + "/credentials.txt", 'r') as f:
        for line in f:
            items = line.split('=')
            key, values = items[0], items[1]
            my_dict[key] = values
    # 1:-2 to remove the linebreak and quotation marks \n
    user = my_dict['user'][1:-2]
    pw = my_dict['pw'][1:-2]
    print("user:" + user)
    return user, pw

def get_credentials():
    # get credentials from .netrc
    import os.path
    usrhome = os.getenv("HOME")
    if os.path.isfile(usrhome + "/.netrc"):
        try:
            print ('Attempt to obtain credentials from .netrc')
            user, pw = credentials_from_netrc()
            return user, pw
        except AttributeError:
            print ("std copernicus user in netrc file not registered")
            print ("try local file credentials.txt")
            print ("file must contain:")
            print ("user='username'")
            print ("pw='yourpassword'")
            except_key = 1
    elif (os.path.isfile(usrhome + "/.netrc") == False
    or except_key == 1):
        try:
            user, pw = credentials_from_txt()
            return user, pw
        except:
            print("Credentials could not be obtained")

def tmploop_get_remotefiles(i,matching,user,pw,
                            server,path,destination):
    #for element in matching:
    print("File: ",matching[i])
    dlstr=('ftp://' + user + ':' + pw + '@' 
                + server + path + matching[i])
    for attempt in range(10):
        print("destination: " + destination)
        try:
            print ("Downloading file")
            urlretrieve(dlstr, destination + matching[i])
            urlcleanup()
        except Exception as e:
            print (e.__doc__)
            print (e.message)
            print ("Waiting for 10 sec and retry")
            time.sleep(10)
        else:
            break
    else:
        print ('An error was raised and I ' + 
              'failed to fix the problem myself :(')
        print ('Exit program')
        sys.exit()

def get_remotefiles(satpath,destination,sdate,edate,timewin,
                    corenum,download):
    '''
    Download swath files and store them at defined location
    time stamps in file name stand for: from, to, creation
    '''
    if download is None:
        print ("No download initialized, checking local files")
        return
    # credentials
    user, pw = get_credentials()
    tmpdate = deepcopy(sdate)
    pathlst = []
    filelst = []
    while (tmpdate <= edate):
        # server and path
        if sdate >= datetime(2017,7,9):
            server='nrt.cmems-du.eu'
            path=(satpath
                 + '/'
                 + str(tmpdate.year)
                 + '/'
                 + tmpdate.strftime('%m')
                 + '/')
            print ('# ----- ')
            print ('Chosen product: ')
            print ('WAVE_GLO_WAV_L3_SWH_NRT_OBSERVATIONS_014_001')
            print ('# ----- ')
        else:
            sys.exit("Product not available for chosen date!")
        # get list of accessable files
        ftp = FTP(server)
        ftp.login(user, pw)
        ftp.cwd(path)
        content=FTP.nlst(ftp)
        #choose files according to verification date
        tmplst=[]
        tmpdate_new=tmpdate-timedelta(minutes=timewin)
        tmpend=edate+timedelta(minutes=timewin)
        while (tmpdate_new.strftime("%Y%m%dT%H")
            <= tmpend.strftime("%Y%m%dT%H")):
            matchingtmp = [s for s in content
                            if ('_'
                            + str(tmpdate_new.year)
                            + str(tmpdate_new)[5:7]
                            + str(tmpdate_new)[8:10]
                            + 'T'
                            + str(tmpdate_new)[11:13])
                            in s
                            ]
            tmplst = tmplst + matchingtmp
            tmpdate_new = tmpdate_new + timedelta(minutes=timewin)
        matching = tmplst
        print ("Download initiated")
        # Download and gunzip matching files
        print ('Downloading ' + str(len(matching)) + ' files: .... \n')
        print ("Used number of cores " + str(corenum) + "!")
        os.system("mkdir -p " + destination)
        Parallel(n_jobs=corenum)(
                        delayed(tmploop_get_remotefiles)(
                        i,matching,user,pw,server,
                        path,destination
                        ) for i in range(len(matching))
                        )
        # update time
        tmpdate = datetime((tmpdate + relativedelta(months=+1)).year,(tmpdate + relativedelta(months=+1)).month,1)
    print ('Files downloaded to: \n' + destination)
    print('Organizing downloaded files in year and month')
    from os.path import expanduser
    home = expanduser("~")
    os.system('cd ' + destination 
            + ' && python '
            + home
            + '/wavyMini/wavyMini/sort.py')

# flatten all lists before returning them
# define flatten function for lists
''' fct does the following:
flat_list = [item for sublist in TIME for item in sublist]
or:
for sublist in TIME:
for item in sublist:
flat_list.append(item)
'''
flatten = lambda l: [item for sublist in l for item in sublist]

def check_date(filelst,date):
    '''
    returns idx for file
    '''
    # check if str in lst according to wished date (sdate,edate)
    idx = []
    for i in range(len(filelst)):
        element = filelst[i]
        tmp = element.find(date.strftime('%Y%m%d'))
        if tmp>=0:
            #return first index available
            idx.append(i)
    return idx[0],idx[-1]

# ---------------------------------------------------------------------#


class satellite_altimeter():
    '''
    class to handle netcdf files containing satellite altimeter derived
    level 3 data i.e. Hs[time], lat[time], lon[time] 
    This class offers the following added functionality:
     - get swaths of desired days and read
     - get the closest time stamp(s)
     - get the location (lon, lat) for this time stamp
     - get Hs value for this time
    '''
    satpath_copernicus = pathfinder.satpath_copernicus
    from region_specs import region_dict

    def __init__(self,sdate,sat=None,edate=None,timewin=None,download=None,
        region=None,corenum=None,mode=None,polyreg=None,destination=None):
        if sat is None:
            sat = 's3a'
        print ('# ----- ')
        print (" ### Initializing satellite_altimeter instance for "
                + sat + " ###")
        print ('# ----- ')
        if corenum is None:
            corenum = 1
        if edate is None:
            print ("Requested time: ", str(sdate))
            edate = sdate
            if timewin is None:
                timewin = int(30)
        else:
            print ("Requested time frame: " + 
                str(sdate) + " - " + str(edate))
        # make satpaths
        if destination is None:
            destination = pathfinder.downloadpath
        destination = destination + '/' + sat + '/'
        satpath_ftp_014_001 = (pathfinder.satpath_ftp_014_001 
                            + 'dataset-wav-alti-l3-swh-rt-global-' 
                            +  sat + '/'
                            )
        self.destination = destination
        # retrieve files
        os.system("mkdir -p " + destination)
        get_remotefiles(satpath_ftp_014_001,destination,
                        sdate,edate,timewin,corenum,download)
        pathlst, filelst = self.get_localfilelst(
                                sdate,edate,timewin,region
                                )
        fLATS,fLONS,fTIME,fVAVHS,fMAXS,fVAVHS_smooth = \
                                    self.read_localfiles(pathlst)
        idx = np.array(range(len(fVAVHS)))[~np.isnan(fVAVHS)]
        fLATS = list(np.array(fLATS)[idx])
        fLONS = list(np.array(fLONS)[idx])
        fTIME = list(np.array(fTIME)[idx])
        fVAVHS = list(np.array(fVAVHS)[idx])
        fVAVHS_smooth = list(np.array(fVAVHS_smooth)[idx])
        gloc = [fLATS,fLONS]
        gHs = fVAVHS
        gHs_smooth = fVAVHS_smooth
        # find values for give time constraint
        ctime,cidx,timelst = self.matchtime(sdate,edate,fTIME,timewin)
        cloc = [np.array(fLATS)[cidx],np.array(fLONS)[cidx]]
        cHs = list(np.array(gHs)[cidx])
        cHs_smooth = list(np.array(gHs_smooth)[cidx])
        cTIME = list(np.array(fTIME)[cidx])
        # find values for given region
        latlst,lonlst,rlatlst,rlonlst,ridx,region = \
            self.matchregion(cloc[0],cloc[1],region=region,\
            polyreg=polyreg)
        rloc = [cloc[0][ridx],cloc[1][ridx]]
        rHs = list(np.array(cHs)[ridx])
        rHs_smooth = list(np.array(cHs_smooth)[ridx])
        rtime = list(np.array(ctime)[ridx])
        rTIME = list(np.array(cTIME)[ridx])
        self.edate = edate
        self.sdate = sdate
        self.basetime = datetime(2000,1,1)
        self.loc = rloc # regional coords [lats,lons]
        self.Hs = rHs # regional HS
        self.Hs_smooth = rHs_smooth # region smoothed ts
        self.idx = ridx # region indices
        self.dtime = rtime # region time steps as datetime obj
        self.time = rTIME # region time steps in seconds from basedate
        self.timewin = timewin
        self.region = region
        self.sat = sat
        print ("Satellite object initialized including " 
                + str(len(self.Hs)) + " footprints.")

    def get_localfilelst(self,sdate,edate,timewin,region):
        print ("Time window: ", timewin)
        tmpdate=deepcopy(sdate-timedelta(minutes=timewin))
        pathlst = []
        filelst = []
        while (tmpdate <= edate + timedelta(minutes=timewin)):
            tmpdatestr=(self.destination
                        + str(tmpdate.year)
                        + '/' + tmpdate.strftime('%m')
                        + '/')
            tmplst = np.sort(os.listdir(tmpdatestr))
            filelst.append(tmplst)
            #pathlst = [(tmpdatestr + e) for e in tmplst]
            pathlst.append([(tmpdatestr + e) for e in tmplst])
            if (edate is not None and edate!=sdate):
                tmpdate = tmpdate + timedelta(hours=1)
            else:
                tmpdate = tmpdate + relativedelta(months=+1)
        filelst=np.sort(flatten(filelst))
        pathlst=np.sort(flatten(pathlst))
        idx_start,tmp = check_date(pathlst,sdate-timedelta(minutes=timewin))
        tmp,idx_end = check_date(pathlst,edate+timedelta(minutes=timewin))
        del tmp
        pathlst = np.unique(pathlst[idx_start:idx_end+1])
        filelst = np.unique(filelst[idx_start:idx_end+1])
        print (str(int(len(pathlst))) + " valid files found")
        return pathlst,filelst

    def read_localfiles(self,pathlst):
        '''
        read and concatenate all data to one timeseries for each variable
        '''
        from utils import runmean
        # --- open file and read variables --- #
        LATS = []
        LONS = []
        VAVHS = []
        TIME = []
        MAXS = []
        count = 0
        print ("Processing " + str(int(len(pathlst))) + " files")
        print (pathlst[0])
        print (pathlst[-1])
        for element in pathlst:
            progress(count,str(int(len(pathlst))),'')
            try:
                # file includes a 1-D dataset with dimension time
                f = netCDF4.Dataset(element,'r')
                tmp = f.variables['longitude'][:]
                # transform
                lons = ((tmp - 180) % 360) - 180
                lats = f.variables['latitude'][:]
                time = f.variables['time'][:]
                VAVH = f.variables['VAVH'][:]
                f.close()
                LATS.append(lats)
                LONS.append(lons)
                TIME.append(time)
                VAVHS.append(VAVH)
                MAXS.append(np.max(VAVH.astype('float')))
            except (IOError):
                print ("No such file or directory")
            count = count + 1
        print ('\n')
        # apply flatten to all lists
        fTIME,fLATS,fLONS,fVAVHS,fMAXS=\
            flatten(TIME),flatten(LATS),flatten(LONS),\
            flatten(VAVHS),MAXS
        fTIME_unique,indices=np.unique(fTIME,return_index=True)
        fLATS=list(np.array(fLATS)[indices])
        fLONS=list(np.array(fLONS)[indices])
        fTIME=list(np.array(fTIME)[indices])
        fVAVHS=list(np.array(fVAVHS)[indices])
        # smooth Hs time series
        fVAVHS_smooth,fVAVHS_std = runmean(fVAVHS,5,'centered')
        return fLATS, fLONS, fTIME, fVAVHS, fMAXS, fVAVHS_smooth

    def bintime(self,binframe=None):
        '''
        fct to return frequency of occurrence per chose time interval
        e.g. days, weeks, months, years ...
        currently only daily bins
        '''
        listofdatetimes=self.rtime
        listofdatetimes_sec=self.rTIME
        sdate=listofdatetimes[0]
        edate=listofdatetimes[-1]
        trange=int(math.ceil((edate-sdate).total_seconds()/60./60./24.))
        freqlst=[]
        datelst=[]
        dincr=0
        timewin = 0
        for i in range(trange):
            lodt=sdate+timedelta(days=dincr)
            ctime,cidx,timelst = self.matchtime(
                                    datetime(lodt.year,lodt.month,lodt.day),
                                    datetime(lodt.year,lodt.month,lodt.day)
                                    +timedelta(days=1),
                                    listofdatetimes_sec,
                                    timewin = timewin)
            count=len(np.array(self.rHs)[
                                cidx][
                                ~np.isnan(np.array(self.rHs)[cidx])
                                     ]
                    )
            freqlst.append(count)
            dincr=dincr+1
            datelst.append(lodt)
        return freqlst,datelst

    def matchtime(self,sdate,edate,fTIME,timewin=None):
        '''
        fct to obtain the index of the time step closest to the 
        requested time step from buoy and forecast including the 
        respective time stamp(s). Similarily, indices are chosen
        for the time and defined region.
        '''
        if timewin is None:
            timewin = 0
        basetime=datetime(2000,1,1)
        # create list of datetime instances
        timelst=[]
        ctime=[]
        cidx=[]
        idx=0
        print ('Time window is: ', timewin)
        if (edate is None or sdate==edate):
            for element in fTIME:
                tmp=basetime + timedelta(seconds=element)
                timelst.append(tmp)
                # choose closest match within window of win[minutes]
                if (tmp >= sdate-timedelta(minutes=timewin) 
                and tmp < sdate+timedelta(minutes=timewin)):
                    ctime.append(tmp)
                    cidx.append(idx)
                del tmp
                idx=idx+1
        if (edate is not None and edate!=sdate):
            for element in fTIME:
                tmp=basetime + timedelta(seconds=element)
                timelst.append(tmp)
                if (tmp >= sdate-timedelta(minutes=timewin)
                and tmp < edate+timedelta(minutes=timewin)):
                    ctime.append(tmp)
                    cidx.append(idx)
                del tmp
                idx=idx+1
        return ctime, cidx, timelst

    def matchregion(self,LATS,LONS,region,polyreg):
        # find values for given region
        if polyreg is None:
            if region is None:
                region = 'Global'
            if ~isinstance(region,str)==True:
                print ("Manuall specified region "
                    + [llcrnrlat,urcrnrlat,llcrnrlon,urcrnrlon] + ": \n"
                    + " --> Bounds: " + str(region))
            else:
                if region not in region_dict.keys():
                    sys.exit("Region is not defined")
                else:
                    print ("Specified region: " + region + "\n"
                      + " --> Bounds: " + str(self.region_dict[region]))
            latlst,lonlst,rlatlst,rlonlst,ridx = \
                self.matchregion_prim(LATS,LONS,region=region)
        else:
            region = polyreg
            latlst,lonlst,rlatlst,rlonlst,ridx = \
                self.matchregion_poly(LATS,LONS,region=region)
        return latlst, lonlst, rlatlst, rlonlst, ridx, region

    def matchregion_prim(self,LATS,LONS,region):
        if (region is None or region == "Global"):
            region = "Global"
            latlst = LATS
            lonlst = LONS
            rlatlst= LATS
            rlonlst= LONS
            ridx = range(len(LATS))
        else:
            if isinstance(region,str)==True:
                if (region=='ARCMFC' or region=='Arctic'):
                    boundinglat = self.region_dict[region]["boundinglat"]
                else:
                    llcrnrlat = self.region_dict[region]["llcrnrlat"]
                    urcrnrlat = self.region_dict[region]["urcrnrlat"]
                    llcrnrlon = self.region_dict[region]["llcrnrlon"]
                    urcrnrlon = self.region_dict[region]["urcrnrlon"]
            else:
                llcrnrlat = region[0]
                urcrnrlat = region[1]
                llcrnrlon = region[2]
                urcrnrlon = region[3]
            # check if coords in region
            latlst=[]
            lonlst=[]
            rlatlst=[]
            rlonlst=[]
            ridx=[]
            for i in range(len(LATS)):
                latlst.append(LATS[i])
                lonlst.append(LONS[i])
                if (
                (region=='ARCMFC' or region=='Arctic')
                and LATS[i] >= boundinglat
                    ):
                    rlatlst.append(LATS[i])
                    rlonlst.append(LONS[i])
                    ridx.append(i)
                elif(
                region != 'ARCMFC' and region != 'Arctic'
                and LATS[i] >= llcrnrlat
                and LATS[i] <= urcrnrlat
                and LONS[i] >= llcrnrlon
                and LONS[i] <= urcrnrlon
                    ):
                    rlatlst.append(LATS[i])
                    rlonlst.append(LONS[i])
                    ridx.append(i)
        if not ridx:
            print ("No values for chosen region and time frame!!!")
        else:
            print ("Values found for chosen region and time frame.")
        return latlst, lonlst, rlatlst, rlonlst, ridx

    def matchregion_poly(self,LATS,LONS,region):
        from matplotlib.patches import Polygon
        from matplotlib.path import Path
        import numpy as np
        from model_specs import model_dict
        if (region not in poly_dict.keys() \
            and region not in model_dict.keys()):
            sys.exit("Region is not defined")
        elif isinstance(region,dict)==True:
            print ("Manuall specified region: \n"
                + " --> Bounds: " + str(region))
            poly = Polygon(list(zip(region['lons'],
                region['lats'])), closed=True)
        elif (isinstance(region,str)==True and region in model_dict.keys()):
            from modelmod import get_model
            import pyproj
            if region == 'mwam8':
                grid_date = datetime(2019,2,1,6)
            elif region == 'ww3':
                grid_date = datetime(2018,12,27,12)
            elif (region == 'MoskNC' or region == 'MoskWC'):
                grid_date = datetime(2018,3,1)
            elif (region == 'swanKC'):
                grid_date = datetime(2007,2,1)
            elif (region == 'swan_karmoy250'):
                grid_date = datetime(2018,1,1)
            elif (region == 'ARCMFC3'):
                grid_date = datetime(2019,7,3)
            else:
                grid_date = datetime(2019,2,1)
            if (region == 'ARCMFC' or region=='ARCMFC3'):
                model_Hs,model_lats,model_lons,model_time,model_time_dt = \
                    get_model(simmode="fc", model=region, fc_date=grid_date,
                    init_date=grid_date)
            else:
                model_Hs,model_lats,model_lons,model_time,model_time_dt = \
                    get_model(simmode="fc", model=region, fc_date=grid_date,
                    leadtime=0)
            if (region == 'swanKC' or region == 'swan_karmoy250'):
                model_lats, model_lons = np.meshgrid(model_lats, model_lons)
            proj4 = model_dict[region]['proj4']
            proj_model = pyproj.Proj(proj4)
            Mx, My = proj_model(model_lons,model_lats,inverse=False)
            Vx, Vy = proj_model(LONS,LATS,inverse=False)
            xmax, xmin = np.max(Mx), np.min(Mx)
            ymax, ymin = np.max(My), np.min(My)
            ridx = list(np.where((Vx>xmin) & (Vx<xmax) & 
                                (Vy>ymin) & (Vy<ymax))[0]
                        )
            latlst, lonlst = LATS, LONS
            rlatlst, rlonlst = LATS[ridx], LONS[ridx]
        elif isinstance(region,str)==True:
            print ("Specified region: " + region + "\n"
              + " --> Bounded by polygon: \n"
              + "lons: " + str(poly_dict[region]['lons']) + "\n"
              + "lats: " + str(poly_dict[region]['lats']))
            poly = Polygon(list(zip(poly_dict[region]['lons'],
                poly_dict[region]['lats'])), closed=True)
            # check if coords in region
            LATS = list(LATS)
            LONS = list(LONS)
            latlst = LATS
            lonlst = LONS
            lats = np.array(LATS).ravel()
            lons = np.array(LONS).ravel()
            points = np.c_[lons,lats]
            hits = Path(poly.xy).contains_points(points)
            rlatlst = list(np.array(LATS)[hits])
            rlonlst = list(np.array(LONS)[hits])
            ridx = list(np.array(range(len(LONS)))[hits])
        if not ridx:
            print ("No values for chosen region and time frame!!!")
        else:
            print ("Values found for chosen region and time frame.")
        return latlst, lonlst, rlatlst, rlonlst, ridx


def get_pointsat(sa_obj,station=None,lat=None,lon=None,distlim=None):
    from utils import haversine
    from stationlist import locations
    if ((lat is None or lon is None) and (station is None)):
        print ("location is missing")
    if (lat is None or lon is None):
        lat=locations[station][0]
        lon=locations[station][1]
    lats = sa_obj.loc[0]
    lons = sa_obj.loc[1]
    Hs = sa_obj.Hs
    time = sa_obj.time
    sample = []
    dists = []
    for i in range(len(lats)):
        if ((lats[i] < lat+1) and (lats[i] > lat-1)):
            if ((lons[i] < lon+1) and (lons[i] > lon-1)):
                dist=haversine(lons[i],lats[i],lon,lat)
                if (dist<=distlim):
                    sample.append(Hs[i])
                    dists.append(dist)
    return sample, dists
