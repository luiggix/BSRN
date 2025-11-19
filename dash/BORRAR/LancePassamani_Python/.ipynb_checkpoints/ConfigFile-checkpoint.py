
import ConfigParser

class ConfigFile:
    """
    class for reading Automate.ini files
    """

    def __init__(self, fname='automate.ini'):
        """
        initialise by reading in the file
        read in nothing if it does not exist
        """
        _ini = ConfigParser.ConfigParser()
        import os
        try:
            _ini.readfp(open(fname))
        except IOError:
            _ini.readfp(open(fname[0].upper()+fname[1:])) # try first letter capitalised i.e. "Automate.ini"
        _cnfname= _ini.get('ConfigurationLocation','File')
        self._cnf = ConfigParser.ConfigParser()
        self._cnf.readfp(open(_cnfname))


    def CreatePath(self, filetype, stn, year):
        """
        make the path and return it
        """
        path = self._cnf.get('Data File Types & Location',filetype)
        subs = { '~': self._cnf.get('Data Locations','RawData'), \
                 '^': self._cnf.get('Data Locations','ProcessData'), \
                 '!': self._cnf.get('Data Locations','WebPath'), \
                 '%': self._cnf.get('Data Locations','CNFPath'), \
                 '$': self._cnf.get('Data Locations','ResultPath'), \
                 '#': str(stn), \
                 '@': filetype, \
                 'Y': str(year) }               
        ret=[]
        for p in path:
            try:
                ret.append(subs[p])
            except KeyError:
                ret.append(p)
        return "".join(ret)

    def getYear(self):
        """
        return the year from automate.ini
        """
        return int(self._cnf.get('Processing Days','Year'))

    def getMonth(self):
        """
        return the month from automate.ini
        note: motnh in automate.ini is in range 2-13

        return: month in range 1-12
        """
        return int(self._cnf.get('Processing Days','Month'))-1
    
    def getTestsStage1(self):
        """
        return as a dictionary the tests to do for stage 1
        """
        return dict(self._cnf.items('Stage 1 (Files Retrieved) Tests'))
        

    def getDataIniPath(self):
        """
        return the location of the data.ini file
        """
        return self._cnf.get('ConfigurationLocation','DTConfig')

# for Stage 7

    def getSensorConfig(self):
        return self._cnf.get('ConfigurationLocation', 'SENSORConfig')
        
    def getBSRNConfig(self):
        return self._cnf.get('ConfigurationLocation', 'BSRNConfig')
        
    def getSiteFile(self):
        return self._cnf.get('Data Location/Configuration', 'SiteFile')
        
