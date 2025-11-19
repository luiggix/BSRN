

##import ExtendedConfigParser
##import ConfigParser

import os
import ConfigFile

import IniReadWriter

#reload(IniReadWriter)

class ReportFileNotFoundError(Exception): pass

class ReportFile:
    """
    class for reading an writing .report files
    """

    def __init__(self, radnum, year, descript, errfile='reporterr.txt', status='append'):
        """
        initialise by reading in the file
        read in nothing if it does not exist
        """
        self._errfile = errfile
               
        tmpFile = "%03i%02i%03s.report" % (radnum, year%100, descript)
        config = ConfigFile.ConfigFile()
        path = config.CreatePath('Report QC', radnum, year)
        self._reportfilename = "%s/%s" % (path, tmpFile)
        if status=='new':
            # if path not exists then create it
            if not os.path.exists(path):
                os.makedirs(path)
        try:
            self._report = IniReadWriter.IniReadWriter(self._reportfilename, status)
        except IniReadWriter.NoFileError:
            self._err = open(errfile,'a')
            self._err.write("file not found:%s\n"%self._reportfilename)
            self._err.close()
            raise ReportFileNotFoundError

# stage 1 stuff

    def setStationSummary(self, name, stn, year, dayfrom, dayto):
        """
        set the year and day range in the repot file
        """
        sec='Station Details'
        self._report.add_section(sec)
        self._report.set(sec,'Station Name',name)
        self._report.set(sec,'Radiation Station Number',str(stn))
        self._report.set(sec,'Period Of File','%d from day number %d to %d'%(year,dayfrom,dayto))
        self._report.set(sec,'Number Of Days Covered',str(dayto-dayfrom+1))

    def reportDataRecoverySummary(self, t, found):
        """
        report files data in [Data Recovery Summary]
        """
        sec = 'Data Recovery Summary'
        self._report.add_section(sec)
        self._report.set(sec, '%s files found'%t.upper(), found)

    def reportDataRecoverySummaryPercent(self, t, percent):
        """
        report files data in [Data Recovery Summary]
        """
        sec = 'Data Recovery Summary'
        self._report.set(sec, '%s %% recovered (files)' %t, '%.4f'%percent)
        
    def reportDataRecoverySummaryMissing(self, t, missing):
        """
        report files data in [Data Recovery Summary]
        """
        sec = 'Data Recovery Summary'
        self._report.set(sec, '%s missing files'%t, missing)

    def reportMissingFiles(self, t, missingarray):
        """
        write out the line of the missing files of type t

        write nothing if none are missing 
        """
        if len(missingarray)==0:
            return
        sec = "Missing %s files" % t.upper()
        opt = "%sMissing0" % t
        self._report.add_section(sec)
        self._report.set(sec, opt, ", ".join(missingarray))

    def reportFoundFiles(self, t, dayfrom, dayto, missingarray):
        """
        write out the line of the found files of type t

        write nothing if none are found

        missing: list of MISSING (not found) days
        """
        if len(missingarray)==dayto-dayfrom+1:
            return
        sec = "Found %s files" % t.upper()
        opt = "%sFound0" % t
        self._report.add_section(sec)
        foundarray = [str(a) for a in range(dayfrom,dayto+1) if str(a) not in missingarray]
        self._report.set(sec, opt, ", ".join(foundarray))

    def setPreviousTest(self, year, day):
        """
        set the previous test date
        """
        sec = 'Previous TEST File'
        self._report.add_section(sec)
        self._report.set(sec,'Year',year)
        self._report.set(sec,'Day',day)


# stage2a stuff

    def writeBINSummary(self, name, correctdict):
        """
        write the BIN Summary for one instrument

        name: name of instrument
        correctdict: dict of number of correct days for each
        quantity for this instrument
        """
        self._measurands = ['mean','min','max','sd','group']
        options = ["Valid Data","Valid Min Data",\
                   "Valid Max Data","Valid SD Data",\
                   "Valid Statistics"]
        sec = '%s Binary Data Recovery Summary' % name
        self._report.add_section(sec)
        for m,op in zip(self._measurands, options):
            self._report.set(sec,op,correctdict[m])
        
    def readDoTests(self, name):
        """
        read do tests for instrument with shortname: name

        return results in dictionary
        """
        options = ["LimitsMean","LimitsMin",\
                   "LimitsMax","LimitsSD",\
                   "Group"]        
        ret={}
        for m,op in self._measurands,options:
            opt = 'Check%s%s' % (name,op)
            ret[m]=self._report.get('Stage 2a (Binary Analysis) Tests',opt)
        return ret


    def writeBadFileList(self, name, shortname, heading, label, \
                                    binerrorfailedarray):
        """
        write out the line of the bad files 

        write nothing if none are missing 
        """
        if len(binerrorfailedarray)==0:
            return
	sec = "Bad BINARY %s%s" % (name, heading)
	opt = "BinaryBad%s%s" % (shortname, label)
        self._report.add_section(sec)
        self._report.set(sec, opt, ", ".join(binerrorfailedarray))
        
                           
# stage3: stage 1 stuff

    def getDayFrom(self):
        """
        return the dayfrom using:
        
        [Station Details]
        Period Of File=2006 from day number 001 to 031
        """
        pof = self._report.get('Station Details','Period Of File')
        i = pof.find('number')+7
        return int(pof[i:i+3])

    def getDayTo(self):
        """
        return the dayto

        uses:        
        [Station Details]
        Period Of File=2006 from day number 001 to 031
        """
        pof = self._report.get('Station Details','Period Of File')
        i = pof.find('to')+3
        return int(pof[i:i+3])

    def getYear(self):
        """
        return the year

        uses:
        [Station Details]
        Period Of File=2006 from day number 001 to 031
        """
        pof = self._report.get('Station Details','Period Of File')
        i = pof.find(' ')
        return int(pof[0:i])
        
    def getStn(self):
        """
        return the station number
        """
        return int(self._report.get('Station Details','Radiation Station Number'))


    def getStationName(self):
        """
        return the station name
        """
        return self._report.get('Station Details','Station Name')
    
    def getDaysCovered(self):
        """
        return the number of days covered
        """
        return self._report.get('Station Details','Number Of Days Covered')
        
    def isStageDone(self,s):
        """
        return True is stage s is done

        parameters:
        s: stage as int or string, e.g. 3, '3', '2a', 'exposure'
        """
        this_stage = 'Stage %s'%s

        try:
            stages = self._report.items('QC Stages Done')
        except IniReadWriter.NoSectionError:
            stages = self._report.items('QC Stages Done]')
        
        for a in stages:
            if a[0].startswith(this_stage):
                return True
        return False


    def getMissingFiles(self, output, section):
        """
        read in missing files and check the number of missing files
        matches the stated number of missing files
        """
        return self.checkDayListStage1(output, section, ' missing files')


    def getFoundFiles(self, output, section):
        """
        read in found files and check the number of found files
        matches the stated number of found files
        """
        return
        self.checkDayListStage1(output, section, ' files found')
        
        
    def checkDayListStage1(self, output, section, string):
        """
        read in the list of daynumbers from one line

        parameters:
        output: list to store the daynumbers
        section: the section in the ini file
        string: option in [Data Recovery Summary] = name + string

        returns:
    the number of records read or error code on error
    Possible errors include:
        more missing file found then expected return -10
        less missing file found then expected return -20 
        """
        option = self._report.items(section)
        name = section.split()[1] # [Missing NAME files]
        try:
            expectednum = self.getNumFiles(name, string)
        except IniReadWriter.NoOptionError:
            self._err = open(errfile,'a')
            self._err.write('No option [%s]: %s\n'%(section, name+string))
            self._err.close()
            return
        self.checkDayList(expectednum, output, section)


    def checkDayList(self, expectednum, output, section):
        """
        read in the list of daynumbers from one line

        parameters:
        expectednum: number of expected daynumbers
        output: list to store the daynumbers
        section: the section in the ini file

        returns:
    the number of records read or error code on error
    Possible errors include:
        more missing file found then expected return -10
        less missing file found then expected return -20 
        """
        option = self._report.items(section)
            
        values = option[0][1].split(',') # only one option
        output.append(values) 
        
        l = len(values)
        if expectednum==l:
            return l
        elif expectednum<l:
            self._err = open(errfile,'a')
            self._err.write( "[%s] expected:%d found:%d\n"%(section,expectednum,l))
            self._err.write(values.__str__())
            self._err.write('\n')
            self._err.close()
            return -10
        elif expectednum>l:
            self._err = open(errfile,'a')
            self._err.write( "[%s] expected:%d found:%d\n"%(section,expectednum,l))
            self._err.write(values.__str__())
            self._err.write('\n')
            self._err.close()
            return -20

        

    def getNumFiles(self, name, string):
        """
        get the number of files for name plus string
        from the parameter in Data Recovery Summary

        e.g.
        name = 'BINARY'
        string = ' missing file'

        finds:
        BINARY missing file=1
        or
        Binary missing file=1
        returns 1 as an int
        """
        option = name + string
        try:
            return int(self._report.get('Data Recovery Summary',option))
        except IniReadWriter.NoOptionError:
            option = name.capitalize() + string # make only first letter capital
            return int(self._report.get('Data Recovery Summary',option))


    def getFoundSectionList(self):
        """
        return all the sections beginning with 'Found'
        """
        return self.getSectionListStartingWith('Found')


    def getMissingSectionList(self):
        """
        return all the sections beginning with 'Missing'
        """
        return self.getSectionListStartingWith('Missing')


    def getSectionListStartingWith(self,start):
        """
        return all the sections beginning with start
        """
        ss = self._report.sections()
        return [s for s in ss if s.startswith(start)]


    def checkStage1(self):
        """
        for each quantity:
        check that the stated number of missing files
        matches the number of files listed;
        check that the stated number of found files
        matches the number of files listed

        if not return False

        return value is not used,
        so return value is not very meaningful
        """
        #missing
        ret = True
        secs = self.getMissingSectionList()
        for sect in secs:
            days=[]
            try:
                code = self.getMissingFiles(days, sect)
            except IniReadWriter.NoSectionError, inst:
                self._err = open(errfile,'a')
                self._err.write("Stage 1 section not found: %s\n"%inst)
                self._err.close()
            if code!=1:
                ret=False
        #found
        secs = self.getFoundSectionList()
        for sect in secs:
            days=[]
            code = self.getFoundFiles(days, sect)
            if code!=1:
                ret=False
        return ret


    def write(self):
        """
        write out the report file

        """
        fname = self._reportfilename+'new'
        # remove any existing report file
        if os.path.exists(fname):
            os.remove(fname)

        fout = open(fname,'w')
        self._report.write(fout)
        
    def setStageDone(self, stage, d):
        """
        set the stage to date stored in d
        for output

        parameters:
        stage: the stage as an int or string
        d: current time in datetime format
        """
        stages = { '1' :'Stage 1 (Files Retrieved)', \
                   '2a':'Stage 2a (Binary Analysis)', \
                   '2b':'Stage 2b (Tracker Analysis)', \
                   '2c':'Stage 2c (Test File Analysis)', \
                   '2d':'Stage 2d (Time File Analysis)', \
                   '3' :'Stage 3 (Report File Analysis)', \
                   '4' :'Stage 4 (Preliminary Data Processing)', \
                   'exposure' :'Stage Exposure (Write Exposure Files)' }
        stage = str(stage).lower()
        option = stages[stage]
        if stage=='1':
            self._report.add_section('QC Stages Done')        
        self._report.setNewOption('QC Stages Done',option,d.strftime('%a %b %d %H:%M:%S %Y'))
     

# stage3: stage 2a stuff

    def getInt(self,section,option):
        """
        return the int of [section] option
        """
        return int(self._report.get(section,option))


    def checkStage2a(self, start, finish):
        """
        read in stage2a stuff and check the daynumbers
        don't write anything
        """
        zz = finish-start+1
        # summary.binaryFiles.foundFiles;

        stage2alist=[['Bad BINARY file size', 'Binary Data Recovery Summary', 'Correct File Size'      ] , \
                     ['Bad BINARY station',   'Binary Data Recovery Summary', 'Correct Station details'] , \
                     ['Bad BINARY year',      'Binary Data Recovery Summary', 'Correct Year'           ] , \
                     ['Bad BINARY day',       'Binary Data Recovery Summary', 'Correct Day Number'     ] , \
                     ['Bad BINARY time',      'Binary Data Recovery Summary', 'Correct Time Stamp'     ] , \
                     ['Bad BINARY flag',      'Binary Data Recovery Summary', 'Valid Flag Identifier'  ] , \
                     ['Bad BINARY samples',   'Binary Data Recovery Summary', 'Valid Samples recorded' ] , \
                     \
                     ['Bad BINARY Global',      'Global Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Global SD',   'Global Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Global max',  'Global Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Global min',  'Global Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Global Group','Global Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Global Thermister',    'Global Thermister Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Global Thermister SD', 'Global Thermister Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Global Thermister max','Global Thermister Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Global Thermister min','Global Thermister Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Global Therm Group',   'Global Thermister Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Diffuse',      'Diffuse Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Diffuse SD',   'Diffuse Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Diffuse max',  'Diffuse Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Diffuse min',  'Diffuse Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Diffuse Group','Diffuse Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Diffuse Thermister',    'Diffuse Thermister Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Diffuse Thermister SD', 'Diffuse Thermister Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Diffuse Thermister max','Diffuse Thermister Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Diffuse Thermister min','Diffuse Thermister Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Diffuse Therm Group',   'Diffuse Thermister Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Direct',      'Direct Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Direct SD',   'Direct Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Direct max',  'Direct Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Direct min',  'Direct Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Direct Group','Direct Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Direct Thermister',    'Direct Thermister Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Direct Thermister SD', 'Direct Thermister Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Direct Thermister max','Direct Thermister Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Direct Thermister min','Direct Thermister Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Direct Therm Group',   'Direct Thermister Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Longwave',      'Longwave Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Longwave SD',   'Longwave Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Longwave max',  'Longwave Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Longwave min',  'Longwave Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Longwave Group','Longwave Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Longwave Body Thermister',    'Longwave Body Thermister Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Longwave Body Thermister SD', 'Longwave Body Thermister Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Longwave Body Thermister max','Longwave Body Thermister Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Longwave Body Thermister min','Longwave Body Thermister Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Longwave Body Therm Group',   'Longwave Body Thermister Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Longwave Dome Thermister',    'Longwave Dome Thermister Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Longwave Dome Thermister SD', 'Longwave Dome Thermister Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Longwave Dome Thermister max','Longwave Dome Thermister Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Longwave Dome Thermister min','Longwave Dome Thermister Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Longwave Dome Therm Group',   'Longwave Dome Thermister Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Short Circuit',      'Short Circuit Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Short Circuit SD',   'Short Circuit Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Short Circuit max',  'Short Circuit Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Short Circuit min',  'Short Circuit Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Short Circuit Group','Short Circuit Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Zero',      'Zero Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Zero SD',   'Zero Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Zero max',  'Zero Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Zero min',  'Zero Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Zero Group','Zero Binary Data Recovery Summary', 'Valid Statistics'],\
                     \
                     ['Bad BINARY Temp',      'Temp Binary Data Recovery Summary', 'Valid Data'],\
                     ['Bad BINARY Temp SD',   'Temp Binary Data Recovery Summary', 'Valid SD Data'],\
                     ['Bad BINARY Temp max',  'Temp Binary Data Recovery Summary', 'Valid Max Data'],\
                     ['Bad BINARY Temp min',  'Temp Binary Data Recovery Summary', 'Valid Min Data'],\
                     ['Bad BINARY Temp Group','Temp Binary Data Recovery Summary', 'Valid Statistics'] ]

        #check they can all be read in                           
        for s in stage2alist:
            num = self.getInt(s[1],s[2])
            if num != -1 and zz - num > 0:
                missing = []
                try:
                    self.checkDayList(zz - num, missing, s[0]) # nothing done with return value in <missing>
                except IniReadWriter.NoSectionError, inst:
                    self._err = open(errfile,'a')
                    self._err.write("Stage 2a section not found: %s\n"%inst)
                    self._err.close()

        # write day type break down
        for zz in range(start, finish+1):
            day = 'Day%03d' % zz
            try:
                self._report.get('Day BreakDown (%) Night-Clear-Cloudy-Suspect',day)
            except IniReadWriter.NoOptionError:
                pass
                #not all days need be present


    def checkStage2b(self, start, finish):
        """
        read in stage2b stuff
        don't write anything
        """
        trksummary = ["Correct Date","Correct Time"]
        
        for t in trksummary:
                self._report.get('Tracker Data Recovery Summary',t)

        # write day type break down
        for zz in range(start, finish+1):
            day = 'Day%03d' % zz
            try:
                self._report.get('Day BreakDown (%) Parked-Passive-Active-Event',day)
            except IniReadWriter.NoOptionError:
                pass
                #not all days need be present

    def readPreviousTest(self):
        """
        read in the previous test, just to check it
        """
        year = self._report.get('Previous TEST File','Year')
        dayn = self._report.get('Previous TEST File','Day')
        return year,dayn


    def checkStage2c(self, start, finish):
        """
        return previous year,dayn
        """

        year,dayn = self.readPreviousTest()

        stage2clist = [['Cleaning TEST event','Test File Data Summary','Cleaning Events'], \
                      ['ADtest TEST event','Test File Data Summary','AD Testing Events'], \
                      ['Other TEST event','Test File Data Summary','Other Events'], \
                      ['Bad TEST event','Test File Data Summary','Bad Events'] ]

        for s in stage2clist:
            num = self.getInt(s[1],s[2])
            if num > 0:
                missing=[]
                try:
                    self.checkDayList(num, missing, s[0]) # nothing done with return value
                except IniReadWriter.NoSectionError, inst:
                    self._err = open(errfile,'a')
                    self._err.write("Stage 2c section not found: %s\n"%inst)
                    self._err.close()

        # write day type break down
        for zz in range(start, finish+1):
            day = 'Day%03d' % zz
            try:
                self._report.get('Day BreakDown (min) Cleaning-ADtest-Other-Bad',day)
            except IniReadWriter.NoOptionError:
                pass
                #not all days need be present

        # read event log
        self._report.items('Test File Event Log')

        return year,dayn

    def addFilesGroupedSection(self,dayn):
        """
        add the section for this day
        and return the section name
        """
        sectionname = "Day %03d Minute Listing Grouped" % int(dayn)
        self._report.add_section(sectionname)
        return sectionname

    def setFlagsGrouped(self,sectionname,fromMinute,toMinute, flags):
        """
        set the flags for a group of minutes
        the minutes have identicial flags

        [Day dayn Minute Listing Grouped]
        minfromMinute-toMinute=flags
        """
        if fromMinute == toMinute:
            option = 'Min%04d'%fromMinute
        else:
            option = 'Min%04d-%04d' % (fromMinute,toMinute)
        self._report.setNewOption(sectionname,option,flags)

    def get2aflags(self, dayn):
        try:
            ret = self._report.dictitems("Day %03d Minute Listing Binary"    % int(dayn))
            return ret
        except IniReadWriter.NoSectionError:
            return {}

    def get2bflags(self, dayn):
        try:
            return self._report.dictitems("Day %03d Minute Listing Tracker"   % int(dayn))
        except IniReadWriter.NoSectionError:
            return {}

    def get2cflags(self, dayn):
        try:
            return self._report.dictitems("Day %03d Minute Listing Test File" % int(dayn))
        except IniReadWriter.NoSectionError:
            return {}

    def get2dflags(self, dayn):
        try:
            return self._report.dictitems("Day %03d Minute Listing Time"      % int(dayn))
        except IniReadWriter.NoSectionError:
            return {}
        
    def removeFlagsUngrouped(self, dayn):
        try:
            self._report.remove_section("Day %03d Minute Listing Binary"    % int(dayn))
        except IniReadWriter.NoSectionError:
            pass
        try:
            self._report.remove_section("Day %03d Minute Listing Tracker"   % int(dayn))
        except IniReadWriter.NoSectionError:
            pass
        try:
            self._report.remove_section("Day %03d Minute Listing Test File" % int(dayn))
        except IniReadWriter.NoSectionError:
            pass
        try:
            self._report.remove_section("Day %03d Minute Listing Time"      % int(dayn))
        except IniReadWriter.NoSectionError:
            pass



# Stage 7 stuff


    
