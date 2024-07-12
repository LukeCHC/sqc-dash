# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 10:25:59 2023

@author: chcuk
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

class StationSampler:
    def __init__(self, data_path, num_bins_lat=20, num_bins_lon=20):

        """
         Initializer for the StationSampler class.
         
         Functionality:
         --------------
         - Reads the JSON data file containing information about stations.
         - Initializes the number of latitude and longitude bins.
         - Creates latitude and longitude bins.
         - Adds 'lat_bin' and 'lon_bin' columns to the DataFrame to categorize each station into a geographic bin.
         - Initializes an empty DataFrame for sampled stations.
         
         Inputs:
         -------
         - data_path (str): The file path of the JSON data file containing the station information.
         - num_bins_lat (int, optional): The number of latitude bins. Default is 20.
         - num_bins_lon (int, optional): The number of longitude bins. Default is 20.
         
         Outputs:
         --------
         None. The method initializes attributes of the object.
         
         How it works:
         -------------
         1. Reads the JSON data into a pandas DataFrame.
         2. Stores the number of bins for latitude and longitude as class attributes.
         3. Calculates the edges of these bins using np.linspace and stores them as class attributes.
         4. Uses pandas' 'cut' function to categorize each station's latitude and longitude into these bins.
         5. Initializes an empty DataFrame for storing sampled stations in future operations.
         """
            
        self.df = pd.read_json(data_path)
        self.sample_df = pd.DataFrame()
        self.num_bins_lat = num_bins_lat
        self.num_bins_lon = num_bins_lon
        self.lat_bins = np.linspace(-90, 90, num_bins_lat + 1)
        self.lon_bins = np.linspace(-180, 180, num_bins_lon + 1)
        
        # Bin the stations based on latitude and longitude
        self.df["lat_bin"] = pd.cut(self.df["Lat"], bins=self.lat_bins, labels=False, include_lowest=True)
        self.df["lon_bin"] = pd.cut(self.df["Lon"], bins=self.lon_bins, labels=False, include_lowest=True)

    def generate_blacklist(self, size):
        # Generate a blacklist of station indices based on given size
        return np.random.choice(self.df.index, size, replace=False).tolist()

    def generate_whitelist(self, size):
        # Generate a whitelist of station indices based on given size
        return np.random.choice(self.df.index, size, replace=False).tolist()

    def perform_sampling(self, blacklist, whitelist):
        # Initialize DataFrames and lists to store results
        old_whitelisted = pd.DataFrame()
        unpopulated_bins = []

        # Loop through each latitude and longitude bin
        for lat_bin in range(self.num_bins_lat):
            for lon_bin in range(self.num_bins_lon):
                # Filter stations in the current bin
                bin_stations = self.df[
                    (self.df["lat_bin"] == lat_bin) & (self.df["lon_bin"] == lon_bin)
                ]
                
                # Calculate the center point of the current bin
                lat_center = (self.lat_bins[lat_bin] + self.lat_bins[lat_bin + 1]) / 2
                lon_center = (self.lon_bins[lon_bin] + self.lon_bins[lon_bin + 1]) / 2

                # Check if there are stations in the current bin
                if not bin_stations.empty:
                    # Filter whitelisted stations in the current bin
                    whitelisted_in_bin = bin_stations[
                        bin_stations.index.isin(whitelist)
                    ]

                    # Check if there are whitelisted stations in the current bin
                    if not whitelisted_in_bin.empty:
                        # Select the most centrally located whitelisted station
                        most_central_whitelisted = whitelisted_in_bin.loc[
                            (
                                (whitelisted_in_bin["Lat"] - lat_center) ** 2
                                + (whitelisted_in_bin["Lon"] - lon_center) ** 2
                            ).idxmin()
                        ]
                        # Store old whitelisted stations for reference
                        old_whitelisted = pd.concat(
                            [old_whitelisted, whitelisted_in_bin.drop(most_central_whitelisted.name)]
                        )
                        # Add the most central whitelisted station to the sample
                        self.sample_df = pd.concat([self.sample_df, most_central_whitelisted.to_frame().T])
                    else:
                        # If no whitelisted stations, select the most central station in the bin
                        most_central = bin_stations.loc[
                            (
                                (bin_stations["Lat"] - lat_center) ** 2
                                + (bin_stations["Lon"] - lon_center) ** 2
                            ).idxmin()
                        ]
                        self.sample_df = pd.concat([self.sample_df, most_central.to_frame().T])
                else:
                    # Record bins with no stations
                    unpopulated_bins.append((lat_bin, lon_bin))

        return self.sample_df, unpopulated_bins, old_whitelisted

    def print_summary_report(self, initial_count, whitelist_count, blacklist_count, total_bins, filled_bins):
        # Print summary statistics
        print("\n--- Summary Report ---")
        print(f"Total stations initially: {initial_count}")
        print(f"Total whitelist stations: {whitelist_count}")
        print(f"Total blacklist stations: {blacklist_count}")
        print(f"Total bins: {total_bins}")
        print(f"Total bins filled: {filled_bins}")
        print(f"Bins filled percentage: {filled_bins / total_bins * 100:.2f}%")
        evenness_stat_lat = self.sample_df["Lat"].std()
        evenness_stat_lon = self.sample_df["Lon"].std()
        print(f"Evenness Stat (Std Dev) - Lat: {evenness_stat_lat:.2f}, Lon: {evenness_stat_lon:.2f}")

    def plot_sample(self, sample_df, blacklist, whitelist, old_whitelisted):
        # Initialize the Plotly figure
        fig = go.Figure()

        # Add traces for various categories of stations
        self._add_scatter_trace(fig, self.df, "All Stations", "green")
        self._add_scatter_trace(fig, sample_df, "Sampled Stations", "blue")
        self._add_scatter_trace(fig, self.df.loc[whitelist], "Whitelisted Stations", "orange")
        self._add_scatter_trace(fig, self.df.loc[blacklist], "Blacklisted Stations", "red")
        self._add_scatter_trace(fig, old_whitelisted, "Old Whitelisted Stations", "purple")

        # Add bin lines for latitude and longitude
        self._add_bin_lines(fig, self.lat_bins, 'Lat')
        self._add_bin_lines(fig, self.lon_bins, 'Lon')

        # Update plot layout and display
        fig.update_geos(
            showcountries=True,
            showcoastlines=True,
            showland=True,
            fitbounds="locations",
        )
        fig.update_layout(
            height=900,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            legend=dict(yanchor="bottom", y=0.99, xanchor="left", x=0.01),
        )
        fig.show(renderer="browser")

    def _add_scatter_trace(self, fig, df, name, color):
        # Helper function to add scatter trace to Plotly figure
        fig.add_trace(
            go.Scattergeo(
                lon=df["Lon"],
                lat=df["Lat"],
                text=df["Station"],
                mode="markers",
                marker=dict(size=6, color=color, symbol="x"),
                name=name,
            )
        )

    def _add_bin_lines(self, fig, bins, axis):
        # Helper function to add bin lines to Plotly figure
        for b in bins:
            fig.add_trace(
                go.Scattergeo(
                    lon=[b, b] if axis == 'Lon' else np.linspace(-180, 180, 100),
                    lat=[-90, 90] if axis == 'Lon' else [b] * 100,
                    mode="lines",
                    line=dict(width=1, color="gray"),
                    name=f"{axis} Bin Line {b}",
                )
            )

sampler = StationSampler("C:\\Users\\chcuk\\Work\\Projects\\I2G\\stnList.json")

blacklist = sampler.generate_blacklist(10)
whitelist = sampler.generate_whitelist(10)
blacklist = [station for station in blacklist if station not in whitelist]

sample_df, unpopulated_bins, old_whitelisted = sampler.perform_sampling(blacklist, whitelist)

initial_count = len(sampler.df)
whitelist_count = len(whitelist)
blacklist_count = len(blacklist)
total_bins = sampler.num_bins_lat * sampler.num_bins_lon
filled_bins = len(sample_df)

sampler.print_summary_report(initial_count, whitelist_count, blacklist_count, total_bins, filled_bins)
sampler.plot_sample(sample_df, blacklist, whitelist, old_whitelisted)


#%%

import matplotlib.pyplot as plt

def describe_data(df, sample_df):
    """
    This function prints the descriptive statistics for the population and the sample.
    It also plots histograms to show the distributions of Longitude and Latitude in the population and the sample.
    """
    print("Population Descriptive Statistics:")
    print(df.describe())
    print("\nSample Descriptive Statistics:")
    print(sample_df.describe())
    
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    axs[0, 0].hist(df["Lon"], bins=20, alpha=0.7, color="skyblue", edgecolor="black")
    axs[0, 0].set_title("Population Longitude")
    axs[0, 0].set_xlabel("Longitude")
    axs[0, 0].set_ylabel("Frequency")
    axs[0, 1].hist(sample_df["Lon"], bins=20, alpha=0.7, color="skyblue", edgecolor="black")
    axs[0, 1].set_title("Sample Longitude")
    axs[0, 1].set_xlabel("Longitude")
    axs[0, 1].set_ylabel("Frequency")
    axs[1, 0].hist(df["Lat"], bins=20, alpha=0.7, color="skyblue", edgecolor="black")
    axs[1, 0].set_title("Population Latitude")
    axs[1, 0].set_xlabel("Latitude")
    axs[1, 0].set_ylabel("Frequency")
    axs[1, 1].hist(sample_df["Lat"], bins=20, alpha=0.7, color="skyblue", edgecolor="black")
    axs[1, 1].set_title("Sample Latitude")
    axs[1, 1].set_xlabel("Latitude")
    axs[1, 1].set_ylabel("Frequency")
    
    
    plt.tight_layout()
    plt.show()

# describe_data(df, sample_df)


