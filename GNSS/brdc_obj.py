class BRDC:
    def __init__(self, inpath, logger = None):
        """
        This class reads the Broadcast Ephemeris file and stores the data
        RNX version 3.04
        
        inpath: Path object of the Broadcast Ephemeris file
        logger: SimpleLogger object for logging
        """

    def read(self):
        """
        Read the Broadcast Ephemeris file and store the data in self
        """
        from Readers import ReadBRDC

        data = ReadBRDC(self.inpath).read()

        self.g_data, self.r_data, self.c_data, self.e_data, self.header = data

    def g_ke

    def _g_columns(self):

        columns = [
            'epoch_observation',
            'system',
            'prn',
            'sv clock bias',  # Satellite clock bias
            'sv clock drift',  # Satellite clock drift
            'sv clock drift rate',  # Satellite clock drift rate
            'IODE',  # Issue of Data, Ephemeris
            'Crs',  # Amplitude of the Sine Harmonic Correction Term to the Orbit Radius
            'Delta n',  # Mean Motion Difference from Computed Value
            'M0',  # Mean Anomaly at Reference Time
            'Cuc',  # Amplitude of the Cosine Harmonic Correction Term to the Argument of Latitude
            'eccentricity',  # Eccentricity
            'Cus',  # Amplitude of the Sine Harmonic Correction Term to the Argument of Latitude
            'sqrtA',  # Square Root of the Semi-Major Axis
            'Toe',  # Reference Time Ephemeris (seconds into GPS week)
            'Cic',  # Amplitude of the Cosine Harmonic Correction Term to the Angle of Inclination
            'omega0',  # Longitude of Ascending Node of Orbit Plane at Weekly Epoch
            'Cis',  # Amplitude of the Sine Harmonic Correction Term to the Angle of Inclination
            'i0',  # Inclination Angle at Reference Time
            'Crc',  # Amplitude of the Cosine Harmonic Correction Term to the Orbit Radius
            'omega',  # Argument of Perigee
            'omega dot',  # Rate of Change of Right Ascension
            'IDOT',  # Rate of Change of Inclination Angle
            'codes on L2',  # Codes on L2 Channel
            'gps week',  # GPS Week Number
            'L2 P data flag',  # L2 P Data Flag
            'sv accuracy',  # Satellite User Range Accuracy
            'sv health',  # Satellite Health
            'TGD',  # Group Delay Differential
            'IODC',  # Issue of Data, Clock
            'transmission time',  # Transmission Time of Message
            'fit interval',  # Fit Interval in Hours
            'ref time',  # Reference Time
        ]
