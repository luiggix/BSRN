'''
    Stage7.Cpp
    
    Stage 7 (BSRN File Conversion)
        
    
    This is the actual QC routine that the windows programmes uses
    
    By Vorpal Bunny and Psychic Wombat
    
    Last Edit: 11 Aug MCMXCIX
    
    Routines:
        Stage7QC()
        CreateLR0008()
        WriteLR0001()
        WriteLR0002()
        WriteLR0004()
        WriteLR0007()
        WriteLR0008()
        WriteLR0009()
        WriteLR0100()

        WriteLocialRecord0003() ?
        WriteLocialRecord0005() x
        WriteLocialRecord0006() x
        WriteLocialRecord0200() x
        WriteLocialRecord0300() x
        WriteLocialRecord0400() x
        WriteLocialRecord1000() x
        WriteLocialRecord1100() x
        WriteLocialRecord1200() x
        WriteLocialRecord1300() x
        WriteLocialRecord1400() x
        WriteLocialRecord1500() x




        Edits:

        18 Apr 2000: It was looking for .txt file in the wrong place. It now uses the .minTXT
                     file and looks in the correct directory.  PWD

        10 May 2000: Program had assumed that each entry in the cal file corresponded to a new
                     calibration. With the new cal format an entry can correspond to an instrument
                     going off line or on line. This caused an error for the first cal info.
                     The program now looks back in time to when the instruments were last
                     calibrated.   PWD

          10 May 2000: change from coords rel to (equator, Greenwich) to
                     coord rel to (S pole, 180 W of Greenwich)         PWD 

        10 May 2000: program now outputs using GMT, not local time. Program is for East of
                     Greenwich. If West of Greenwich then extra code would need to be written. PWD
                     
        Apr 2009: converted to python. pwd
'''

import sys
import os

if sys.platform == 'win32':
	MP = r'\\memsat'
else:
	MP = os.sep + 'media' 

import datetime
import os
import ConfigParser
from xml.dom import minidom, Node

from SolarFiles import ConfigFile, ReportFile
import ScreenOutput

EOL = '\r\n' #use windows end of line

PREFIX = {801:'asp',
          701:'lau',
          803:'dwn',
          925:'coc'}

MONTHNAME = ['', 'Jan', 'Feb', 'Mar',
             'Apr', 'May', 'Jun', 
             'Jul', 'Aug', 'Sep',
             'Oct', 'Nov', 'Dec', 'ALL']

GLO = 'GLO'
DIR = 'DIR'
DIF = 'DIF'
TER = 'TER'

INSTRUMENTS = (GLO, DIR, DIF, TER)

QUANTITIES = ('Global', 'Direct', 'Diffuse', 'Longwave')

class NoReportFileError: pass
class StageNotDoneError: pass
class NoCalFileError: pass
class BadLongitudeError: pass


class SiteInfo:
    def __init__(self, fname):
        self.data = open(fname).readlines()
    
    def get(self, radnum):
        nextline = self.data[1:]
        for d, n in zip(self.data, nextline):
            if d.startswith(str(radnum)):
                return dict(radnum=d[0:3],
                            bureaunum=d[3:11],
                            wnonum=d[11:19],
                            name=d[20:40],
                            nccnum=d[40:42],
                            latdeg=int(float(n[0:6])), # can't int number ending in decimal point e.g. '42.' so float it first
                            latmin=float(n[6:12]),
                            londeg=int(float(n[12:18])),
                            lonmin=float(n[18:24]),
                            tzlon=float(n[24:30]),
                            gmtoffset=float(n[30:36]),
                            elevation=int(float(n[36:42])),                            
                            )
              
class MinTxt:
    '''
    read and interact with the data from the mintxt files
    '''
    def __init__(self, fname, date):
        self.ini = ConfigParser.ConfigParser()
        self.nofile = False
        try:
            self.ini.readfp(open(fname))
        except IOError:
            self.nofile = True
        self.date = date
        self.daynum = int(date.strftime('%j'))
        self.quantities = self.get_quantities() # store settings of quantities as True or False from mintxt file

    def get_quantities(self):
        '''
        is the quantity set to True in the mintxt file
        '''
        if self.nofile:
            return {} # no file so nothing will be True
        ret = {}
        for q in QUANTITIES:
            if self.ini.get('Quantities Done', q) == 'TRUE':
                ret[q] = True
            else:
                ret[q] = False
        return ret
       
    def get_minutedata(self, quantity, minute):
        if (quantity not in self.quantities) or (not self.quantities[quantity]):
            #print 'no %s for day %s minute %s' % (quantity, self.date.strftime('%Y-%m-%d'), minute)
            return -999, -99.9, -999, -999
        try:    
            line = self.ini.get('Irradiance Values Day %03i - %s' % (self.daynum, quantity),
							    'min%03d' % minute)
        except ConfigParser.NoOptionError:
        	# no data for this minute so assume sun is down
            return 0, 0.0, 0, 0        	
        if line[0] == '(':
            return -999, -99.9, -999, -999
        s = line.split()[1:5]
        
        for i in range(len(s)):
            s[i] = float(s[i])
            if i != 1:
                if s[i] < -998:
                    s[i] = -999
                elif s[i] < 0:
                      s[i] = 0
                elif s[i] > 9999.9:
                      s[0] = -999
        #stdev a special case
        if s[1] < -98.9:
            s[1] = -99.9
        elif s[0]==s[2] and s[0]==s[3] and s[0] != 0:
            if s[0] > -998:
                s[1] = 0
            else:
                s[1] = -99.9
        elif s[1] > 999.9:
            s[1] = -99.9
                    
        return s
       
class BSRN:
    '''
    read and interact with the data from the file bsrn.ini
    for BSRN stations
    '''
    def __init__(self, fname):
        self.ini = ConfigParser.ConfigParser()
        self.ini.readfp(open(fname))

class SensorsXML:
    '''
    read and interact with the data from the file sensors.xml
    for BSRN stations
    '''
    def __init__(self, fname='', xmltext='', tagname='sensor', id='serial_number', defaultname='default'):
  
        if xmltext:
            dom1 = minidom.parseString(xmltext)
        else:
            st = open(fname).read()
            dom1 = minidom.parseString(st)
            #dom1 = minidom.parse(fname)

        default = dom1.getElementsByTagName(defaultname)

        defaultdict = self._getcontent(default[0])
        
        stations = dom1.getElementsByTagName(tagname)
        
        self._data = {} # dict of station numbers:stationdata
        
        for s in stations:
            ser = (s.getElementsByTagName(id)[0].childNodes[0].data).strip()
            self._data[ser] = self._getcontent(s)

        # add in default values
        for s,v in self._data.iteritems():
            for k in defaultdict:
                if k not in v:
                    v[k] = defaultdict[k]

            # default values for the calibrations
            for cal in v['calibration']:
                for k in defaultdict['calibration'][0]:
                    if k not in cal:
                        cal[k] = defaultdict['calibration'][0][k]
                
            
        self._orderdata()
                                    
    def _getcontent(self, node):
        '''
        recursively get the content of a node
        returning it as a dict of dicts of ....  of text
        
        can't deal with a node having both text and children
        can't deal with attributes
        '''
        ret = []
        retdict = {}
        for child in node.childNodes:
            if child.nodeType == Node.TEXT_NODE:
                ret.append((child.nodeValue).strip())
            elif child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName in retdict:
                    retdict[child.nodeName].append(self._getcontent(child))
                else:
                    retdict[child.nodeName] = [self._getcontent(child)]
        if retdict: #if have nodes then return the nodes (ignore any text)
            return retdict    
        return ''.join(ret) #return the text

#    def __init__(self, fname):
#        self._ini = ConfigParser.ConfigParser()
#        self._ini.readfp(open(fname))
#        self._ordered = self._orderdata()
        
    def todatetime(self, dte, tme):
        return datetime.datetime(int(dte[6:10]), int(dte[3:5]), int(dte[0:2]), int(tme[0:2]), int(tme[3:5]))
    
    def getsensorsections(self):
        return self._data.keys()

    def getcaltimes(self):
        '''
        ret = 20042570800 : ['CM11-924691', 'DN5-5015', 'CM11-924031'],
              20042571900 : ['PIR-33693F3'],
              etc
              
        ret2 ='CM11-924691' : [20042570800, 20042571900]
        '''
        ret = {}
        ret2 = {}
        for sensor, val in self._data.iteritems():
            for i, c in enumerate(val['calibration']):
                tagdt = self.todatetime(c['date'][0], c['time'][0])
                if tagdt not in ret:
                    ret[tagdt] = []
                ret[tagdt].append(sensor)
                if sensor not in ret2:
                    ret2[sensor] = [] 
                ret2[sensor].append({'time':tagdt, 'calno':i})
        return ret, ret2
    
    def _orderdata(self):
        self._calbytime, self._calbyserial = self.getcaltimes()
        '''
        tags = self._calbytime.keys()
        tags.sort()
        for t in tags:
            print t, self._calbytime[t]
            
        tags = self._calbyserial.keys()
        tags.sort()
        for t in tags:
            print t, self._calbyserial[t]
        '''    

    def store_cal_if_most_recent_cal_before_date(self, ret, date, ser, v):
        if v['time'] < date: # is this cal before date?
            if ser not in ret: # have not yet stored a cal for this ser, so store it
                ret[ser] = v
            elif ret[ser]['time'] < v['time']: # is this cal more recent than previously stored cal?
                ret[ser] = v
        return ret
    
    def get_record(self, date):
        '''
        return all the records for a given date
        '''
        ret = {}
#        print 'in get record',date
        for ser, val in self._calbyserial.iteritems():
            for v in val:
                ret = self.store_cal_if_most_recent_cal_before_date(ret, date, ser, v)
        return ret

    def get_cal(self, serial, calno):
        return self._data[serial]['calibration'][calno]['mean_calibration_coefficent_band_1'][0]
    
    def get_calibration_all(self, serial, calno):
        '''
        return all the data from a [Calibration <serialnumber> <calibrationnumber>] section as a dict
        note ConfigParser converts all tags to lowercase
        
        all things are stored as the 0th elements of a list, so get out of that
        '''
        ret = {}
        for k,v in self._data[serial]['calibration'][calno].iteritems():
            ret[k] = v[0]
        return ret

    def get_sensor_all(self, serial):
        '''
        return all the data from a [Sensor <serialnumber>] section as a dict
        note ConfigParser converts all tags to lowercase

        all things are stored as the 0th elements of a list (except calibration), so get out of that
        '''
        ret = {}
        for k,v in self._data[serial].iteritems():
            if k != 'calibration':
                ret[k] = v[0]
            else:
                ret[k] = v
        return ret
        
class Sensors:
    '''
    no longer used

    read and interact with the data from the file sensors.ini
    for BSRN stations
    
    '''

    def __init__(self, fname):
        self._ini = ConfigParser.ConfigParser()
        self._ini.readfp(open(fname))
        self._orderdata()
        
    def todatetime(self, dt):
        return datetime.datetime(int(dt[0:4]), 1, 1, int(dt[7:9]), int(dt[9:11])) + datetime.timedelta(days=int(dt[4:7]))
    
    def getsensorsections(self):
        sensorsecs = []         
        for s in self._ini.sections():
            if s.startswith('Sensor'):
                sensorsecs.append(s)
        return sensorsecs

    def getcaltimes(self):
        '''
        ret = 20042570800 : ['CM11-924691', 'DN5-5015', 'CM11-924031'],
              20042571900 : ['PIR-33693F3'],
              etc
              
        ret2 ='CM11-924691' : [20042570800, 20042571900]
        '''
        ret = {}
        ret2 = {}
        sensorsecs = self.getsensorsections()
        for s in sensorsecs:
            items = self._ini.items(s)
            for it in items:
                tag = it[0]
                if len(tag) == 11 and tag[0] in ('1', '2'):
                    tagdt = self.todatetime(tag)
                    sensor = s[7:] # serial number is after 'Sensor '
                    if tagdt not in ret:
                        ret[tagdt] = []
                    ret[tagdt].append(sensor)
                    if sensor not in ret2:
                        ret2[sensor] = [] 
                    ret2[sensor].append({'time':tagdt, 'calno':it[1]})
        return ret, ret2
    
    def _orderdata(self):
        self._calbytime, self._calbyserial = self.getcaltimes()
        '''
        tags = self._calbytime.keys()
        tags.sort()
        for t in tags:
            print t, self._calbytime[t]
            
        tags = self._calbyserial.keys()
        tags.sort()
        for t in tags:
            print t, self._calbyserial[t]
        '''    

    def store_cal_if_most_recent_cal_before_date(self, ret, date, ser, v):
        if v['time'] < date: # is this cal before date?
            if ser not in ret: # have not yet stored a cal for this ser, so store it
                ret[ser] = v
            elif ret[ser]['time'] < v['time']: # is this cal more recent than previously stored cal?
                ret[ser] = v
        return ret
    
    def get_record(self, date):
        '''
        return all the records for a given date
        '''
        ret = {}
#        print 'in get record',date
        for ser, val in self._calbyserial.iteritems():
            for v in val:
                ret = self.store_cal_if_most_recent_cal_before_date(ret, date, ser, v)
        return ret

    def get_cal(self, serial, calno):
        return self._ini.get('Calibration %s %s' % (serial, calno), 'mean calibration coefficent (band 1)')
    
    def get_calibration_all(self, serial, calno):
        '''
        return all the data from a [Calibration <serialnumber> <calibrationnumber>] section as a dict
        note ConfigParser converts all tags to lowercase
        '''
        tupl = self._ini.items('Calibration %s %s' % (serial, calno))
        ret = {}
        for a in tupl:
            ret[a[0]]=a[1]
        return ret

    def get_sensor_all(self, serial):
        '''
        return all the data from a [Sensor <serialnumber>] section as a dict
        note ConfigParser converts all tags to lowercase
        '''
        tupl = self._ini.items('Sensor %s' % (serial))
        ret = {}
        for a in tupl:
            ret[a[0]]=a[1]
        return ret

class NullStationToArchiveFile:
    '''
    class for records when the file does not exist
    return '' for any line in any record asked for
    '''
    def get(self, key):
        '''
        return blank lines for whichever lines are asked for
        
        these shold not match the existing lines and so trigger a 'C' for a changed record
        '''
        return ['' for a in range(100)]
    
class StationToArchiveReader:
    '''
    read the type of file produced by this program
    
    used to read in last months data file to see if things have changed
    '''
    def __init__(self, year, month, radnum):
        bf = '%s%02d%02d.dat' % (PREFIX[radnum], month, year%100)    
        config = ConfigFile.ConfigFile()
        path = config.CreatePath('BSRN', radnum, year)
        bf = os.path.join(path, bf)
        try:
            lines = open(bf, 'r').readlines()
        except IOError:
            self.records = NullStationToArchiveFile()
            return
        # make self.records. each record is a list of lines stored ina dict with the record num as the key e.g. '0001'
        self.records = {}
        for l in lines:
            if l[0]=='*':
                key = (l[2:]).strip()
                self.records[key] = []
            else:
                try:
                    self.records[key].append(l.strip('\r\n'))
                except UnboundLocalError:
                    print 'bsrn output file for previous month (%s) does not begin with a *. Ignoring data until line begins with a *.' % bf
        
    def getrecord(self, key):
        '''
        return a list of the lines for this record
        '''
        return self.records.get(key)
        
def getFnames(radnum):
    '''
    get fnames
    and create output directory is needed
    '''
    config = ConfigFile.ConfigFile()
    sf = config.getSensorConfig().replace('#', str(radnum))
    df = config.getBSRNConfig().replace('#', str(radnum))
    return sf, df

def openOutput(year, month, radnum):
    bf = '%s%02d%02d.dat' % (PREFIX[radnum], month, year%100)    
    config = ConfigFile.ConfigFile()
    path = config.CreatePath('BSRN', radnum, year)
    if not os.path.exists(path):
        os.makedirs(path)
    bf = os.path.join(path, bf)
    fout = open(bf, 'wb') # binary coz putting in EOL explicitly so can have WIndows EOLs under unix
    return fout

def getSiteInfo():
    config = ConfigFile.ConfigFile()
    sitefile = config.getSiteFile()
    return SiteInfo(sitefile)
    
def totwodigityear(d):
    '''
    take string: dd/mm/yy or dd/mm/yyyy
    and convert to a two digit year
    mm/dd/yy
    
    if input is XXX or zero length return XXX
    
    '''
    if d == 'XXX' or len(d) == 0:
        return 'XXX'
    
    if len(d)>8:
        year = d[8:10]
    else:
        year = d[6:8]
    return '%02d/%02d/%s' % (int(d[3:5]), int(d[0:2]), year)

def stage7qc(log, year=2008, month=1, radnum=925, stationname='Cocos Island'):
    '''
    Convert data to BSRN format ...    

    We use the data that was processed in stage 4
    '''
    log('Stage 7 (File Conversion)') 
    
    # get reportfile
    try:
        reportfile = ReportFile.ReportFile(radnum, year, MONTHNAME[month])
    except IOError:
        log("Can't find Automate.ini and/or report file for %s %s %s"% (radnum, year, MONTHNAME[month]))
        raise NoReportFileError
    except ReportFile.ReportFileNotFoundError:
        log("Can't find report file for %s %s %s"% (radnum, year, MONTHNAME[month]))
        raise NoReportFileError
 
    # check stage 4 done
    if not reportfile.isStageDone('4'):
        log("One or more critical stages were not done")
        raise StageNotDoneError

    # get input and output filenames
    sf, df = getFnames(radnum)

    # first find and read what the report file says are the missing files. &summary.stationNumber

    daystart = datetime.datetime(year, month, 1)
    if month==12:
        dayfinish = datetime.datetime(year+1, 1, 1) - datetime.timedelta(days=1)
    else:
        dayfinish = datetime.datetime(year, month+1, 1) - datetime.timedelta(days=1)
    numdays = int(dayfinish.strftime('%j')) - int(daystart.strftime('%j')) + 1

    lastmonth = daystart - datetime.timedelta(days=1)
    lastmonthsdata = StationToArchiveReader(lastmonth.year, lastmonth.month, radnum)

    sensors, cal, bsrn, bsrnsensors = CreateLR0008(log, sf, year, daystart, dayfinish, radnum, df)
    out = []
    out.append(WriteLR0001(year, month, bsrn, bsrnsensors, lastmonthsdata.getrecord('0001')))
    out.append(WriteLR0002(bsrn, lastmonthsdata.getrecord('0002')))
    out.append(WriteLR0004(log, bsrn, radnum, lastmonthsdata.getrecord('0004')))
    out.append(WriteLR0007())
    out.append(WriteLR0008(sensors, bsrnsensors, daystart, dayfinish, radnum, lastmonthsdata.getrecord('0008')))
    out.append(WriteLR0009(sensors, bsrnsensors, daystart, dayfinish, radnum, lastmonthsdata.getrecord('0009')))
    out.append(WriteLR0100(daystart, numdays, radnum))

    fout = openOutput(year, month, radnum)    
    fout.write(''.join(out))
    fout.close()
    
    log('''Note: Due to GMT correction some data will be missing from
      the last day unless the mintxt file for the 1st of the
      next month already exists.''')

def CreateLR0008(log, sf, year, daystart, dayfinish, radnum, df):
    '''
    get the classes needed to access the ini files: raddirs.ini, sensors.ini, bsrn.ini
    '''
    
    siteinfoall = getSiteInfo()
    siteinfo = siteinfoall.get(radnum)
    zone = siteinfo['gmtoffset']
    
    #sensors = Sensors(sf)
    sensors = SensorsXML(sf)
    bsrn = BSRN(df)
    
    # code to read the new-cal-file data into memory. PWD
    
    import sys
    sys.path.append('%s/atmoswatch/sys.admin/bin/web/solar' % MP)
    import caledit

    config = ConfigFile.ConfigFile()
    path = config.CreatePath('NEWCAL', radnum, year)
    calindexfile = os.path.join(path, '%d.cal' % radnum)
    cal = caledit.caledit(calindexfile)
    if cal.ds.empty:
        log('CreateLR0008: Could not read file %s' % calindexfile)
        raise NoCalFileError


    startnum = cal.get_recordnumber(daystart - datetime.timedelta(hours=zone)) # record number applying at start of month. subtract timezone as it is negative.
    finishnum = cal.get_recordnumber(dayfinish + datetime.timedelta(days=1) - datetime.timedelta(hours=zone)) # record number applying at end of month, add one day to get from midnight on last day to midnight on first day of next mount.
    recs = cal.get_records(startnum, finishnum) # get all the records that apply from start to finish of month, no check on positive or negative value

    bsrncount = {GLO:0, DIF:0, DIR:0, TER:0}
    
    bsrnsensors = {} 
    for ins in INSTRUMENTS:        
        bsrnsensors[ins] = [] # one entry for each GLO (etc.) cal record needed in the month

    lastdate = {}
    for ins in INSTRUMENTS:
        lastdate[ins] = '-1'    
        
    # loop through all records needed for this month
    for r in recs:
#        print r['start']
        s = sensors.get_record(cal.datestring_to_datetime(r['start'])) # get bsrn sensor for this calfile time
        print 'sensors', dir(sensors)
        for inst in r['inst']: # loop over all the instruments in cal record
            print 'instrument', inst
            # only include positive cals
            if float(inst['cal']) > 0:
                bsrncount[inst['symbol']] += 1
                try:
                    bsrninst = s[inst['serial'].strip()]
                except KeyError:
                	print 'BSRN sensor file does not contain instrument: %s at time: %s' % (inst['serial'].strip(), r['start'])
                	log('BSRN sensor file does not contain instrument: %s at time: %s' % (inst['serial'].strip(), r['start']))
                	raise
                # no duplicates of same cal, check by date
                if lastdate[inst['symbol']] != bsrninst['time']:
                    bsrnsensors[inst['symbol']].append(dict(calserial=inst['serial'], # serial number from cal file
                                                    serial=inst['serial'].strip(), #serial number minus trailing spaces
                                                    #bsrnsensor=s[inst['serial'].strip()],
                                                    calcal=inst['cal'], # cal value from cal file
                                                    bsrndate=bsrninst['time'], # time from bsrn file
                                                    bsrncalno=bsrninst['calno'], # cal number from bsrn file
                                                    bsrncalinfo=sensors.get_calibration_all(inst['serial'].strip(), s[inst['serial'].strip()]['calno']), # all info for this cal from bsrnfile                                                    
                                                    ))
                    lastdate[inst['symbol']] = bsrninst['time']            
        
    return sensors, cal, bsrn, bsrnsensors
    
def WriteLR0001(year, month, bsrn, bsrnsensors, lastmonth):
    '''
    int WriteLR0001(HWND hWnd, char *fn, struct radstruct inputs, struct BSRNsensors BSRNsensors, char *iniFile)

    Description:
      Write BSRN Logical Record 0001 to file
      (Id of File)
    

    We use the data that was processed in stage 4
    '''
    out = []
 
    id = int(bsrn.ini.get('Logical Record 0001','StationId'))
    ver = int(bsrn.ini.get('Logical Record 0001','Version'))


    # line2 etc
    count = 0

    line = []
    if len(bsrnsensors[GLO]) > 0:
        count += 1
        line.append(' %9d' % (2))

    if len(bsrnsensors[DIF]) > 0:
        count += 1
        line.append(' %9d' % 4)

    if len(bsrnsensors[DIR]) > 0:
        count += 1
        line.append(' %9d' % 3)

    if len(bsrnsensors[TER]) > 0:
        count += 1
        line.append(' %9d' % 5)

    for zz in range(0, 8 - count):
           line.append(' %9d' % -1)

    line.append(EOL)
    line = ''.join(line)
    
    if line == lastmonth[1]:
        out.append('*U0001%s' % EOL)
    else:
        out.append('*C0001%s' % EOL)

    # line 1
    out.append(' %2d %2d %4d %2d%s' % (id, month, year, ver, EOL))

    out.append(line)

    # phew that's it!
    return ''.join(out)

def WriteLR0002(bsrn, lastmonth):
    '''
  int WriteLR0002(HWND hWnd, char *fn, struct radstruct inputs, char *iniFile)

  Description:
    Write BSRN Logical Record 0002 to file
    (Scientist)
    -------------------------------------------------------------------------*/

 char NameScientist[80 +1],
    FonScientist[80 +1],
    FaxScientist[80 +1],
    IPScientist[80 +1],
    EmailScientist[80 +1],
    AddressScientist[80 +1],
    NameDeputyScientist[80 +1],
    FonDeputyScientist[80 +1],
    FaxDeputyScientist[80 +1],
    IPDeputyScientist[80 +1],
    EmailDeputyScientist[80 +1],
    AddressDeputyScientist[80 +1];
    '''
    scientisttags = (
    "NameScientist",
    "FonScientist",
    "FaxScientist", 
    "TCP/IPScientist",
    "EmailScientist",
    "AddressScientist", 
    "NameDeputyScientist", 
    "FonDeputyScientist", 
    "FaxDeputyScientist",
    "TCP/IPDeputyScientist",
    "EmailDeputyScientist", 
    "AddressDeputyScientist",
     )

    scientistinfo = {}

    for t in scientisttags:
        scientistinfo[t] = bsrn.ini.get('Logical Record 0002', t)

    out = []

    # line 1
    #out.append(" %2d %2d %2d\n" % (1, 0, 0))
    out.append(" %2d %2d %2d" % (-1, -1, -1)) # onging; not just started on 1st of month

    # line 2

    out.append("%-38.38s %-20.20s %-20.20s" % (
    scientistinfo['NameScientist'],
    scientistinfo['FonScientist'],
    scientistinfo['FaxScientist']))

    # line 3
    out.append("%-15.15s %-50.50s" % (
    scientistinfo['TCP/IPScientist'],
    scientistinfo['EmailScientist']))

    # line 4
    out.append("%-80.80s" %
     scientistinfo['AddressScientist'])

    # line 5
    #out.append(" %2i %2i %2i\n" % (1, 0, 0))
    out.append(" %2d %2d %2d" % (-1, -1, -1)) # onging; not just started on 1st of month

    # line 6

    out.append("%-38.38s %-20.20s %-20.20s" %
    (scientistinfo['NameDeputyScientist'],
    scientistinfo['FonDeputyScientist'],
    scientistinfo['FaxDeputyScientist']))

    # line 7
    out.append("%-15.15s %-50.50s" %
     (scientistinfo['TCP/IPDeputyScientist'],
     scientistinfo['EmailDeputyScientist']))

    # line 8
    out.append("%-80.80s" %
     scientistinfo['AddressDeputyScientist'])

    ret = EOL.join(out)
    
    if (out[1:4] == lastmonth[1:4] and
        out[5:8] == lastmonth[5:8]):
        return '%s%s%s%s' % ('*U0002', EOL, ret, EOL)
    else:
        return '%s%s%s%s' % ('*C0002', EOL, ret, EOL)

def WriteLR0004(log, bsrn, radnum, lastmonth):
    '''
/*-----------------------------------------------------------------------------
  int WriteLR0004(HWND hWnd, char *fn, char *iniFile, char *siteFile)

  Description:
    Write BSRN Logical Record 0004 to file
    (Staion description, horizon)    

-------------------------------------------------------------------------*/
    '''

    stationtags = (
    "SurfaceType",
    "TopographyType",
    "Address",
    "Fon",
    "Fax",
    "TCP/IP",
    "Email", 
    "SYNOPid",
     )

    stationinfo = {}

    for t in stationtags:
        stationinfo[t] = bsrn.ini.get('Logical Record 0004', t)

    out = []

    # line 1
    #out.append(" %2i %2i %2i\n" % (1, 0, 0))
    out.append(" %2d %2d %2d" % (-1, -1, -1)) # onging; not just started on 1st of month

    # line 2
    out.append(" %2i %2i" % (int(stationinfo['SurfaceType']), int(stationinfo['TopographyType'])))

    # line 3
    out.append("%-80.80s" % stationinfo['Address'])     

    # line 4
    out.append("%-20.20s %-20.20s" % (stationinfo['Fon'], stationinfo['Fax']))

    # line 5
    out.append("%-15.15s %-50.50s" % (stationinfo['TCP/IP'], stationinfo['Email']))

    siteinfoall = getSiteInfo()
    siteinfo = siteinfoall.get(radnum)
    
    # line 6
    lat = siteinfo['latdeg']/ abs(siteinfo['latdeg']) * (abs(siteinfo['latdeg']) + siteinfo['latmin']/60.)
    lon = siteinfo['londeg']/ abs(siteinfo['londeg']) * (abs(siteinfo['londeg']) + siteinfo['lonmin']/60.) 

    # change from coords rel to (equator, Greenwich) to coord rel to (S pole, 180 W of Greenwich) PWD 10 May 2000

    lat = 90.0 - lat     # assumes lat is S (not N) of the equator
    lon = lon + 180.0    # assumes lon is E (not W) of Greenwich

    out.append(" %7.3f %7.3f %4i %-5.5s" % 
     (lat,
     lon,
     siteinfo['elevation'],
     stationinfo['SYNOPid']))

    toppart = out[:] # copy for later comparision
    # line 7
    out.append(" %2d %2d %2d" % (-1, -1, -1)) # true if horizon hasn't changed

    out = ['%s%s' % (EOL.join(out), EOL)] # join all the lines suing EOL to make out[0]
    
    # line 8 horizon description ...


    #open file read 'till LR0004
    #then read azimuth values and elevation 
    # count and once 11th value read add new line
    # keep reding untill hit new header [

    items = bsrn.ini.items('Logical Record 0004')
    items = [it for it in items if it[0].lower().startswith('azimuth')] # skip any kind which doesn't have the right leader
    # put in order of azimuth from 180-> 360, 0 -> 180
    sortlist = []
    for it in items:
        sorter = int(it[0][7:10])
        if sorter < 180:
            sorter += 360
        sortlist.append( [sorter,it] )
    sortlist.sort()
    items = []
    for s in sortlist:
        items.append(s[1])
    
    horizon = []
    for it in items:
        horizon.append(dict(azi=int(it[0][7:10]),
                            ele=int(it[1])))
        
    count = 0
    
    for h in horizon:
        if h['azi'] <=0 or h['azi'] > 360:
            log("bad azimuth angle: %3d" % h['azi'])
        elif h['ele'] <0 or h['ele'] > 90:
            log("bad elevation angle: %3d for azimuth: %3d" % (h['ele'], h['azi']))
        else:
            out.append(" %3i %2i" % (h['azi'], h['ele']))
            count += 1

        if count >= 11:
            count = 0
            out.append(EOL)

    if count < 11 and count != 0:
        for a in range(count, 11):
            out.append(" %3i %2i" % (-1, -1))
        out.append(EOL)
    for a in range(11):
        out.append(" %3i %2i" % (-1, -1))
    out.append(EOL)

    ret = ''.join(out)
    
    if (toppart[1:6] == lastmonth[1:6]): # not checkling the skyline for change. Need to do this by hand.
        return '%s%s%s' % ('*U0004', EOL, ret)
    else:
        return '%s%s%s' % ('*C0004', EOL, ret)

def WriteLR0006():
    '''
/*-----------------------------------------------------------------------------
  int WriteLR0006(HWND hWnd, char *fn, struct radstruct inputs, char *iniFile)

  Description:
    Write BSRN Logical Record 0006 to file
    (Ozone measuring Equipment)
  
-------------------------------------------------------------------------*/
    '''
    
    out = []   
 
    out.append("*U0006")

    # line 1
    hour = 0
    min = 0
    day = 1
    
    # set that sensor was measuring
    meas = 'N'

    out.append(" %2i %2i %2i %c" % (when.day, hour, min, meas))

    # line 2
    out.append("%-80.80s", "XXX");

    # line 3
    out.append("%-80.80s", "XXX");

    # line 4
    out.append("%-80.80s", "XXX");

    # line 5
    out.append("%-80.80s", "XXX");

    # line 6
    out.append("%-80.80s", "XXX");

    # line 7
    out.append("%c %c %c %c %c %c", "N", "N", "N", "N", "N", "N");

    return EOL.join(out)

def WriteLR0007():
    ''''
  int WriteLR0007(HWND hWnd, char *fn, struct radstruct inputs, char *iniFile)

  Description:
    Write BSRN Logical Record 0007 to file
    (Station History)
    '''
    out = []
    out.append("*U0007")

    # line 1
    hour = 0
    min = 0
    day = 1
    
    #out.append(" %2i %2i %2i\n" % (day, hour, min))
    out.append(" %2d %2d %2d" % (-1, -1, -1)) # ongoing; not just started on 1st of month

    # line 2
    out.append("%-80.80s" % "XXX")

    # line 3
    out.append("%-80.80s" % "XXX")

    # line 4
    out.append("%-80.80s" % "XXX")

    # line 5
    out.append("%-80.80s" % "XXX")

    # line 6
    out.append("%-80.80s" % "XXX")

    # line 7
    out.append("%c %c %c %c %c %c" % ('N', 'N', 'N', 'N', 'N', 'N'))

    return '%s%s' % (EOL.join(out), EOL)

def WriteLR0008(sensors, bsrnsensors, daystart, dayfinish, radnum, lastmonth):
    '''
/*-----------------------------------------------------------------------------
  int WriteLR0008(HWND hWnd, char *fn, struct radstruct inputs, struct BSRNsensors BSRNsensors)

  Description:
    Write BSRN Logical Record 0008 to file
    (Radiation Instruments)
    

  We use the data that was processed in stage 4

-------------------------------------------------------------------------*/
    '''

    # serialout will point to serial number after the '-'
    #char *serialout;

    out = []

    # now for each instrument thare are 11 lines to write out.  yes eleven ...
    # ... didn't Dalbello have a song about 11?

    siteinfoall = getSiteInfo()
    siteinfo = siteinfoall.get(radnum)
    zone = siteinfo['gmtoffset']

    for t in [GLO, DIF, DIR, TER]: 
        print 'doing sensor::', t
        for b in bsrnsensors[t]: # loop over each instrument cal needed for this month for this instrument
            print 'doing date::', b['bsrndate'], b['serial']
#            print 'doing date', b.keys()			
            # this might get too many, e.g. when cal goes negative
            if dayfinish < b['bsrndate']:
                # not sure if this can ever happen - the cal date is after the end of the month!?!!
                hour = -1
                min = -1
                day = -1
            elif daystart > b['bsrndate']:
                #hour = 0
                #min = 0
                #day = 1
                hour = -1 # ongoing; not just started on 1st of month
                min = -1
                day = -1
            else:
                tme = b['bsrndate'] + datetime.timedelta(hours=zone)
                day = tme.day
                hour = tme.hour
                min = tme.minute

            # set that sensor was measuring
            meas = 'Y'

            out.append(" %2i %2i %2i %c" % (day, hour, min, meas))
            # line 2

            
            # serialout will point to serial number after the '-'
            serialout = b['serial'].split('-')[1]
            sensorinfo = sensors.get_sensor_all(b['serial'])
            out.append("%-30.30s %-15.15s %-18.18s %-8.8s %5li" % (sensorinfo['manufacturer'],
                                     sensorinfo['model'],
                                     serialout,
                                     totwodigityear(sensorinfo['purchase_date']),        
                                     int(sensorinfo['wrmc_number'])))
            # line 3
            out.append("%-80.80s" % sensorinfo['remarks'])

            # line 4
            out.append(" %2i %2i %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f %2i %2i" % (
                            int(sensorinfo['pyrgeometer_body_compensation']),
                            int(sensorinfo['pyrgeometer_dome_compensation']),
                            float(sensorinfo['wavelength_of_band_1']),
                            float(sensorinfo['bandwidth_of_band_1']),
                            float(sensorinfo['wavelength_of_band_2']),
                            float(sensorinfo['bandwidth_of_band_2']),
                            float(sensorinfo['wavelength_of_band_3']),
                            float(sensorinfo['bandwidth_of_band_3']),
                            int(sensorinfo['max_zenith_angle_direct']),
                            int(sensorinfo['min_zenith_angle_direct']),
                            ))

            # line 5
            out.append("%-30.30s %-40.40s" % (
                                                b['bsrncalinfo']['location'],
                             b['bsrncalinfo']['person']))

            # line 6,7,8
            for bandno in range(1,4):
                print 'bandifno', b['bsrncalinfo'].keys()			
#                out.append("%-8.8s" % totwodigityear(b['bsrncalinfo']['start_of_calibration_period_band_%d' % bandno]))
                if float(b['bsrncalinfo']['mean_calibration_coefficent_band_%d' % bandno]) < -0.9: # i.e. == -1.0000
                    ccc = "%-8.8s %-8.8s" % ('XXX','XXX')
                else:
                    ccc = "%-8.8s %-8.8s" % (
                                 totwodigityear(b['bsrncalinfo']['date']),
                                 totwodigityear(b['bsrncalinfo']['end_date']),
                                 )
                out.append("%s %2i %12.4f %12.4f" % (
                       ccc,
                       int(b['bsrncalinfo']['number_of_comparisons_band_%d' % bandno]),
                       float(b['bsrncalinfo']['mean_calibration_coefficent_band_%d' % bandno]),
                       float(b['bsrncalinfo']['standard_error_of_calibration_band_%d' % bandno])))

            # line 9
            out.append("%-80.80s" % b['bsrncalinfo']['remarks1'])

            # line 10
            out.append("%-80.80s" % b['bsrncalinfo']['remarks2'])

            # line 11 ... oops no 11th line sorry, and Dalbello didn't write a song about 10 ;-)

    ret = '%s%s' % (EOL.join(out), EOL)
    
    if len(out) != len(lastmonth):
        return '%s%s%s' % ('*C0008', EOL, ret)
    else:
        same = True
        for i in range(1, len(out), 10):
            if out[i:i+9] != lastmonth[i:i+9]:
                same = False
        if same:
            return '%s%s%s' % ('*U0008', EOL, ret)
        else:
            return '%s%s%s' % ('*C0008', EOL, ret)

def WriteLR0009(sensors, bsrnsensors, daystart, dayfinish, radnum, lastmonth):
    '''
/*-----------------------------------------------------------------------------
  int WriteLR0009(HWND hWnd, char *fn, struct radstruct inputs, struct BSRNsensors BSRNsensors)

  Description:
    Write BSRN Logical Record 0009 to file
    (Assignment of radiation quanties to Instruments)
    

  We use the data that was processed in stage 4

-------------------------------------------------------------------------*/
    '''
    out = []

    siteinfoall = getSiteInfo()
    siteinfo = siteinfoall.get(radnum)
    zone = siteinfo['gmtoffset']

    quant = dict(GLO=2, DIF=4 ,DIR=3, TER=5)

    for t in [GLO, DIF, DIR, TER]: 
        for b in bsrnsensors[t]: # loop over each instrument cal needed for this month for this instrument
            # this might get too many, e.g. when cal goes negative
            if dayfinish < b['bsrndate']:
                # not sure if this can ever happen - the cal date is after the end of the month!?!!
                hour = -1
                min = -1
                day = -1
            elif daystart > b['bsrndate']:
                #hour = 0
                #min = 0
                #day = 1
                hour = -1 # ongoing; not just started on 1st of month
                min = -1
                day = -1
            else:
                tme = b['bsrndate'] + datetime.timedelta(hours=zone)
                day = tme.day
                hour = tme.hour
                min = tme.minute

            sensorinfo = sensors.get_sensor_all(b['serial'])
            out.append(" %2i %2i %2i %9i %5i %2i" % (day, hour, min, quant[t],
                                                       int(sensorinfo['wrmc_number']),
                                                       -1))


    ret = '%s%s' % (EOL.join(out), EOL)
    
    if len(out) != len(lastmonth):
        return '%s%s%s' % ('*C0009', EOL, ret)
    else:
        same = True
        for r,l in zip(out, lastmonth):
            if r[9:] != l[9:]:
                same = False
        if same:
            return '%s%s%s' % ('*U0009', EOL, ret)
        else:
            return '%s%s%s' % ('*C0009', EOL, ret)

def WriteLR0100(daystart, numdays, radnum):      
    '''
/*-----------------------------------------------------------------------------
  int WriteLR0100(HWND hWnd, char *fn, struct radstruct inputs, char *iniFile)

  Description:
    Write BSRN Logical Record 0100 to file
    (Basic Measurement)    

-------------------------------------------------------------------------*/
    '''
    out = []

    siteinfoall = getSiteInfo()
    siteinfo = siteinfoall.get(radnum)
    zone = siteinfo['gmtoffset']

    if zone > 0:
        print "WriteLR0100:Code not written for stations West of Greenwich"
        raise BadLongitudeError
    
    zoneminutes = int (60.0 * zone)    # number of minutes to add to get GMT (this will be -ve for Aust)

    out.append("*C0100")

    config = ConfigFile.ConfigFile()
    
    lastdaynum = -1

    for dayoffset in range(numdays):
        date = daystart + datetime.timedelta(days=dayoffset)

        # now the BSRN file
        for mingmt in range(1440):
            
            dtgmt = date + datetime.timedelta(minutes=mingmt)
            dayofmonthgmt = int(dtgmt.day)
                        
            dt = dtgmt - datetime.timedelta(minutes=zoneminutes)            
            daynum = int(dt.strftime('%j'))
            if daynum != lastdaynum:                      
                dataFile = "%03i%02i%03i.minTXT" % (radnum, dt.year%100, daynum)
                path = config.CreatePath('Processed Data', radnum, dt.year)
                dataFile = os.path.join(path, dataFile)
                mintxt = MinTxt(dataFile, dt)
                lastdaynum = daynum
            
            min = dt.hour*60 + dt.minute
            
            gl = mintxt.get_minutedata('Global', min + 1)
            dr = mintxt.get_minutedata('Direct', min + 1)
            df = mintxt.get_minutedata('Diffuse', min + 1)
            te = mintxt.get_minutedata('Longwave', min + 1)
                
            # line 1
            out.append(" %2i %4i   %4i %5.1f %4i %4i   %4i %5.1f %4i %4i" % ( 
                                dayofmonthgmt,
                                mingmt,
                                int(gl[0]),
                                gl[1],
                                int(gl[2]),
                                int(gl[3]),
                                int(dr[0]),
                                dr[1],
                                int(dr[2]),
                                int(dr[3]),
                                ))      
            # line 2
            out.append("           %4i %5.1f %4i %4i   %4i %5.1f %4i %4i    %5.1f %5.1f %4i" % ( 
                                int(df[0]),
                                df[1],
                                int(df[2]),
                                int(df[3]),
                                int(te[0]),
                                te[1],
                                int(te[2]),
                                int(te[3]),
                                -99.9,
                                -99.9,
                                -999))
    
    return '%s%s' % (EOL.join(out), EOL)
        
def printout(txt):
    print txt
        
if __name__ == '__main__':
    TEST = False
    #TEST = True
    if TEST:
        #stage7qc(log=printout, year=2006, month=8, radnum=701)
        stage7qc(log=printout, year=1995, month=8, radnum=801)
        
        #screenfile = ScreenOutput.ScreenOutput()
        #print screenfile.out()
    
    else:
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option("-y", "--year", dest="year",
                    help="the year")
        parser.add_option("-m", "--month", dest="month",
                      help="the month to process")
        parser.add_option("-s", "--stnum", dest="stnum",
                      help="the station number")
    
        (options, args) = parser.parse_args()
    
        if not options.year or not options.month or not options.stnum:
            print 'The options are not optional. Please supply station number, year and month.\n Enter Stage7 -h for more information.'
        else:
            print options.stnum, options.year, options.month
            stage7qc(log=printout,
                 year=int(options.year), month=int(options.month),
                 radnum=int(options.stnum))
