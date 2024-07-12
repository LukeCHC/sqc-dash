import os
from datetime import datetime
from pathlib import Path

#path = Path(__file__).parent.absolute() # returns: WindowsPath('C:/Users/chcuk/Desktop/LocalWorkDir/yyctoSP3/short')
                                         # Path(__file__) is the path to the current file.
                                         # .parent gives you the directory the file is in.
                                         # .absolute() gives you the full absolute path to it.
                                         # str(path) returns: 'C:\\Users\\chcuk\\Desktop\\LocalWorkDir\\yyctoSP3\\short'
class combineSP3:
   
    satsystems = ('G','R','C','E')
   
    def __init__(self, currentime, SP3_pathParsed):
        self.time_called =  currentime
        self.sp3_path = str(SP3_pathParsed)  #directory to read .sp3 files
        self.sp3_dirbank = []                #anything that sits inside the directory with .sp3 files
        self.sp3_sources = []                #seperated strings from files '' representing available sources GHZ, DLR..
        self.sp3_selected = []               #selected files for processing
        self.sp3_existingDates = []          #dates extracted from the names of files
        self.sp3_grouped = []                #.sp3 files grouped by the same date
        self.sp3_uniqueGroups = []            #.sp3 files to be processed
        self.sp3_timetags = []               # loaded timetags corresponding to uniqueGroup (node to node)
       
    def __call__(self):
        self.checkSP3()     #searching for .sp3 files
        self.sourcesSP3()   #identifying .sp3 sources
        self.groupSP3()     #grouping files
        self.uniqueSP3()    #isolating sp3 gourps against the same source and timedates
        self.connectSP3()
        self.deleteSP3()    #deleting processed files
   
    def checkSP3 (self):
        for sp3_file in os.listdir(self.sp3_path):        #reading the directory and creating a list of files available
            if sp3_file.endswith('.SP3') or sp3_file.endswith('.sp3'):
                self.sp3_dirbank.append(os.path.join(self.sp3_path, sp3_file))        
               
        if len(self.sp3_dirbank) == 0:
            with open(self.sp3_path + '/no_sp3_found.txt', 'w') as noSP3:
                noSP3.write( 
                                ('No ''.sp3'' files found in this directory.')
                                + ('\nObserved\t: ') + self.sp3_path
                                + ('\nCalled\t: ') + self.time_called.strftime("%Y %m %d - %H:%M:%S")
                )
        #looking for the correct name format, name proof check and all unique names available for sources from the files    
        else:
            for i in range(0,len(self.sp3_dirbank)):
                #if the date exists
                if (self.sp3_dirbank[i][-11:-6]).isdigit() == True:
                    self.sp3_sources.append(self.sp3_dirbank[i][-14:-11])
            sorted(self.sp3_dirbank)  # sorted(set(self.sp3_sources))
            self.sp3_sources = sorted(list(set(self.sp3_sources)))      
   
    def sourcesSP3 (self):   #creating a source list    
       for i in range(0,len(self.sp3_sources)): 
           groups = []    
           for sub in range(0, len(self.sp3_dirbank)):
               if self.sp3_sources[i]==self.sp3_dirbank[sub][-14:-11]:
                   groups.append(self.sp3_dirbank[sub])
           self.sp3_selected.append(groups)
         
       #creating a date list
       for i in range(0,len(self.sp3_dirbank)):
           if (self.sp3_dirbank[i][-11:-6]).isdigit() == True:
               self.sp3_existingDates.append(self.sp3_dirbank[i][-11:-6])
     
       sorted(self.sp3_existingDates)
       self.sp3_existingDates = sorted(list(set(self.sp3_existingDates)))
       
       index = 0
       while index < len(self.sp3_dirbank): #discarding unwanted items for processing
           if self.sp3_dirbank[index][-5] not in self.satsystems:
               self.sp3_dirbank.pop(index)
               index = 0
           index += 1  
                       
    def groupSP3 (self):            #grouping SP3 files by date
        sublist_length = []
        for sublist in self.sp3_selected:
            sublist_length.append(len(sublist))                          
               
        for i in range (0, len(self.sp3_existingDates)):
            sublist = []          
            for keylist in range(0, len(self.sp3_selected)):
                for element in range (0, sublist_length[keylist]):                  
                     if self.sp3_existingDates[i] == self.sp3_selected[keylist][element][-11:-6]:      
                         sublist.append(self.sp3_selected[keylist][element])
                         self.sp3_grouped.append(sublist)
             
        self.sp3_grouped = [list(i) for i in set(map(tuple, self.sp3_grouped))]
       
    def uniqueSP3 (self): #creating unique groups for the same source and date      
        for date in self.sp3_existingDates:
            for node in self.sp3_selected:
                sublist = []
                for element in node:
                    if date == element[-11:-6]:
                        sublist.append(element)
                if len(sublist) != 0:
                    self.sp3_uniqueGroups.append(sublist)
       
        self.sp3_uniqueGroup = [list(i) for i in set(map(tuple, self.sp3_uniqueGroups))]
       
    def openTT (self): #looking for timetags: unique group corresponds to tt nodes
        for node in self.sp3_uniqueGroups:
            groupTimetags = []
            for elementFile in node:
                sublist = []
                try:
                    with open(elementFile, 'r') as openedSP3:                
                            for line in openedSP3:
                                if line[0] == '*':                        
                                    date = ' '.join(line[1:].split())                                                                
                                    sublist.append(datetime.strptime(date[:-2], '%Y %m %d %H %M %S.%f'))                                                
                except:
                    pass
                if len(sublist) != 0:
                    groupTimetags.append(sublist)
            self.sp3_timetags.append(groupTimetags)
        
        unique_TTlist = []               
        for node in self.sp3_timetags:
            for TTlist in node:
                if TTlist not in unique_TTlist:
                    unique_TTlist.append(TTlist)
        self.sp3_timetags = unique_TTlist
        
    def connectSP3 (self):
        for node in self.sp3_uniqueGroups:
            opened_node = []
            destination_file  = None
            for file in node:
                if destination_file == None:
                    destination_file = file[:-6] + '_combined.sp3'
                opened_node.append(open(file,'r'))
            
            combined_file = open(destination_file, 'a')
    
            index = 0
            line_stored = [index for i in range(0, len(node))] 
            iterator_Files = iter(opened_node)
    
            while True:
                try:
                    opened_file = next(iterator_Files)  
                    
                    if opened_file.closed == True:
                        opened_file = next(iterator_Files)  
                    else:
                        if line_stored[index] != 0:
                            line = line_stored[index] # get the current/last line from the file
                        else:    
                            line = opened_file.readline()
                            if line[0] != '*':
                                while line[0] != '*':
                                    line = opened_file.readline()
                                    if line == '':
                                        opened_file.close()
                                        break   
    
                        while opened_file.closed == False:
                                if index == 0 and line[0] == '*': 
                                    TT_located = line
                                    combined_file.write(line)
                                    line = opened_file.readline()
                                    while line[0] != '*':
                                        combined_file.write(line)
                                        line = opened_file.readline()
                                        if line == '':
                                            opened_file.close()
                                            raise StopIteration
                                        elif line [0] == '*':
                                            line_stored[index] = line
                                            index += 1
                                            break
                                    break                               # to next file
                                else:
                                    # if line != TT_located:        # missing epochs            
                                    #     while line != TT_located:
                                    #         line = opened_file.readline()
                                    #         if line == '':
                                    #             with open(self.sp3_path + '/no_EpochsFound.txt', 'a') as TT_notFound:
                                    #                 TT_notFound.write( 
                                    #                                  ('The following time epochs were found to be missing: ')
                                    #                             +    (TT_located) 
                                    #                             +    ('in this file: ')
                                    #                             +    (str(opened_file)[-36:-29])
                                    #                             +    ('\n\n')
                                    #                 )
                                    #             opened_file.seek(0)
                                    #             line = opened_file.readline()
                                    #             while line != line_stored[index]:
                                    #                 line = opened_file.readline()
                                    #             break
                                    if line[0] == '*':
                                        line = opened_file.readline()
                                        while line[0] != '*':
                                            combined_file.write(line)
                                            line = opened_file.readline()
                                            if line == '':
                                                opened_file.close()  
                                                combined_file.write('\n')
                                                break
                                            elif line[0] == '*':
                                                line_stored[index] = line
                                                index += 1
                                                break
                                        break                           # to next file
                except StopIteration:
                    if line == '' and index == 0:
                        combined_file.close()          
                        for file in opened_node:
                            file.close()
                        break
                    index = 0
                    iterator_Files = iter(opened_node) # restart the node
           
    def deleteSP3(self):
        for node in self.sp3_uniqueGroup:
            for elementFile in node:
                os.remove(elementFile)      
                
combinedSP3 = combineSP3(datetime.now(), Path(__file__).parent.absolute())
combinedSP3()