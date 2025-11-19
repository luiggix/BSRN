import datetime
import copy

# caledit
class datastore:
    pass

class CantInsertFirstRecordError:
    pass

class CantInsertExistingTimeError:
    pass

class BadRecDateError:
    pass

class caledit:
    # class to read and write cal files.

    def __init__(self,fname):
        # read in info from file fname

        self.ds = datastore()
        
        try:
            lines = open(fname).readlines()
            self._parse(lines)
#            self.write_to_file('test.cal')
            self.ds.empty = False
        except IOError:
            # no file
            self.ds.empty = True
            pass


    def _parse(self,data):
        """
        extract the data from the lines of the file


        comment
        stn start finish numquantities numcombinations
        quants { symbol = name }
        
        combserial [ serial ]
        combquant [ symbol ]

        numentries

        entry[ {'line', 'start', 'finish' } ]

        record [ {'start', 'finish', 'mod', 'numinst', 'numcomm', 'inst':[], 'comm':[] } ]
        record['inst'] [ {'comb', 'serial', 'symbol', 'cal'} ]
        record['comm'] [ comments ]
        
        """
        # comment
        self.ds.comment = data.pop(0).strip('\n')

        # stn, start time, finish time, numquantities, numcombinations
        self.ds.stn,self.ds.start,self.ds.finish,self.ds.numquantities,self.ds.numcombinations = data.pop(0).split()

        self.ds.numquantities = int(self.ds.numquantities)
        self.ds.numcombinations = int(self.ds.numcombinations)

        # GLO global etc
        self.ds.quants={}
        for i in range(self.ds.numquantities):
            symbol,name = data.pop(0).split()
            self.ds.quants[symbol]=name

        # instrument serial combinations
        self.ds.combquant=[]
        self.ds.combserial=[]
        for i in range(self.ds.numcombinations):
            key,serial_symbol = data.pop(0).split(' ',1)            
            self.ds.combserial.append(serial_symbol[0:20])
            self.ds.combquant.append(serial_symbol[21:24])
            
        
        # num entries
        self.ds.numentries = int(data.pop(0))
        # read entries (index)
        self.ds.entry = []
        for i in range(self.ds.numentries):
            line,start,end = data.pop(0).split()
            self.ds.entry.append( {'line':int(line), 'start':start, 'finish':end} )
            
        # read records
        self.ds.record = []
        for i in range(self.ds.numentries):
            stn,start,end,mod,numinst,numcomm = data.pop(0).split()
            self.ds.record.append( {'start':start, 'finish':end, 'mod':mod, 'numinst':int(numinst), 'numcomm':int(numcomm), 'inst':[], 'comm':[]} )

            for j in range(int(numinst)):
                comb_serial_symbol_cal = data.pop(0).strip('\n')
##                print comb_serial_symbol_cal
##                print comb_serial_symbol_cal[0:3]
##                print comb_serial_symbol_cal[4:24]
##                print comb_serial_symbol_cal[25:28]
##                print comb_serial_symbol_cal[29:]
                self.ds.record[-1]['inst'].append({'comb':comb_serial_symbol_cal[0:3], \
                                                   'serial':comb_serial_symbol_cal[4:24], \
                                                   'symbol':comb_serial_symbol_cal[25:28], \
                                                   'cal':comb_serial_symbol_cal[29:].strip('\n')})

            for j in range(int(numcomm)):
                self.ds.record[-1]['comm'].append(data.pop(0).strip('\n'))            


    def generate_output(self):
        """
        generate output for file
        """
        out = []
        
        # comment
        out.append('%-79s' % self.ds.comment[:79])

        # stn, start time, finish time, numquantities, numcombinations
        out.append('%03d %s %s %3d %3d' % (int(self.ds.stn),self.ds.start,self.ds.finish,self.ds.numquantities,self.ds.numcombinations))

        # GLO global etc
        for k in self.ds.quants.keys():
            out.append('%s %-20s'%(k,self.ds.quants[k][:20]))

        # instrument serial combinations
        for i in range(len(self.ds.combserial)):
            out.append('%s %-20s %s'%(i+1,self.ds.combserial[i][:20],self.ds.combquant[i]))
        
        
        # num entries
        out.append(str(self.ds.numentries))

        for e in self.ds.entry:
            out.append('%s %s %s'%(e['line'],e['start'],e['finish']))
            
        # read records
        for r in self.ds.record:
            out.append('%3s %s %s %s %3s %3s'%(self.ds.stn,r['start'],r['finish'],r['mod'],r['numinst'],r['numcomm']))

            for ins in r['inst']:
                out.append('%3s %-20s %s %.6f'%(ins['comb'],ins['serial'][:20],ins['symbol'],float(ins['cal'])))
                
            for c in r['comm']:
                out.append(c)

        return out

    def write_to_file(self,fname):
        out = self.generate_output()
        f = open(fname,'w')
        f.write('\r\n'.join(out))
        f.write('\r\n')
        f.close()

    def datestring_to_datetime(self,date):
        """
        YYYYDDDMMHH to datetime
        """
        # daynumber starts at zero in YYYYDDDMMHH
        return datetime.datetime(int(date[0:4]),1,1, int(date[7:9]),int(date[9:11])) + datetime.timedelta(int(date[4:7]))

        # use below if daynumber starts at one in YYYYDDDMMHH
        # return datetime.datetime(int(date[0:4]),1,1, int(date[7:9]),int(date[9:11])) + datetime.timedelta(int(date[4:7])-1)

    def datetime_to_datestring(self,date):
        """
        datetime to YYYYDDDMMHH
        """
        # daynumber starts at zero in YYYYDDDMMHH
        ret=[]
        ret.append(date.strftime('%Y'))
        ret.append('%03d' % (int(date.strftime('%j'))-1) )
        ret.append(date.strftime('%H%M'))        
        return "".join(ret)

        # use below if daynumber starts at one in YYYYDDDMMHH
        # return date.('%Y%j%H%M')
        
        
    def printdate(self,date):
        """
        format date for printing

        YYYYDDDMMHH to DD/MM/YYYY HH:MM

        daynumber starts at zero!
        """
        d = self.datestring_to_datetime(date)
        return d.strftime('%d/%m/%Y %H:%M')

    def getdmyhm(self,date):
        """
        return a list of [yyyy,mm,dd,hh,mm]

        YYYYDDDMMHH or datetime to [YYYY,MM,DD,HH,MM]

        daynumber starts at zero!
        """
        try:
            dummy = date.strftime('%d')
        except AttributeError:
            date = self.datestring_to_datetime(date)
        return [date.strftime('%d'),\
                date.strftime('%m'),
                date.strftime('%Y'),
                date.strftime('%H'),
                date.strftime('%M')]

    def now(self):
        """
        return now in yyyydddhhmmss format

        now as YYYYDDDMMHH

        daynumber starts at zero!
        """
        return self.datetime_to_datestring(datetime.datetime.now())


    def dmyhm_to_string(self,day,month,year,hour,minute):
        """
        from DD/MM/YYYY HH:MM to YYYYDDDHHMM

        daynumber starts at zero!        
        """
        d = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute))
        return self.datetime_to_datestring(d)

    def previous_minute(self,datestring):
        """
        return datestring minus one minute
        """
        d = self.datestring_to_datetime(datestring)
        d = d - datetime.timedelta(minutes=1)
        return self.datetime_to_datestring(d)

    def add_minute(self,datestring,minutes=1):
        """
        return datestring plus 'minutes' minutes
        """
        d = self.datestring_to_datetime(datestring)
        d = d + datetime.timedelta(minutes=minutes)
        return self.datetime_to_datestring(d)

        
    def append_record(self, rec):
        """
        add a record to the last, place. record is in the same format as all records
        rec['now'] overwritten
        rec['finish'] overwritten

        record [ {'start', 'finish', 'mod', 'numinst', 'numcomm', 'inst':[], 'comm':[] } ]
        record['inst'] [ {'comb', 'serial', 'symbol', 'cal'} ]
        record['comm'] [ comments ]

        """

        #SO FAR ONLY FOR NO NEW COMBINATIONS
        
        good = True

        start = int(rec['start'])

        if start<= int(self.ds.record[-1]['start']):
            good = False

        if not good:
            raise 'bad record for appending'
        

        # record
        rec['finish'] = self.ds.record[-1]['finish']
        self.ds.record[-1]['finish'] = self.previous_minute(start)
        self.ds.entry[-1]['finish'] = self.previous_minute(start)
        now = self.now()
        self.ds.record[-1]['mod'] = now
        rec['mod']=now
        self.ds.entry.append({'start':rec['start'], \
                              'finish':rec['finish'], \
                              'line':self.ds.entry[-1]['line'] + \
                              self.ds.record[-1]['numinst'] + self.ds.record[-1]['numcomm'] \
                              + 1})
                              
        self.ds.record.append(rec)

        self.ds.numentries = self.ds.numentries + 1

        
    def insert_record(self, rec):
        """
        insert a record. record is in the same format as all records
        rec['now'] overwritten
        rec['finish'] overwritten

        record [ {'start', 'finish', 'mod', 'numinst', 'numcomm', 'inst':[], 'comm':[] } ]
        record['inst'] [ {'comb', 'serial', 'symbol', 'cal'} ]
        record['comm'] [ comments ]

        """

        #ONLY FOR NO NEW COMBINATIONS
        
        good = True

        # record that applies at rec start time
        recnum = self.get_recordnumber(self.datestring_to_datetime(rec['start']))

        if not recnum:
            # would be new first record
            raise CantInsertFirstRecordError

        #test if rec start does not equal the start time of record that applies
        if int(rec['start'])<= int(self.ds.record[recnum]['start']):
            good = False
            
        #test if rec start does not equal the finish time of record that applies
        if int(rec['start'])>= int(self.ds.record[recnum]['finish']):
            good = False

        if not good:
            raise CantInsertExistingTimeError
        "can't insert: bad start time"
        

        # record
        rec['finish'] = self.ds.record[recnum]['finish']
        self.ds.record[recnum]['finish'] = self.previous_minute(rec['start'])
        self.ds.entry[recnum]['finish'] = self.previous_minute(rec['start'])
        now = self.now()
        self.ds.record[recnum]['mod'] = now
        rec['mod']=now
        self.ds.numentries = self.ds.numentries + 1 # must increment before entry_insert
        self.ds.record.insert(recnum+1,rec) # must insert record before entry_insert
        self.entry_insert(recnum+1,{'start':rec['start'], \
                              'finish':rec['finish']})
        



    def entry_insert(self, position, ent):
        """
        insert entry ent before position postion
        then recalc the 'line's
        """
        self.ds.entry.insert(position,\
                             {'start':ent['start'], \
                              'finish':ent['finish'], \
                              'line':0})
        self.recalc_lines()


    def recalc_lines(self):
        """
        recalculate numentries and the 'line' parameters for entry
        """
        self.ds.numentries = len(self.ds.entry)
        
        linenum =   1 \
                  + 1 \
                  + self.ds.numquantities \
                  + self.ds.numcombinations \
                  + 1 \
                  + self.ds.numentries \
                  + 1
                  
        for e,r in zip(self.ds.entry,self.ds.record):
            e['line'] = linenum
            linenum = linenum + 1 + r['numinst'] + r['numcomm']

    def delete_record(self, recnum):
        """
        delete record number recnum
        """
        recnum=int(recnum)

        if recnum==0:
            self.ds.start = self.ds.record[1]['start']
        else:
            finish = self.ds.record[recnum]['finish']
            self.ds.record[recnum-1]['finish']=finish
            self.ds.entry[recnum-1]['finish']=finish
        self.ds.numentries = self.ds.numentries - 1 # must decrement before entry_insert
        self.ds.record.pop(recnum) # must delete record before entry_delete
        self.entry_delete(recnum)

    def entry_delete(self, position):
        """
        delete entry at position postion
        then recalc the 'line's
        """
        self.ds.entry.pop(position)
        self.recalc_lines()
      

    def get_combination_number(self, serial, symbol):
        """
        if combination exists return the number, if not return -1
        """
        for i in range(len(self.ds.combquant)):
            if self.ds.combserial[i]==serial and self.ds.combquant[i]==symbol:
                return i+1
        return -1

    def add_combination(self, serial, symbol):
        """
        add the combination, return the number
        assume it doesn't exist
        """
        self.ds.combquant.append(symbol)
        self.ds.combserial.append(serial)
        self.ds.numcombinations = self.ds.numcombinations + 1
        return len(self.ds.combquant)
        
        
    def force_combination_number(self, serial, symbol):
        """
        if combination exists return the number, if not generate a new one
        """
        num = self.get_combination_number(serial, symbol)
        if num == -1:
            num = self.add_combination(serial, symbol)
        return num

    def get_next_record(self, date, n=1):
        """
        get the record after the record applying on a certain date
        date in datetime format
        return nothing if already at the last record with the current date
        """
        d = self.datetime_to_datestring(date)
        do_next=False
        for r in self.ds.record:
            if do_next:
                return copy.deepcopy(r)                
            if r['start']<= d and r['finish'] >= d:
                do_next=True

        
    def get_record(self, date):
        """
        get the record applying on a certain datetime
        date in datetime format
        """
        if self.ds.empty:
            return []
        d = self.datetime_to_datestring(date)
        for r in self.ds.record:
            if r['start']<= d and r['finish'] >= d:
                return copy.deepcopy(r)

    def get_recordnumber(self, date):
        """
        get the record number applying at a certain datetime
        date in datetime format
        recordnumber starts at zero
        """
        if self.ds.empty:
            raise BadRecDateError # not really the correct error to raise here. There are no records at all.
        d = self.datetime_to_datestring(date)
        for i in range(len(self.ds.record)):
            if self.ds.record[i]['start']<= d and self.ds.record[i]['finish'] >= d:
                return i
        raise BadRecDateError

        
    def get_record_n(self,n):
        """
        return the nth record. zero based list
        """
        return copy.deepcopy(self.ds.record[n])


    def get_records(self,m,n):
        """
        return the mth to nth records inclusive. zero based list
        """
        if self.ds.empty:
            return []
        if m<0:
            m=0
        if n<0:
            n=0
            #m=0 #make the start zero as well
            
        return copy.deepcopy(self.ds.record[m:n+1])
                

    def get_serial_from_record(self, rec, symbol):
        """
        given a record and a symbol, return the serialnumber
        """
        for ins in rec['inst']:
            if ins['symbol']==symbol:
                return ins['serial']

    def get_cal_from_record(self, rec, symbol):
        """
        given a record and a symbol, return the cal
        """
        for ins in rec['inst']:
            if ins['symbol']==symbol:
                return ins['cal']



if __name__ == '__main__': 
    c = caledit('//memsat/data.process/solar/cal/201/201.cal')
    rec={}
    rec['start']='20063400003'
    rec['numinst']=4
    rec['numcomm']=0
    rec['inst']=[]
    rec['comm']=[]
    num = c.force_combination_number('CH1-940043','DIR')
    rec['inst'].append({'comb':num, 'serial':'CH1-940043',
                        'symbol':'DIR', 'cal':'10.28'})
    num = c.force_combination_number('PIR-29070F3','TER')
    rec['inst'].append({'comb':num, 'serial':'PIR-29070F3',
                        'symbol':'TER', 'cal':'-4.37'})
    num = c.force_combination_number('CM11-924025','GLO')
    rec['inst'].append({'comb':num, 'serial':'CM11-924025',
                        'symbol':'GLO', 'cal':'-4.54'})
    num = c.force_combination_number('CM11-924043','DIF')
    rec['inst'].append({'comb':num, 'serial':'CM11-924043',
                        'symbol':'DIF', 'cal':'4.65'})

    c.append_record(rec)
    out = c.generate_output()

    print out
    

