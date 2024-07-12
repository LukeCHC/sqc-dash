from pathlib import Path
import pandas as pd

class ReadQILogFile:
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.df = None

    def read(self):
        data = []
        epoch = None

        with open(self.input_file_path, 'r') as file:
            for line in file:
                line = line.strip()

                if line.startswith('Epoch:'):
                    epoch = line[7:]
                elif line.startswith('sat'):
                    values = line.split()
                    prn = values[1]
                    zoneid = values[2]
                    qi1_regtrop = values[3]
                    qi1_regiono = values[4]
                    qi1_rtkf1 = values[5]
                    qi1_rtkf2 = values[6]

                    data.append([epoch, prn, zoneid, qi1_regtrop, qi1_regiono, qi1_rtkf1, qi1_rtkf2])

        df = pd.DataFrame(data, columns=['epoch', 'prn', 'zoneid', 'qi1_regtrop', 'qi1_regiono', 'qi1_rtkf1', 'qi1_rtkf2'])

        df['epoch'] = pd.to_datetime(df['epoch'])
        df[['qi1_regtrop', 'qi1_regiono', 'qi1_rtkf1', 'qi1_rtkf2']] = df[['qi1_regtrop', 'qi1_regiono', 'qi1_rtkf1', 'qi1_rtkf2']].astype(float)

        return df
    
if __name__ == '__main__':
    input_file_path = Path(r"\\meetingroom\Integrity\SWASQC\playback\Intg_regqi_2024067.log")
    reader = ReadQILogFile(input_file_path)
    df = reader.read()
    print(df.head())