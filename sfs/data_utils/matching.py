import datetime
import pathlib
from types import SimpleNamespace

import ee
import numpy as np
import pandas as pd
import xarray as xr
import yaml

from extractor import OpenArchive
from ftp_downloader import FTPDataDownloader


def date_parser(file):
    """Extract date from these cmems archive."""
    parts = file.name.split("_")
    print(parts[2])
    date = parts[2]
    date = date[:4] + "-" + date[4:6] + "-" + date[6:]
    return ee.Date(date)

def filter_date(files):
    filtered = [file for file in files if int(file.stem[-4:]) > 2018]
    print(f"Removed {len(files) - len(filtered)} files with date not > 2018")
    return filtered
    

ee.Initialize()

geometry = ee.Geometry.Polygon(
    [
        [
            [27.338252711386975, 46.78303213409735],
            [27.338252711386975, 40.76170683114531],
            [41.92809646138698, 40.76170683114531],
            [41.92809646138698, 46.78303213409735],
        ]
    ]
)
images = ee.ImageCollection("COPERNICUS/S3/OLCI").filterBounds(geometry)
#print(images.first().bandNames().getInfo())

with open("examples/cmems_example.yml", "r") as file:
    config = SimpleNamespace(**yaml.safe_load(file))

downloader = FTPDataDownloader(
    config.host,
    config.source,
    exclude_dirs=config.exclude,
    target_dir="in_situ_downloaded/",
)
downloader.register_filter(filter_date)

downloader.check_credentials()
downloader.dry_run()


keepvars = ["PSAL", "TEMP", "DEPTH", "LATITUDE", "LONGITUDE", "JULD"]

for archive in downloader:
    print(archive)
    with OpenArchive(archive) as files:
        for file in files:

            date = date_parser(file)
            filtered_images = images.filterDate(date.getRange("day"))

            if filtered_images.size().getInfo() == 0:
                print("No images on this date")
                continue

            print("num images: ", filtered_images.size().getInfo())

            ds = xr.open_dataset(file)

            # Drop variables that I don't care about
            ds = ds.drop_vars([v for v in ds.data_vars if v not in keepvars])

            # Stack the profile index and depth level index
            # NOTE: this may be undesirable - could introduce correlations in dataset
            # Actually I just want the top level anyway
            ds = ds.stack(dimensions={"INDEX": ("N_PROF", "N_LEVELS")})

            # Create mask for entries with depth below threshold of 5m
            # NOTE: I shouldn't have to assign MASK to the dataset object itself
            ds = ds.assign(MASK=("INDEX", ds.DEPTH.values < 50))

            # Fills the 'masked' entries with Na*, then drop the mask
            ds = ds.where(ds.MASK)
            ds = ds.drop_vars("MASK")

            # Drop the Na*
            ds = ds.dropna(dim="INDEX")

            df = ds.to_pandas()

            print(df.head())
            print("")
