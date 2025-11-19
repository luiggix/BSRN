# Items.cpp: implementation of the CItems class.

class NoOptionError:
    pass

class NoSectionError(Exception):
    def __init__(self,section):
        self.section=section
    def __str__(self):
        return repr(self.section)

class NoFileError:
    pass

class IniReadWriter:
    """
    class to speed up the reading and writing of ini data

    reads whole file into a list for each section
    does not parse option=value until required by a funtion

    order of data is preserved when writing, but comments are lost
    """

    def __init__(self,filename,status='append'):
        """
        read in the file to a list
        store the location of the sections

        self._section_range: dict[sectionname] = [startline of section,endline of section+1]
        """
        if status=='new':
            # new file
            self._section_list=[]
            self._sections={}
        else:
            # existing file
            try:
                self._totalfile = open(filename).readlines()
            except IOError:
                raise NoFileError
            self._section_range={} #store where each section begins and ends
            self._file=self._noCommentFile()
            self._storeSections()
            self._sectionsRemoveBlanks()

    def _noCommentFile(self):
        """
        return a list of the file with the comment lines removed
        """
        return [l for l in self._totalfile if l[0]!=';']

            
    def _storeSections(self):
        """
        store the section names in _section_list
        store each section contents in _sections[sectionname]
        """
        sectionname=''
        self._section_list=[]
        self._sections={}
        for i in range(len(self._file)):
            if self._file[i][0]=='[':
                if sectionname:
                    self._section_list.append(sectionname)
                    self._sections[sectionname]=self._file[startline:i]
                startline=i+1
                sectionname=self._file[i][1:-2]
        if sectionname:
            self._section_list.append(sectionname)
            self._sections[sectionname]=self._file[startline:i+1]


    def _sectionsRemoveBlanks(self):
        """
        remove blank lines from the end of sections
        """
        for k,v in self._sections.iteritems():
            self._sections[k] = self._removeBlankLines(self._sections[k])


    def _removeBlankLines(self, a):
        """
        remove blank lines from the end of list a
        return new list
        """
        while not a[-1].rstrip():
            a.pop()
        return a


    def items(self,sec):
        """
        return list of option,value pairs in section split around =
        """
        out=[]
        try:
            for line in self._sections[sec]:
                try:
                    k,v = line.split('=',1)                    
                    out.append([k,v.rstrip()])
                except ValueError:
                    #no '=' on the line
                    pass
        except KeyError:
            raise NoSectionError(sec)
        return out


    def dictitems(self,sec):
        """
        return dict of [option]=value  in section split around =
        """
        out={}

        try:
            for line in self._sections[sec]:
#                try:
                    k,v = line.split('=',1)
                    out[k]=v.rstrip()
#                except ValueError:                    
#                    pass  # no '=' on the line
        except KeyError:
            raise NoSectionError(sec)
        return out


    def get(self,sec,opt):
        """
        return value in section sec for option opt
        [sec]
        opt=returnvalue
        """
        for line in self._sections[sec]:
            try:
                o,v = line.split('=',1)
                if opt==o:
                    return v.rstrip()
            except ValueError:
                #no '=' on the line, probably a blank line or comment
                pass
        raise NoOptionError


    def write(self,fout):
        """
        write out the in date to file

        parameters:
        fname: name of file to write out to
        """
        for sec in self._section_list:
            fout.write('['+sec+']\n')
            for line in self._sections[sec]:
                fout.write(line)
            fout.write('\n') # blank line after each section's data
        fout.close()


    def set(self,sec,opt,val):
        """
        set opt=val in existing section sec
        """
        opteq = opt + '='
        # does opt already exist, if so change it
        try:
            for i in xrange(len(self._sections[sec])):
                if self._sections[sec][i].startswith(opteq):
                    self._sections[sec][i] = "%s=%s\n"%(top,val)
                    return
            # opt does not exist so add it
            self._sections[sec].append("%s=%s\n"%(opt,val))
        except KeyError:
            raise NoSectionError(sec)


    def setNewOption(self,sec,opt,val):
        """
        set opt=val in existing section sec
        opt should not already exist

        if opt does already exists there will be
        two opts in the section (this may be desired sometimes,
        though non-standard ini)
        """
        # opt does not exist so add it
        self._sections[sec].append("%s=%s\n"%(opt,val))
        

    def sections(self):
        """
        return a list of all the sections
        """
        return self._section_list

    def add_section(self,sec):
        """
        add a section
        """
        if sec in self._section_list:
            return
        self._section_list.append(sec)
        self._sections[sec]=[]

    def remove_section(self,sec):
        """
        remove a section
        """
        try:
            self._section_list.remove(sec)
            self._sections.pop(sec)
        except ValueError:
            raise NoSectionError(sec)

        
