# -*- coding: utf-8 -*-
"""
GPS Constant
Created on Wed Jun 24 2020
@author: Dr Hui Zhi
"""

class GPS():
    fo      = 10.23E+06           # Atomic Clock Frequency (Hz) - 10.23    MHZ
    L1      = 1575.42E+06         # GPS L1 Frequency       (Hz) - 154 * fo Hz
    L2      = 1227.60E+06         # GPS L2 Frequency       (Hz) - 120 * fo Hz
    L5      = 1176.45E+06         # GPS L5 Frequency       (Hz) - 115 * fo Hz
    MaxNoSV = 32
    
    Pi      = 3.1415926535898
    a       = 6378137.0           # Semi-major axis (m)
    b       = 6356752.3142        # Semi-minor axis (m)
    Invf    = 298.257223563       # Inverse flattening
    e       = 8.1819190842622E-2  # First eccentriciy
    esq     = 6.69437999014E-3    # First eccentriciy squared
    se      = 8.2094437949696E-2  # Second eccentriciy
    sesq    = 6.73949674228E-3    # Second eccentriciy squared
    GM      = 3.986005E+14        # Gravitational constant m3/s3
    c       = 2.99792458E+08      # Speed of light m/s
    F       = -4.442807633E-10    # sec/(meter)**(1/2)
    
    miu     = 3.986005E+14        # WGS-84 value of the Earth's universal gravitational parameter
    rad     = 7.2921151467E-5     # WGS-84 value of the Earth's rotation rate (EarthRate)
                                  # Angular velocity rad/sec
    ephInterval = 7200            # 2hours / in seconds
    ephDelay = 0                  # starts from the beginning of the day
    ephFlag = 1                   # 1 - sent at time epoch
    
    
    SV = ['G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08', 'G09', 'G10',
          'G11', 'G12', 'G13', 'G14', 'G15', 'G16', 'G17', 'G18', 'G19', 'G20',
          'G21', 'G22', 'G23', 'G24', 'G25', 'G26', 'G27', 'G28', 'G29', 'G30',
          'G31', 'G32']
    
    L1_code = ['C1C', 'L1C', 'D1C', 'S1C',
               'C1S', 'L1S', 'D1S', 'S1S',
               'C1L', 'L1L', 'D1L', 'S1L',
               'C1X', 'L1X', 'D1X', 'S1X',
               'C1P', 'L1P', 'D1P', 'S1P',
               'C1W', 'L1W', 'D1W', 'S1W',
               'C1Y', 'L1Y', 'D1Y', 'S1Y',
               'C1M', 'L1M', 'D1M', 'S1M',
               'L1N', 'D1N', 'S1N']
    
    L2_code = ['C2C', 'L2C', 'D2C', 'S2C',
               'C2D', 'L2D', 'D2D', 'S2D',
               'C2S', 'L2S', 'D2S', 'S2S',
               'C2L', 'L2L', 'D2L', 'S2L',
               'C2X', 'L2X', 'D2X', 'S2X',
               'C2P', 'L2P', 'D2P', 'S2P',
               'C2W', 'L2W', 'D2W', 'S2W',
               'C2Y', 'L2Y', 'D2Y', 'S2Y',
               'C2M', 'L2M', 'D2M', 'S2M',
               'L2N', 'D2N', 'S2N']
    
    L5_code = ['C5I', 'L5I', 'D5I', 'S5I',
               'C5Q', 'L5Q', 'D5Q', 'S5Q',
               'C5X', 'L5X', 'D5X', 'S5X']
    
    L1_channel = ['C/A', 'L1C (D)', 'L1C (P)', 'L1C (D+P)', 'P (AS off)', 
                'Z-tracking and similar (AS on)', 'Y', 'M', 'codeless']
    L2_channel = ['C/A', 'L1(C/A)+(P2-P1) (semi-codless)', 'L2C (M)', 'L2C (L)', 'L2C (M+L)', 
                  'P (AS off)', 'Z-tracking and similar (AS on)', 'Y', 'M', 'codeless']
    L5_channel = ['I', 'Q', 'I+Q']
    
    IIF   = [ 1,  3,  6,  8,  9, 10, 24, 25, 26, 27, 30, 32]
    III   = [ 4, 11, 14, 18, 23]
    IIR   = [ 2, 13, 16, 19, 20, 21, 22]
    IIR_M = [ 5,  7, 12, 15, 17, 28, 29, 31]
    
    IIF_SV   = ['G01', 'G03', 'G06', 'G08', 'G09', 'G10', 'G24', 'G25', 'G26',
                'G27', 'G30', 'G32']
    III_SV   = ['G04', 'G11', 'G14', 'G18', 'G23']
    IIR_SV   = ['G02', 'G13', 'G16', 'G19', 'G20', 'G21', 'G22']
    IIR_M_SV = ['G05', 'G07', 'G12', 'G15', 'G17', 'G28', 'G29', 'G31']
    
    # III_RB  = [4, 14, 18, 23]
    # IIRM_RB = [5, 7, 12, 15, 17, 29, 31]
    # IIR_RB  = [2, 11, 13, 16, 19, 20, 21, 22, 28, 30]
    # IIF_CS  = [8, 24]
    # IIF_RB  = [1, 3, 6, 9, 10, 25, 26, 27, 32]
    
    # III_RB_SV  = ['G04', 'G14', 'G18', 'G23']
    # IIRM_RB_SV = ['G05', 'G07', 'G12', 'G15', 'G17', 'G29', 'G31']
    # IIR_RB_SV  = ['G02', 'G11', 'G13', 'G16', 'G19', 'G20', 'G21', 'G22',
    #               'G28', 'G30']
    # IIF_CS_SV  = ['G04', 'G04']
    # IIF_RB_SV  = ['G01', 'G03', 'G06', 'G09', 'G10', 'G25', 'G26', 'G27',
    #               'G32']
    
    SISRE_Wr   = 0.98
    SISRE_Wac2 = 1/49
    
    CLOCK_TYPE = ['RB','CS']   
    # ordered by launch date
    CLOCK_RB = ['G13', 'G20', 'G22', 'G16', 'G21', 'G19', 'G02', 'G17', 'G31', 'G12', 'G15', 'G29', 'G07', 'G05', 
                'G25', 'G01', 'G27', 'G30', 'G06', 'G09', 'G03', 'G26', 'G10', 'G32', 'G04', 'G18', 'G23', 'G14', 'G11'] 
    CLOCK_CS = ['G24', 'G08'] 
    
    @classmethod
    def clock (cls, passed_SV):
        if passed_SV not in cls.CLOCK_RB and passed_SV not in cls.CLOCK_CS:
            raise Exception('Passed sattelite/PRN does not exist')
        elif passed_SV in cls.CLOCK_CS:
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
        L1_channel = [channel.lower() for channel in cls.L1_channel]
        L2_channel = [channel.lower() for channel in cls.L2_channel]
        L5_channel = [channel.lower() for channel in cls.L5_channel]
        
        if passed_code.lower() in (L1_channel + L2_channel + L5_channel):
            arg_validation = True
            passed_code = passed_code.lower()
            passed_stored = passed_code
            if passed_code in L1_channel:
                channel_code = ['C', 'S', 'L', 'X', 'P', 'W', 'Y', 'M', 'N']
                L1_channel = list(zip(L1_channel, channel_code))    
                for channel in L1_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.L1_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band L1/1575.42-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in L2_channel:
                channel_code = ['C', 'D', 'S', 'L', 'X', 'P', 'W', 'Y', 'M', 'N']
                L2_channel = list(zip(L2_channel, channel_code))    
                for channel in L2_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.L2_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band L2/1227.60-Mhz: ' + str(code_output))
                code_output = []
                passed_code = passed_stored
            if passed_code in L5_channel:
                channel_code = ['I', 'Q', 'X']
                L5_channel = list(zip(L5_channel, channel_code))    
                for channel in L5_channel:
                    if passed_code == channel[0]:
                        passed_code = channel[1]
                        break
                for obs_code in cls.L5_code:
                    if passed_code == obs_code[2]:
                        code_output.append(obs_code)
                print('Band L5/1176.45-Mhz: ' + str(code_output))
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
            for obs_code in (cls.L1_code + cls.L2_code + cls.L5_code):
                if obs_code[0] == phase_measurement:
                    code_output.append(obs_code)    
            print(code_output)    
        if passed_code.upper() in (cls.L1_code + cls.L2_code + cls.L5_code):
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
            if passed_code in cls.L1_code:
                band_freq = 'L1/1575.42-MHz'
                if passed_code[2] == 'C':
                    channel_code = cls.L1_channel[0]
                elif passed_code[2] == 'S':
                    channel_code = cls.L1_channel[1]
                elif passed_code[2] == 'L':
                    channel_code = cls.L1_channel[2]
                elif passed_code[2] == 'X':
                    channel_code = cls.L1_channel[3]
                elif passed_code[2] == 'P':
                    channel_code = cls.L1_channel[4]        
                elif passed_code[2] == 'W':
                    channel_code = cls.L1_channel[5]
                elif passed_code[2] == 'Y':
                    channel_code = cls.L1_channel[6]
                elif passed_code[2] == 'M':
                    channel_code = cls.L1_channel[7]
                elif passed_code[2] == 'N':
                    channel_code = cls.L1_channel[8]
                    if passed_code[0] == 'C':
                        phase_measurement = ''
            if passed_code in cls.L2_code:
                band_freq = 'L2/1227.60-MHz'
                if passed_code[2] == 'C':
                    channel_code = cls.L2_channel[0]
                elif passed_code[2] == 'D':
                    channel_code = cls.L2_channel[1]
                elif passed_code[2] == 'S':
                    channel_code = cls.L2_channel[2]
                elif passed_code[2] == 'L':
                    channel_code = cls.L2_channel[3]
                elif passed_code[2] == 'X':
                    channel_code = cls.L2_channel[4]        
                elif passed_code[2] == 'P':
                    channel_code = cls.L2_channel[5]
                elif passed_code[2] == 'W':
                    channel_code = cls.L2_channel[6]
                elif passed_code[2] == 'Y':
                    channel_code = cls.L2_channel[7]
                elif passed_code[2] == 'M':
                    channel_code = cls.L2_channel[8]
                elif passed_code[2] == 'N':
                    channel_code = cls.L2_channel[9]
                    if passed_code[0] == 'C':
                        phase_measurement = ''
            if passed_code in cls.L5_code:
                band_freq = 'L5/1176.45-MHz'
                if passed_code[2] == 'I':
                    channel_code = cls.L5_channel[0]
                elif passed_code[2] == 'Q':
                    channel_code = cls.L5_channel[1]
                elif passed_code[2] == 'X':
                    channel_code = cls.L5_channel[2]
            if phase_measurement is not None:
                print (passed_code + ': ' + channel_code + ' channel-code derived ' + band_freq + ' ' + phase_measurement)  
        if arg_validation == None:
            print('Given code is not valid.')
