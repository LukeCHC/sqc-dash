# -*- coding: utf-8 -*-
"""
GLONASS Constant
Created on Tue Jul 14 2020
@author: DR Hui Zhi
"""

class GLO():   
    # https://www.glonass-iac.ru/en/GLONASS/
    RF_chnl = [ 1, -4,  5,  6,  1, -4,  5,  6, 
               -2, -7,  0, -1, -2, -7,  0,  1,
                4, -3,  3,  2,  4, -3,  3,  2]
    
    
    G1  = [(1602 + k*9/16)*1E+6 for k in RF_chnl] # GLONASS G1  Frequency (Hz)
    G1a = [1600.995E+06 for i in range(24)]        # GLONASS G1a Frequency (Hz)
    G2  = [(1246 + k*7/16)*1E+6 for k in RF_chnl] # GLONASS G2  Frequency (Hz)
    G2a = [1248.06E+06 for i in range(24)]         # GLONASS G2a Frequency (Hz)
    G3  = [1202.025E+06 for i in range(24)]        # GLONASS G3  Frequency (Hz)
    MaxNoSV = 24
    
    ephInterval = 1800               # 30minutes / in seconds
    ephDelay = 900                   # starts from 15min of the day
    ephFlag = 1                      # 1 - sent at time epoch
    
    SV = ['R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R09', 'R10',
          'R11', 'R12', 'R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20',
          'R21', 'R22', 'R23', 'R24']
    
    G1_code  = ['C1C', 'L1C', 'D1C', 'S1C',
                'C1P', 'L1P', 'D1P', 'S1P']
    
    G1a_code = ['C4A', 'L4A', 'D4A', 'S4A',
                'C4B', 'L4B', 'D4B', 'S4B',
                'C4X', 'L4X', 'D4X', 'S4X']
    
    G2_code  = ['C2C', 'L2C', 'D2C', 'S2C',
                'C2P', 'L2P', 'D2P', 'S2P']
    
    G2a_code = ['C6A', 'L6A', 'D6A', 'S6A',
                'C6B', 'L6B', 'D6B', 'S6B',
                'C6X', 'L6X', 'D6X', 'S6X']
    
    G3_code  = ['C3I', 'L3I', 'D3I', 'S3I',
                'C3Q', 'L3Q', 'D3Q', 'S3Q',
                'C3X', 'L3X', 'D3X', 'S3X']
    
    G1_channel  = ['C/A', 'P']
    G1a_channel = ['L1OCd', 'L1OCp', 'L1OCd+L1OCp']
    G2_channel  = ['C/A (GLONASS M)', 'P']
    G2a_channel = ['L2CSI', 'L2OCp', 'L2CSI+L2OCp']
    G3_channel  = ['I', 'Q', 'I+Q'] 
    
    SISRE_Wr   = 0.98
    SISRE_Wac2 = 1/45
    
    CLOCK_TYPE = ['CS'] # 'Caesium'
    # ordered by launch date
    CLOCK_CS = ['719', '720', '721', '723', '730', '733', '732', '735', '736', '743', '744', 
                 '745', '747', '754', '755', '702', '751', '753', '752', '756', '757', '758'] 
    CLOCK_NOT_DEFINED = ['759', '760', '705'] 
    
    @classmethod
    def clock (cls, passed_SV):
        if passed_SV not in cls.SV and passed_SV not in cls.CLOCK_CS and passed_SV not in cls.CLOCK_NOT_DEFINED:
            raise Exception('Passed satellite/PRN does not exist')
        elif passed_SV in cls.CLOCK_CS:
            return cls.CLOCK_TYPE[0]
        else: 
            return 'Clock type is not defined'
        
    @classmethod
    def obs_code (cls, passed_code):
        phase_measurement = None
        channel_code = None
        band_freq = None
        arg_validation = None
        code_output = []
        G1_channel  = [channel.lower() for channel in cls.G1_channel]
        G1a_channel = [channel.lower() for channel in cls.G1a_channel]
        G2_channel  = [channel.lower() for channel in cls.G2_channel]
        G2a_channel = [channel.lower() for channel in cls.G2a_channel]
        G3_channel  = [channel.lower() for channel in cls.G3_channel]
        
        if passed_code.lower() in (G1_channel + G1a_channel + G2_channel + G2a_channel + G3_channel):
            arg_validation = True
            passed_code = passed_code.lower()
            passed_stored = passed_code
            if passed_code in G1_channel:
                channel_code = ['C', 'P']
                G1_channel = list(zip(G1_channel, channel_code))    
                for channel in G1_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.G1_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band G1/1602-Mhz + k*9/16 k= -7….+12: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in G1a_channel:
                channel_code = ['A', 'B', 'X']
                G1a_channel = list(zip(G1a_channel, channel_code))    
                for channel in G1a_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.G1a_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band G1a/1600.995-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in G2_channel:
                channel_code = ['C', 'P']
                G2_channel = list(zip(G2_channel, channel_code))    
                for channel in G2_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.G2_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band G2/1246-Mhz +k*7/16: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in G2a_channel:
                channel_code = ['A', 'B', 'X']
                G2a_channel = list(zip(G2a_channel, channel_code))    
                for channel in G2a_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.G2a_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band G2a/1248.06-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in G3_channel:
                channel_code = ['I', 'Q', 'X']
                G3_channel = list(zip(G3_channel, channel_code))    
                for channel in G3_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.G3_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band G3/1202.025-Mhz: ' + str(code_output))
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
            for obs_code in (cls.G1_code + cls.G1a_code + cls.G2_code + cls.G2a_code + cls.G3_code):
                if obs_code[0] == phase_measurement:
                    code_output.append(obs_code)    
            print(code_output)    
        if passed_code.upper() in (cls.G1_code + cls.G1a_code + cls.G2_code + cls.G2a_code + cls.G3_code):
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
            if passed_code in cls.G1_code:
                band_freq = 'Band G1/1602-Mhz + k*9/16 k= -7….+12'
                if passed_code[2] == 'C':
                    channel_code = cls.G1_channel[0]
                elif passed_code[2] == 'P':
                    channel_code = cls.G1_channel[1]
            if passed_code in cls.G1a_code:
                band_freq = 'Band G1a/1600.995-Mhz'
                if passed_code[2] == 'A':
                    channel_code = cls.G1a_channel[0]
                elif passed_code[2] == 'B':
                    channel_code = cls.G1a_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.G1a_channel[2]
            if passed_code in cls.G2_code:
                band_freq = 'Band G2/1246-Mhz +k*7/16'
                if passed_code[2] == 'C':
                    channel_code = cls.G2_channel[0]
                elif passed_code[2] == 'P':
                    channel_code = cls.G2_channel[1]
            if passed_code in cls.G2a_code:
                band_freq = 'Band G2a/1248.06-Mhz'
                if passed_code[2] == 'A':
                    channel_code = cls.G2a_channel[0]
                elif passed_code[2] == 'B':
                    channel_code = cls.G2a_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.G2a_channel[2]
            if passed_code in cls.G3_code:
                band_freq = 'Band G3/1202.025-Mhz'
                if passed_code[2] == 'I':
                    channel_code = cls.G3_channel[0]
                elif passed_code[2] == 'Q':
                    channel_code = cls.G3_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.G3_channel[2]
            if phase_measurement is not None:
                print (passed_code + ': ' + channel_code + ' channel-code derived ' + band_freq + ' ' + phase_measurement)  
        if arg_validation == None:
            print('Given code is not valid.')