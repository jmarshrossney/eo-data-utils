# Earth Observation Data Utils

A collection of useful utilities for downloading and combining Earth Observation datasets from the likes of Copernicus (CMEMS) and Google Earth Engine.

## Installation

Clone the repository:

```
git clone https://github.com/marshrossney/eo-data-utils
cd eo-data-utils
```

Create a conda environment using the `environment.yml` file provided, which uses Python 3.9:

```
conda env create --file environment.yml
```

Activate the environment and install the package:

```
conda activate eodu
flit install --symlink
```

Run the tests:

```
pytest --pyargs eo_data_utils
```

## Download in-situ data from Copernicus

To do

## Extract and match downloaded data with Google Earth Engine dataset

To do

