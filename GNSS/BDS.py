# -*- coding: utf-8 -*-
"""
BDS Constant
Created on Tue Jul 14 2020
@author: Dr Hui Zhi
"""

class BDS():
    B12 = 1561.098E+06              # BDS B1-2 Frequency (Hz)
    B1  = 1575.42E+06               # BDS B1   Frequency (Hz)
    B2a = 1176.45E+06               # BDS B2a  Frequency (Hz) - BDS-3 Signals
    B2b = 1207.14E+06               # BDS B2b  Frequency (Hz) - BDS-2 Signals
    B2  = 1191.795E+06              # BDS B2   Frequency (Hz) - BDS-3 Signals
    B3  = 1268.52E+06               # BDS B3   Frequency (Hz)
    MaxNoSV = 63
    
    C   = 2.99792458E+08            # Speed of light         (meter/second)
    Pi  = 3.1415926535898
    a   = 6378137.0                 # Semi-major axis (m)
    miu = 3.986004418E+14           # WGS-84 value of the Earth's universal
                                    # gravitational parameter
    rad = 7.2921150E-5              # WGS-84 value of the Earth's rotation
                                    # rate (EarthRate)
    F   = -4.442807309e-10          # sec/(meter)**(1/2)
    
    ephInterval = 3600            # 1hours / in seconds
    ephDelay = 0                  # starts from the beginning of the day
    ephFlag = 1                   # 1 - sent at time epoch
    
    #= http://www.csno-tarc.cn/en/system/constellation
    SV = ['C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'C09', 'C10',
          'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20',
          'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30',
          'C31', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37', 'C38', 'C39', 'C40',
          'C41', 'C42', 'C43', 'C44', 'C45', 'C46', 'C47', 'C48', 'C49', 'C50',
          'C51', 'C52', 'C53', 'C54', 'C55', 'C56', 'C57', 'C58', 'C59', 'C60',
          'C61', 'C62', 'C63']
    #= MEO also included in IGSO list
    IGSO = ['C06', 'C07', 'C08', 'C09', 'C10',
          'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20',
          'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30',
          'C31', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37', 'C38', 'C39', 'C40',
          'C41', 'C42', 'C43', 'C44', 'C45', 'C46', 'C47', 'C48', 'C49', 'C50',
          'C51', 'C52', 'C53', 'C54', 'C55', 'C56', 'C57', 'C58']
    
    GEO = ['C01', 'C02', 'C03', 'C04', 'C05', 'C59', 'C60', 'C61', 'C62', 
           'C63']
    geo = [[2,1], [2,2], [2,3], [2,4], [2,5], [2,18]]
    
    B12_code = ['C1I', 'L1I', 'D1I', 'S1I',
                'C1Q', 'L1Q', 'D1Q', 'S1Q',
                'C1X', 'L1X', 'D1X', 'S1X',
                'C2I', 'L2I', 'D2I', 'S2I',
                'C2Q', 'L2Q', 'D2Q', 'S2Q',
                'C2X', 'L2X', 'D2X', 'S2X']
    
    B1_code  = ['C1D', 'L1D', 'D1D', 'S1D',
                'C1P', 'L1P', 'D1P', 'S1P',
                'C1X', 'L1X', 'D1X', 'S1X',
                'C1A', 'L1A', 'D1A', 'S1A',
                       'L1N', 'D1N', 'S1N']
    
    B2a_code = ['C5D', 'L5D', 'D5D', 'S5D',
                'C5P', 'L5P', 'D5P', 'S5P',
                'C5X', 'L5X', 'D5X', 'S5X']
    
    B2b_code = ['C7I', 'L7I', 'D7I', 'S7I',
                'C7Q', 'L7Q', 'D7Q', 'S7Q',
                'C7X', 'L7X', 'D7X', 'S7X',
                'C7D', 'L7D', 'D7D', 'S7D',
                'C7P', 'L7P', 'D7P', 'S7P',
                'C7Z', 'L7Z', 'D7Z', 'S7Z']
    
    B2_code  = ['C8D', 'L8D', 'D8D', 'S8D',
                'C8P', 'L8P', 'D8P', 'S8P',
                'C8X', 'L8X', 'D8X', 'S8X']
    
    B3_code  = ['C6I', 'L6I', 'D6I', 'S6I',
                'C6Q', 'L6Q', 'D6Q', 'S6Q',
                'C6X', 'L6X', 'D6X', 'S6X',
                'C6A', 'L6A', 'D6A', 'S6A']
    
    B12_channel = ['I', 'Q', 'I+Q']
    B1_channel = ['Data', 'Pilot', 'Data+Pilot', 'B1A', 'Codeless']
    B2a_channel = ['Data', 'Pilot', 'Data+Pilot']
    B2b_channel = ['I', 'Q', 'I+Q', 'Data', 'Pilot', 'Data+Pilot']
    B2_channel = ['Data', 'Pilot', 'Data+Pilot']
    B3_channel = ['I', 'Q', 'I+Q', 'B3A']
    
    SISRE_Wr_IGSO   = 0.99          # IGSO,GEO
    SISRE_Wac2_IGSO = 1/126         # IGSO,GEO
    SISRE_Wr_MEO    = 0.98          # MEO
    SISRE_Wac2_MEO  = 1/54          # MEO
    
    CLOCK_TYPE = ['RB','HMAC'] # 'Rubidium', 'Hydrogen'
    # ordered by launch date
    CLOCK_RB =   ['C06', 'C04', 'C07', 'C08', 'C09', 'C10', 'C05', 'C11', 'C12', 'C14', 'C02', 'C31', 'C57',
                  'C58', 'C03', 'C13', 'C19', 'C20', 'C21', 'C22', 'C16', 'C23', 'C24', 'C32', 'C33', 'C36',
                  'C37', 'C01', 'C45', 'C46'] 
    CLOCK_HMAC = ['C18', 'C27', 'C28', 'C29', 'C30', 'C26', 'C25', 'C35', 'C34', 'C59', 'C38', 'C39', 'C40',
                  'C43', 'C44', 'C41', 'C42', 'C60','C61']     
    
    @classmethod
    def clock (cls, passed_SV):
        if passed_SV not in cls.CLOCK_RB and passed_SV not in cls.CLOCK_HMAC:
            raise Exception('Passed satellite/PRN does not exist')
        elif passed_SV in cls.CLOCK_HMAC:
            return cls.CLOCK_TYPE[1]
        else: 
            return cls.CLOCK_TYPE[0]
        
    @classmethod
    def obs_code (cls, passed_code):
        phase_measurement = None
        channel_code = None
        band_freq = None
        arg_validation = None
        code_output = []
        B12_channel = [channel.lower() for channel in cls.B12_channel]
        B1_channel  = [channel.lower() for channel in cls.B1_channel]
        B2a_channel = [channel.lower() for channel in cls.B2a_channel]
        B2b_channel = [channel.lower() for channel in cls.B2b_channel]
        B2_channel  = [channel.lower() for channel in cls.B2_channel]
        B3_channel  = [channel.lower() for channel in cls.B3_channel]
        
        if passed_code.lower() in (B12_channel + B1_channel + B2a_channel + B2b_channel + B2_channel + B3_channel):
            arg_validation = True
            passed_code = passed_code.lower()
            passed_stored = passed_code
            if passed_code in B12_channel:
                channel_code = ['I', 'Q', 'X']
                B12_channel = list(zip(B12_channel, channel_code))    
                for channel in B12_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.B12_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band B1-2/1561.098-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in B1_channel:
                channel_code = ['D', 'P', 'X', 'A', 'N']
                B1_channel = list(zip(B1_channel, channel_code))    
                for channel in B1_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.B1_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band B1/1575.42-Mhz (BDS-3 Signals): ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in B2a_channel:
                channel_code = ['D', 'P', 'X']
                B2a_channel = list(zip(B2a_channel, channel_code))    
                for channel in B2a_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.B2a_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band B2a/1176.45-Mhz (BDS-3 Signals): ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in B2b_channel:
                channel_code = ['I', 'Q', 'X', 'D', 'P', 'Z']
                B2b_channel = list(zip(B2b_channel, channel_code))    
                for channel in B2b_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.B2b_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                if passed_code in ['D', 'P', 'Z']:
                    print('Band B2b/1207.140-Mhz (BDS-3 Signals): ' + str(code_output))
                else:
                    print('Band B2b/1207.140-Mhz (BDS-2 Signals): ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in B2_channel:
                channel_code = ['D', 'P', 'X']
                B2_channel = list(zip(B2_channel, channel_code))    
                for channel in B2_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.B2_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band B2(B2a+B2b)/1191.795-Mhz (BDS-3 Signals): ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in B3_channel:
                channel_code = ['I', 'Q', 'X', 'A']
                B3_channel = list(zip(B3_channel, channel_code))    
                for channel in B3_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.B3_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band B3/1268.52-Mhz: ' + str(code_output))
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
            for obs_code in (cls.B12_code + cls.B1_code + cls.B2a_code + cls.B2b_code + cls.B2_code + cls.B3_code):
                if obs_code[0] == phase_measurement:
                    code_output.append(obs_code)    
            print(code_output)    
        if passed_code.upper() in (cls.B12_code + cls.B1_code + cls.B2a_code + cls.B2b_code + cls.B2_code + cls.B3_code):
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
            if passed_code in cls.B12_code:
                band_freq = 'Band B1-2/1561.098-Mhz'
                if passed_code[2] == 'I':
                    channel_code = cls.B12_channel[0]
                elif passed_code[2] == 'Q':
                    channel_code = cls.B12_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.B12_channel[2]
            if passed_code in cls.B1_code:
                band_freq = 'Band B1/1575.42-Mhz'
                if passed_code[2] == 'D':
                    channel_code = cls.B1_channel[0]
                elif passed_code[2] == 'P':
                    channel_code = cls.B1_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.B1_channel[2]
                elif passed_code[2] == 'A':
                    channel_code = cls.B1_channel[3]
                elif passed_code[2] == 'N':
                    channel_code = cls.B1_channel[4]
            if passed_code in cls.B2a_code:
                band_freq = 'Band B2a/1176.45-Mhz (BDS-3 Signals)'
                if passed_code[2] == 'D':
                    channel_code = cls.B2a_channel[0]
                elif passed_code[2] == 'P':
                    channel_code = cls.B2a_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.B2a_channel[2]
            if passed_code in cls.B2b_code:
                band_freq = 'Band B2b/1207.140-Mhz (BDS-2 Signals)'
                if passed_code[2] == 'I':
                    channel_code = cls.B2b_channel[0]
                elif passed_code[2] == 'Q':
                    channel_code = cls.B2b_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.B2b_channel[2]
                else:
                    band_freq = 'Band B2b/1207.140-Mhz (BDS-3 Signals)'
                    if passed_code[2] == 'D':
                        channel_code = cls.B2b_channel[3]
                    if passed_code[2] == 'P':
                        channel_code = cls.B2b_channel[4]
                    if passed_code[2] == 'Z':
                        channel_code = cls.B2b_channel[5]
            if passed_code in cls.B2_code:
                band_freq = 'Band B2(B2a+B2b)/1191.795-Mhz (BDS-3 Signals): '
                if passed_code[2] == 'D':
                    channel_code = cls.B2_channel[0]
                elif passed_code[2] == 'P':
                    channel_code = cls.B2_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.B2_channel[2]
            if passed_code in cls.B3_code:
                band_freq = 'Band B3/1268.52-Mhz'
                if passed_code[2] == 'I':
                    channel_code = cls.B2_channel[0]
                elif passed_code[2] == 'Q':
                    channel_code = cls.B2_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.B2_channel[2]
                elif passed_code[2] == 'A':
                    channel_code = cls.B2_channel[2]
                    
            if phase_measurement is not None:
                print (passed_code + ': ' + channel_code + ' channel-code derived ' + band_freq + ' ' + phase_measurement)  
        if arg_validation == None:
            print('Given code is not valid.')