"""
Some examples of how to manipulate xarray.DataSet objects containing the Copernicus
in-situ data.
"""
# TODO turn into helper functions, add tests

import numpy as np
import pandas as pd
import xarray as xr

def filter_depth(dataset: xr.Dataset, thresh: float = 5.0):
    """Throw away measurements taken at a depth greater than the given threshold."""
    # Ideally the last 4 should be 'coords' not 'data_vars'
    keepvars = ["PSAL", "TEMP", "DEPTH", "LATITUDE", "LONGITUDE", "JULD"]
    
    ds = dataset.copy()
    
    # Drop variables that I don't care about
    ds = ds.drop_vars([v for v in ds.data_vars if v not in keepvars])

    # Stack the profile index and depth level index
    # NOTE: this may be undesirable - could introduce correlations in dataset
    ds = ds.stack(dimensions={"INDEX": ("N_PROF", "N_LEVELS")})

    # Create mask for entries with depth below threshold
    # NOTE: I shouldn't have to assign a new variable to the dataset object
    ds = ds.assign(MASK=("INDEX", ds.DEPTH.values < thresh))

    # Fills the 'masked' entries with Na*, then drop the mask
    ds = ds.where(ds.MASK)
    ds = ds.drop_vars("MASK")
    
    # Drop the Na*
    ds = ds.dropna(dim="INDEX")

    df = ds.to_pandas()

    print("Original dataset:\n------------------")
    print(dataset)
    print()
    print("New dataset:\n-----------------")
    print(ds)
    print()
    print("As dataframe:\n----------------")
    print(df)

if __name__ == "__main__":
    dataset = xr.open_dataset("cora5.2/easy/ECO_DMQCGL01_20200630_TS_TS.nc")
    filter_depth(dataset)

