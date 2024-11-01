from chc_modules import FindSvBrdc, FindSV
from Coord import LLA, ECEF
from datetime import datetime
import pandas as pd
import numpy as np

class CalculateHorizonCrossings:
    def __init__(self, process_date, ground_pos_lla, local_work_dir, elevation_mask=15, logger=None):
        """
        Calculate the epochs at which a satellite comes above and below the horizon.
        
        args:
            process_date: datetime
                Date to calculate the horizon crossings for.
            ground_pos_lla: LLA
                LLA object containing the ground position of the station.
            local_work_dir: Path
                Path to the local working directory. Used to store downloaded brdc files
            elevation_mask: int
                Elevation mask in degrees.
            logger: SimpleLogger
                Logger object to write logs to.
        """
        if not isinstance(process_date, datetime):
            raise TypeError("process_date must be a datetime object")
        self.process_date = process_date
        self.ground_pos_lla = LLA(ground_pos_lla, 'R')
        self.elevation_mask = int(elevation_mask)
        self.local_work_dir = local_work_dir
        self.logger = logger

    def run(self):
        # download brdc GPS
        try:  # sp3
            find_sv_sp3_GCE = FindSV(self.process_date, ['G', 'C', 'E'], self.local_work_dir, interval=30, logger=self.logger)
            sv_pos_arr_GCE = find_sv_sp3_GCE.run()
        except:
            find_sv_brdc_GCE = FindSvBrdc(self.process_date, ['G', 'C', 'E'], self.local_work_dir, save_file_flag=False, interval=30, logger=self.logger)
            sv_pos_arr_GCE = find_sv_brdc_GCE.run()
        
        # calculate azel
        sat_pos_ecef = ECEF(sv_pos_arr_GCE[:, 3:6])
        ground_pos_lla = self.ground_pos_lla
        
        azel = ground_pos_lla.calculate_azel(sat_pos_ecef)
        
        full_combined_arr = np.hstack((sv_pos_arr_GCE, azel))
        
        sat_pos_df = pd.DataFrame(full_combined_arr, columns=['epoch', 'sys', 'prn', 'x', 'y', 'z', 'az', 'el'])
        
        return self._process_sat_pos_df(sat_pos_df)
    
    def run_with_sat_pos_df(self, sat_pos_df):
        """
        Process the provided satellite position DataFrame directly.

        args:
            sat_pos_df: pd.DataFrame
                DataFrame containing satellite positions and calculated azimuth/elevation.

        returns:
            el_crossing_df: pd.DataFrame
                DataFrame containing the entering and leaving epochs for each satellite.
        """
        return self._process_sat_pos_df(sat_pos_df)
    
    def _process_sat_pos_df(self, sat_pos_df):
        """
        Internal method to process the satellite position DataFrame and find elevation crossings.

        args:
            sat_pos_df: pd.DataFrame
                DataFrame containing satellite positions and calculated azimuth/elevation.

        returns:
            el_crossing_df: pd.DataFrame
                DataFrame containing the entering and leaving epochs for each satellite.
        """
        el_crossing_df = sat_pos_df.groupby(['sys', 'prn']).apply(self.find_elevation_crossings).reset_index()
        el_crossing_df.columns = ['sys', 'prn', 'arc number', 'entering_epoch', 'leaving_epoch']
        el_crossing_df['entering_epoch'] = pd.to_datetime(el_crossing_df['entering_epoch'], unit='s')
        el_crossing_df['leaving_epoch'] = pd.to_datetime(el_crossing_df['leaving_epoch'], unit='s')
        return el_crossing_df

    def find_elevation_crossings(self, group):
        # Identify where the elevation crosses the threshold
        above = group['el'] >= self.elevation_mask
        # Find transitions
        transition_points = above != above.shift()
        transition_points.iloc[0] = False  # Ignore the first point
        
        # Separate entering and leaving points
        entering_sight = group.loc[transition_points & above, 'epoch']
        leaving_sight = group.loc[transition_points & ~above, 'epoch']
        
        # If the group starts above the threshold, there's no entering point at the start
        if above.iloc[0]:
            entering_sight = pd.concat([pd.Series([group['epoch'].iloc[0]]), entering_sight])

        # If the group ends above the threshold, there's no leaving point at the end
        if above.iloc[-1]:
            leaving_sight = pd.concat([leaving_sight, pd.Series([group['epoch'].iloc[-1]])])

        # Return as DataFrame
        return pd.DataFrame({
            'entering_epoch': entering_sight.reset_index(drop=True),
            'leaving_epoch': leaving_sight.reset_index(drop=True)
        })
     
if __name__ == '__main__':
    from pathlib import Path
    process_date = datetime(
        2021, 1, 1
        )
    ground_pos_lla = LLA(
        [35,100,0], 'D'
        )
    local_work_dir = Path(
        r"F:/test"
        )
    chc = CalculateHorizonCrossings(
        process_date, ground_pos_lla, local_work_dir
        )
    el_crossing_df = chc.run()
    print(el_crossing_df)
    