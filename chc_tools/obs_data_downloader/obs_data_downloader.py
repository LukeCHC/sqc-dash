import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from sklearn.cluster import KMeans
from pathlib import Path

from FTP import FTPWorkflowManager, FTPConnectionManager, FTPDownloader
from chc_tools.decompress import decompress_gzip
from chc_tools.hatanaka import crx2rnx


class SimpleDataDownloader:
    def __init__(self, year_to_download: int, days_to_download: list, station_list: list, output_dir: str):
        self.year_to_download = year_to_download
        self.days_to_download = days_to_download  # list of day of years 0-366
        self.station_list = station_list
        self.output_dir = Path(output_dir)

    def run(self):
        station_list = self.station_list

        # Step 2: Download the observation data for the sampled stations
        self.download_obs_data(station_list)

        # Step 3: Decompress downloaded files
        self.decompress_files()
        
    def download_obs_data(self, station_list: list):
        year = self.year_to_download
        IP = "141.74.17.25"  # "gdc.cddis.eosdis.nasa.gov"

        for station in station_list:
            for day in self.days_to_download:
                # Download data for each station and day
                remote_path = f"/IGS/obs/{year}/{day:03d}"
                local_folder_save_path = self.output_dir / f"{day:03d}"
                local_folder_save_path.mkdir(parents=True, exist_ok=True)

                conn = FTPConnectionManager()
                if conn.connect(IP, 21):
                    if conn.authenticate("anonymous", ""):  # (USER, PASSWORD)
                        filenames = conn.list_files(remote_path)
                        # Search for the file with the station code in its name
                        matched_files = [filename for filename in filenames if station in filename]
                        matched_files = [filename for filename in matched_files if '_MO.' in filename]  # obs files only
                        for file_to_download in matched_files:
                            remote_file_path = f"{remote_path}/{file_to_download}"
                            local_file_path = local_folder_save_path / file_to_download

                            # Download the file
                            if conn.download_file(remote_file_path, local_file_path):
                                print(f"File {file_to_download} downloaded successfully")
                            else:
                                print(f"Failed to download file {file_to_download}")
                                
                    conn.disconnect()
                    
    def decompress_files(self):
        for file in self.output_dir.glob("*.gz"):
            decompress_gzip(file)  # returns path or error

        for file in self.output_dir.glob("*.crx"):
            new_file = file.rename(file.with_suffix(f'.{str(self.year_to_download)[2:]}d'))
            crx2rnx(new_file)  # returns bool based on success

        return True
        
class ObsDataDownloader:
    def __init__(self, year_to_download: int, days_to_download: list, station_list_file_path: str, output_dir: str):
        self.year_to_download = year_to_download
        self.days_to_download = days_to_download  # list of day of years 0-366
        self.station_list_file_path = station_list_file_path
        self.output_dir = Path(output_dir)
        self.regions = {
            'South America': {'lat_range': (-60, 15), 'lon_range': (-90, -30)},
            'North America': {'lat_range': (15, 85), 'lon_range': (-170, -30)},
            'Europe': {'lat_range': (35, 70), 'lon_range': (-10, 40)},
            'North East Asia': {'lat_range': (30, 85), 'lon_range': (40, 180)},
            'South East Asia and Oceania': {'lat_range': (-60, 30), 'lon_range': (60, 180)},
            'Africa': {'lat_range': (-40, 40), 'lon_range': (-20, 55)}
        }

    def run(self):
        # Step 1: Read station list
        stn_df = self.read_station_list()

        # Step 2: Retrieve file list from FTP server
        file_list = self.get_file_list_from_ftp()

        # Step 3: Check which stations are in the file list
        common_stations = self.get_common_stations(stn_df, file_list)
        if not common_stations:
            print("No common stations found in the file list.")
            return

        # Step 4: Perform stratified sampling to ensure each sampled file is available
        sampled_df = self.stratified_sampling(stn_df, common_stations)
        if sampled_df.empty:
            print("No samples could be obtained from the available stations.")
            return
        
        # Step 5: Extract site names from sampled DataFrame
        station_list = self.extract_site_names(sampled_df)

        # Step 6: Download the observation data for the sampled stations
        self.download_obs_data(sampled_df)

        # Step 7: Decompress downloaded files
        self.decompress_files()
        
        # step 8 : plot the stations on the map
        self.plot_stations_on_map(stn_df, sampled_df)
        
        # final step
        self.save_station_list(sampled_df)

    def save_station_list(self, sampled_df: pd.DataFrame):
        with open(self.output_dir / '_station_list.txt', 'w') as f:
            for index, row in sampled_df.iterrows():
                f.write(f"{row['Site Name']} - {row['Region']}\n")
        print("Station list saved successfully.")

    def get_file_list_from_ftp(self):
        year = self.year_to_download
        IP = "141.74.17.25"  # "gdc.cddis.eosdis.nasa.gov"

        for day in self.days_to_download:
            remote_path = f"/IGS/obs/{year}/{day:03d}"
            conn = FTPConnectionManager()
            if conn.connect(IP, 21):
                if conn.authenticate("Anonymous"," "):  # (USER, PASSWORD)
                    filenames = conn.list_files(remote_path)
                conn.disconnect()
            break
        
        # remove all navigation files
        filenames = [filename for filename in filenames if '_MN.' not in filename]
        
        return filenames

    def get_common_stations(self, stn_df: pd.DataFrame, file_list: list) -> list:
        station_codes = self.extract_station_codes(file_list)
        common_stations = [code for code in stn_df['Site Name'].tolist() if code in station_codes]
        return common_stations

    def extract_station_codes(self, filenames: list) -> set:
        """
        Extract the station codes from the filenames.
        
        Args:
            filenames (list): List of filenames.
        
        Returns:
            set: Set of station codes.
        """
        station_codes = {filename.split('_')[0] for filename in filenames}
        return station_codes

    def download_obs_data(self, sampled_df: pd.DataFrame):
        year = self.year_to_download
        IP = "141.74.17.25"  # "gdc.cddis.eosdis.nasa.gov"

        for index, row in sampled_df.iterrows():
            station = row['Site Name']
            region = row['Region']
            for day in self.days_to_download:
                # Download data for each station and day
                remote_path = f"/IGS/obs/{year}/{day:03d}"
                local_folder_save_path = self.output_dir / region / f"{day:03d}"
                local_folder_save_path.mkdir(parents=True, exist_ok=True)

                conn = FTPConnectionManager()
                if conn.connect(IP, 21):
                    if conn.authenticate("anonymous", ""):  # (USER, PASSWORD)
                        filenames = conn.list_files(remote_path)
                        # Search for the file with the station code in its name
                        matched_files = [filename for filename in filenames if station in filename]
                        matched_files = [filename for filename in matched_files if '_MO.' in filename]  # obs files only
                        for file_to_download in matched_files:
                            remote_file_path = f"{remote_path}/{file_to_download}"
                            local_file_path = local_folder_save_path / file_to_download

                            # Download the file
                            if conn.download_file(remote_file_path, local_file_path):
                                print(f"File {file_to_download} downloaded successfully")
                            else:
                                print(f"Failed to download file {file_to_download}")
                                
                    conn.disconnect()

    def decompress_files(self):
        for file in self.output_dir.glob("*.gz"):
            decompress_gzip(file)  # returns path or error

        for file in self.output_dir.glob("*.crx"):
            new_file = file.rename(file.with_suffix(f'.{str(self.year_to_download)[2:]}d'))
            crx2rnx(new_file)  # returns bool based on success

        return True

    def read_station_list(self) -> pd.DataFrame:
        return pd.read_csv(self.station_list_file_path)

    def extract_site_names(self, stn_df: pd.DataFrame) -> list:
        """
        Extracts the first 4 characters from all the site names.

        Parameters:
        stn_df (pd.DataFrame): DataFrame containing 'Site Name'.

        Returns:
        list: List of the first 4 characters of each site name.
        """
        return stn_df['Site Name'].tolist()

    def stratified_sampling(self, stn_df: pd.DataFrame, common_stations: list) -> pd.DataFrame:
        """
        Performs stratified sampling on the station DataFrame to return 10-20 stations 
        from each specified region.

        Parameters:
        stn_df (pd.DataFrame): DataFrame containing 'Site Name', 'Latitude', 'Longitude'.
        common_stations (list): List of stations that are available in the file list.

        Returns:
        pd.DataFrame: Sampled DataFrame with 10-20 stations from each region.
        """
        available_stations_df = stn_df[stn_df['Site Name'].isin(common_stations)]
        
        if available_stations_df.empty:
            return pd.DataFrame()

        sampled_df = pd.DataFrame()
        
        for region, bounds in self.regions.items():
            region_stations = available_stations_df[
                (available_stations_df['Latitude'] >= bounds['lat_range'][0]) & 
                (available_stations_df['Latitude'] <= bounds['lat_range'][1]) &
                (available_stations_df['Longitude'] >= bounds['lon_range'][0]) & 
                (available_stations_df['Longitude'] <= bounds['lon_range'][1])
            ]
            
            if not region_stations.empty:
                n_samples = min(20, len(region_stations))
                sampled_region_stations = region_stations.sample(n=n_samples, random_state=42)
                sampled_region_stations['Region'] = region  # Add region column
                sampled_df = pd.concat([sampled_df, sampled_region_stations])
        
        return sampled_df.reset_index(drop=True)

    def stratified_sampling_(self, stn_df: pd.DataFrame, common_stations: list) -> pd.DataFrame:
        """
        Performs stratified sampling on the station DataFrame to return 100 stations 
        that are well evenly distributed based on their geographical coordinates.

        Parameters:
        stn_df (pd.DataFrame): DataFrame containing 'Site Name', 'Latitude', 'Longitude'.
        common_stations (list): List of stations that are available in the file list.

        Returns:
        pd.DataFrame: Sampled DataFrame with 100 evenly distributed stations.
        """
        available_stations_df = stn_df[stn_df['Site Name'].isin(common_stations)]
        
        if available_stations_df.empty:
            return pd.DataFrame()

        n_clusters = min(100, len(available_stations_df))  # Number of clusters should not exceed the number of available stations

        # Extract latitude and longitude for clustering
        coordinates = available_stations_df[['Latitude', 'Longitude']].values

        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        available_stations_df['cluster'] = kmeans.fit_predict(coordinates)

        # Sample one station from each cluster
        sampled_df = available_stations_df.groupby('cluster', group_keys=False).apply(lambda x: x.sample(1)).reset_index(drop=True)

        # Drop the cluster column
        return sampled_df.drop(columns=['cluster'])

    def plot_stations_on_map(self, stn_df: pd.DataFrame, sampled_df: pd.DataFrame):
        """
        Plots the original and sampled stations on a map to visualize distribution.

        Parameters:
        stn_df (pd.DataFrame): Original DataFrame containing all stations.
        sampled_df (pd.DataFrame): DataFrame containing sampled stations.
        """
        stn_gdf = gpd.GeoDataFrame(
            stn_df, geometry=gpd.points_from_xy(stn_df.Longitude, stn_df.Latitude))
        sampled_gdf = gpd.GeoDataFrame(
            sampled_df, geometry=gpd.points_from_xy(sampled_df.Longitude, sampled_df.Latitude))

        stn_gdf.set_crs(epsg=4326, inplace=True)
        sampled_gdf.set_crs(epsg=4326, inplace=True)

        # Convert to Web Mercator (EPSG:3857)
        stn_gdf = stn_gdf.to_crs(epsg=3857)
        sampled_gdf = sampled_gdf.to_crs(epsg=3857)

        fig, ax = plt.subplots(figsize=(12, 8))
        stn_gdf.plot(ax=ax, color='blue', alpha=0.5, markersize=10, label='Original Stations')
        
        colors = {
            'South America': 'red', 
            'North America': 'green', 
            'Europe': 'orange', 
            'North East Asia': 'purple', 
            'South East Asia and Oceania': 'yellow', 
            'Africa': 'pink'
        }

        for region, color in colors.items():
            sampled_gdf[sampled_gdf['Region'] == region].plot(
                ax=ax, color=color, alpha=0.7, markersize=30, label=f'{region} Sampled Stations'
            )

        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Original and Sampled Station Distribution on Map')
        plt.legend()
        plt.savefig(self.output_dir / '_station_distribution.png')


if __name__ == "__main__":
    station_list_file_path = Path(r"\\meetingroom\Integrity\for_zoe\station_positions.csv")
    save_dir = Path(r"\\meetingroom\Integrity\for_zoe\sme_obs_data_11_6_24")
    year = 2024
    days = [131, 132, 155]

    station_list = [
        "ALRT", "ANMG", "ANTC", "AREG", "ARHT", "ARTU", "ASCG", "BOGT", "CAS1", "CGGN",
        "CHAN", "CHPI", "CHTI", "COTE", "COYQ", "CPVG", "CUT0", "CYNE", "CZTG", "DAV1",
        "DGAR", "DLTV", "DUMG", "DUND", "FALK", "FFMJ", "GAMB", "GLPS", "HNPT", "HNUS",
        "HOB2", "HOLB", "HYDE", "INEG", "ISBA", "ISPA", "KAT1", "KERG", "KOKB", "KRGG",
        "LAUT", "LHAZ", "MAC1", "MAG0", "MAJU", "MAL2", "MAW1", "MCIL", "MCM4", "MDO1",
        "MKEA", "MOBS", "MQZG", "MTKA", "MTV1", "NABG", "NYA1", "NYA2", "NYAL", "OHI2",
        "OHI3", "OUS2", "OWMG", "PALM", "PARC", "PETS", "PICL", "PIMO", "PNGM", "RABT",
        "RAEG", "RBAY", "RESO", "RGDG", "RIO2", "ROTH", "SANT", "SAVO", "SCTB", "SSIA",
        "STHL", "STJO", "STPM", "SYOG", "TEJA", "THTG", "THU2", "TIXI", "TOW2", "TUVA",
        "ULAB", "UTQI", "VACS", "VNDP", "WIND", "WUTH", "XJCC", "XMIS", "YIBL", "YKRO"
    ]
    
    # obs_data_downloader = SimpleDataDownloader(year, days, station_list, save_dir) # simple
    obs_data_downloader = ObsDataDownloader(year, days, station_list_file_path, save_dir) # advanced
    obs_data_downloader.run()
    
    
    
 
    
    
"""
Station list old

['SOD300FIN', 'NLIB00USA', 'COCO00AUS', 'FALK00FLK', 'USN800USA', 
'SUTM00ZAF', 'PARK00AUS', 'MSSA00JPN', 'GAMB00PYF', 'VILL00ESP', '
SALU00BRA', 'KITG00UZB', 'YELL00CAN', 'HLFX00CAN', 'NICO00CYP', 
'REUN00REU', 'KOKB00USA', 'WTZR00DEU', 'DAV100ATA', 'PBR400IND', 
'SOLO00SLB', 'DJIG00DJI', 'YKRO00CIV', 'UTQI00USA', 'MCM400ATA', 
'AREG00PER', 'KARR00AUS', 'ENAO00PRT', 'TONG00TON', 'PTGG00PHL', 
'QUIN00USA', 'UFPR00BRA', 'BOGT00COL', 'IISC00IND', 'OP7100FRA', 
'CRO100VIR', 'REYK00ISL', 'THTG00PYF', 'GMSD00JPN', 'CZTG00ATF', 
'SANT00CHL', 'BADG00RUS', 'NRMD00NCL', 'NABG00NOR', 'CAS100ATA', 
'KAT100AUS', 'STPM00SPM', 'KRGG00ATF', 'LPAL00ESP', 'DUBO00CAN', 
'BREW00USA', 'TWTF00TWN', 'STHL00GBR', 'MAC100AUS', 'GUAM00GUM', 
'KZN200RUS', 'THU200GRL', 'PADO00ITA', 'JDPR00IND', 'SYOG00ATA', 
'VALD00CAN', 'NVSK00RUS', 'DGAR00GBR', 'ANMG00MYS', 'RIO200ARG',
'SEY200SYC', 'VIS000SWE', 'MATG00ITA', 'HARB00ZAF', 'BRAZ00BRA', 
'MAL200KEN', 'TOW200AUS', 'OWMG00NZL', 'NAUS00BRA', 'ZECK00RUS',
'WHIT00CAN', 'TUVA00TUV', 'CEDU00AUS', 'GLPS00ECU', 'ABPO00MDG',
'ZIM200CHE', 'OUS200NZL', 'SVTL00RUS', 'FAIR00USA', 'SCUB00CUB',
'QAQ100GRL', 'KOUG00GUF', 'SULP00UKR', 'MCIL00JPN', 'SASK00CAN',
'GODS00USA', 'AMC400USA', 'POHN00FSM', 'LPGS00ARG', 'PALM00ATA',
'MAW100ATA', 'URUM00CHN', 'MIKL00UKR', 'CHWK00CAN', 'CPVG00CPV']

"""