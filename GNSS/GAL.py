# -*- coding: utf-8 -*-
"""
GALILEO Constant
Created on Tue Jul 14 2020
@author: Dr Hui Zhi
"""

class GAL():
    E1  = 1575.42E+06                # GALILEO E1  Frequency (Hz)
    E5a = 1176.45E+06                # GALILEO E5a Frequency (Hz)
    E5b = 1207.14E+06                # GALILEO E5b Frequency (Hz)
    E5  = 1191.795E+06               # GALILEO E5  Frequency (Hz) - (E5a + E5b)
    E6  = 1278.75E+06                # GALILEO E6  Frequency (Hz)
    MaxNoSV = 36
    
    miu     = 3.986004418E+14        # WGS-84 value of the Earth's universal gravitational parameter
    
    ephInterval = 600                # 10minutes / in seconds
    ephDelay = 0                     # starts from the beginning of the day
    ephFlag = 4                      # 4 - sent at time epoch
    
    SV = ['E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08', 'E09', 'E10',
          'E11', 'E12', 'E13', 'E14', 'E15', 'E16', 'E17', 'E18', 'E19', 'E20',
          'E21', 'E22', 'E23', 'E24', 'E25', 'E26', 'E27', 'E28', 'E29', 'E30',
          'E31', 'E32', 'E33', 'E34', 'E35', 'E36']
    
    E1_code  = ['C1A', 'L1A', 'D1A', 'S1A',
                'C1B', 'L1B', 'D1B', 'S1B',
                'C1C', 'L1C', 'D1C', 'S1C',
                'C1X', 'L1X', 'D1X', 'S1X',
                'C1Z', 'L1Z', 'D1Z', 'S1Z']
    
    E5a_code = ['C5I', 'L5I', 'D5I', 'S5I',
                'C5Q', 'L5Q', 'D5Q', 'S5Q',
                'C5X', 'L5X', 'D5X', 'S5X']
    
    E5b_code = ['C7I', 'L7I', 'D7I', 'S7I',
                'C7Q', 'L7Q', 'D7Q', 'S7Q',
                'C7X', 'L7X', 'D7X', 'S7X']
    
    E5_code  = ['C8I', 'L8I', 'D8I', 'S8I',
                'C8Q', 'L8Q', 'D8Q', 'S8Q',
                'C8X', 'L8X', 'D8X', 'S8X']
    
    E6_code  = ['C6A', 'L6A', 'D6A', 'S6A',
                'C6B', 'L6B', 'D6B', 'S6B',
                'C6C', 'L6C', 'D6C', 'S6C',
                'C6X', 'L6X', 'D6X', 'S6X',
                'C6Z', 'L6Z', 'D6Z', 'S6Z']
    
    E1_channel  = ['A PRS', 'B I/NAV OS/CS/SoL', 'C no data', 'B+C', 'A+B+C']
    E5a_channel = ['I F/NAV OS', 'Q no data', 'I+Q']
    E5b_channel = ['I I/NAV OS/CS/SoL', 'Q no data', 'I+Q']
    E5_channel  = ['I', 'Q', 'I+Q']
    E6_channel  = ['A PRS', 'B C/NAV CS', 'C no data', 'B+C', 'A+B+C']
    
    SISRE_Wr   = 0.98
    SISRE_Wac2 = 1/61
    
    CLOCK_TYPE = ['RAFS', 'PHM', 'RAFS-PHM'] # 'Rubidium', 'Hydrogen', 'Rubidium-Hydrogen'
    # order by launch date
    CLOCK_RAFS = ['E12', 'E20']
    CLOCK_PHM = ['E11', 'E19', 'E34', 'E10']
    CLOCK_RAFS_PHM = ['E18', 'E14', 'E26', 'E22', 'E24', 'E30', 'E08', 'E09', 'E01', 'E02', 'E07', 
                     'E03', 'E04', 'E05', 'E21', 'E25', 'E27', 'E31', 'E36', 'E13', 'E15', 'E33'] 
    
    @classmethod
    def clock (cls, passed_SV):
        if passed_SV not in cls.CLOCK_RAFS and passed_SV not in cls.CLOCK_PHM and passed_SV not in cls.CLOCK_RAFS_PHM:
            raise Exception('Passed satellite/PRN does not exist')
        elif passed_SV in cls.CLOCK_RAFS:
            return cls.CLOCK_TYPE[0]
        elif passed_SV in cls.CLOCK_PHM:
            return cls.CLOCK_TYPE[1]
        else: 
            return cls.CLOCK_TYPE[2]
    
    @classmethod
    def obs_code (cls, passed_code):
        phase_measurement = None
        channel_code = None
        band_freq = None
        arg_validation = None
        code_output = []
        E1_channel  = [channel.lower() for channel in cls.E1_channel]
        E5a_channel = [channel.lower() for channel in cls.E5a_channel]
        E5b_channel = [channel.lower() for channel in cls.E5b_channel]
        E5_channel  = [channel.lower() for channel in cls.E5_channel]
        E6_channel  = [channel.lower() for channel in cls.E6_channel]
        
        if passed_code.lower() in (E1_channel + E5a_channel + E5b_channel + E5_channel + E6_channel):
            arg_validation = True
            passed_code = passed_code.lower()
            passed_stored = passed_code
            if passed_code in E1_channel:
                channel_code = ['A', 'B', 'C', 'X', 'Z']
                E1_channel = list(zip(E1_channel, channel_code))    
                for channel in E1_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.E1_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band E1/1575.42-MHZ: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in E5a_channel:
                channel_code = ['I', 'Q', 'X']
                E5a_channel = list(zip(E5a_channel, channel_code))    
                for channel in E5a_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.E5a_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band E5a/1176.45-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in E5b_channel:
                channel_code = ['I', 'Q', 'X']
                E5b_channel = list(zip(E5b_channel, channel_code))    
                for channel in E5b_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.E5b_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band E5b/1207.140-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in E5_channel:
                channel_code = ['I', 'Q', 'X']
                E5_channel = list(zip(E5_channel, channel_code))    
                for channel in E5_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.E5_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band E5(E5a+E5b)/1191.795-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in E6_channel:
                channel_code = ['A', 'B', 'C', 'X', 'Z']
                E6_channel = list(zip(E6_channel, channel_code))    
                for channel in E6_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.E6_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band E6/1278.75-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
                
        if passed_code.lower() in ('pseudorange', 'pseudo', 'carrierphase', 'carrier', 'doppler', 'signalstrength', 'signal'):
            arg_validation = True
            passed_code = passed_code.lower()
            if passed_code in ('pseudorange', 'pseudo'):  
                phase_measurement = 'C'
            elif passed_code in ('carrierphase', 'carrier'):  
                phase_measurement = 'L'
            elif passed_code == 'doppler':
                phase_measurement = 'D'
            elif passed_code in ('signalstrength', 'signal'):  
                phase_measurement = 'S'  
            for obs_code in (cls.E1_code + cls.E5a_code + cls.E5b_code + cls.E5_code + cls.E6_code):
                if obs_code[0] == phase_measurement:
                    code_output.append(obs_code)    
            print(code_output)    
        if passed_code.upper() in (cls.E1_code + cls.E5a_code + cls.E5b_code + cls.E5_code + cls.E6_code):
            arg_validation = True
            passed_code = passed_code.upper()
            if passed_code[0] == 'C':  
                phase_measurement = 'Pseudo-range'
            elif passed_code[0] == 'L':
                phase_measurement = 'Carrier-phase'
            elif passed_code[0] == 'D':
                phase_measurement = 'Doppler'
            elif passed_code[0] == 'S':
                phase_measurement = 'Signal-strength'  
            if passed_code in cls.E1_code:
                band_freq = 'Band E1/1575.42-MHZ'
                if passed_code[2] == 'A':
                    channel_code = cls.E1_channel[0]
                elif passed_code[2] == 'B':
                    channel_code = cls.E1_channel[1]
                elif passed_code[2] == 'C':
                    channel_code = cls.E1_channel[2]
                elif passed_code[2] == 'X':
                    channel_code = cls.E1_channel[3]
                elif passed_code[2] == 'Z':
                    channel_code = cls.E1_channel[4]
            if passed_code in cls.E5a_code:
                band_freq = 'Band E5a/1176.45-Mhz'
                if passed_code[2] == 'I':
                    channel_code = cls.E5a_channel[0]
                elif passed_code[2] == 'Q':
                    channel_code = cls.E5a_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.E5a_channel[2]
            if passed_code in cls.E5b_code:
                band_freq = 'Band E5b/1207.140-Mhz'
                if passed_code[2] == 'I':
                    channel_code = cls.E5b_channel[0]
                elif passed_code[2] == 'Q':
                    channel_code = cls.E5b_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.E5b_channel[2]
            if passed_code in cls.E5_code:
                band_freq = 'Band E5(E5a+E5b)/1191.795-Mhz'
                if passed_code[2] == 'I':
                    channel_code = cls.E5_channel[0]
                elif passed_code[2] == 'Q':
                    channel_code = cls.E5_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.E5_channel[2]
            if passed_code in cls.E6_code:
                band_freq = 'Band E6/1278.75-Mhz'
                if passed_code[2] == 'A':
                    channel_code = cls.E6_channel[0]
                elif passed_code[2] == 'B':
                    channel_code = cls.E6_channel[1]
                elif passed_code[2] == 'C':
                    channel_code = cls.E6_channel[2]
                elif passed_code[2] == 'X':
                    channel_code = cls.E6_channel[3]
                elif passed_code[2] == 'Z':
                    channel_code = cls.E6_channel[4]
            if phase_measurement is not None:
                print (passed_code + ': ' + channel_code + ' channel-code derived ' + band_freq + ' ' + phase_measurement)  
        if arg_validation == None:
            print('Given code is not valid.')