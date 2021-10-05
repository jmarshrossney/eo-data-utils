# Accessing Copernicus data

The data we would like to download is the [CORA 5.2 dataset for global in situ temperature and salinity measurements](https://resources.marine.copernicus.eu/product-detail/INSITU_GLO_TS_REP_OBSERVATIONS_013_001_b/INFORMATION) (also see [this article](https://os.copernicus.org/articles/15/1601/2019/)).
Copernicus give us [several options](https://help.marine.copernicus.eu/en/articles/4682988-what-are-the-data-access-endpoints-for-copernicus-marine-products-and-datasets).

The data is provided as a set of [tar](https://en.wikipedia.org/wiki/Tar_(computing%29) archives (`.tgz`), which contain yearly databases in [NetCDF](https://en.wikipedia.org/wiki/NetCDF) format (`.nc`).
It should not be necessary to extract all of the archives; archives can be accessed as and when the data is needed to save disk space.

## Method 1: Browsing the filesystem over FTP

1. [Log in to the server](https://help.marine.copernicus.eu/en/articles/4683022-what-are-the-advantages-of-the-file-transfer-protocol-ftp-data-access-service) holding the reprocessed and reanalysis products

```sh
$ ftp my.cmems-du.eu
Connected to my.cmems-du.eu.
220 Welcome to CMEMS MY FTP service
Name (my.cmems-du.eu:joe): <enter your username>
331 Please specify the password.
Password: <enter your password>
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> pass  # switch to passive mode
ftp> cd Core/INSITU_GLO_TS_REP_OBSERVATIONS_013_001_b/CORIOLIS-GLOBAL-EasyCORA-OBS/
```

2. Copy the data to your local directory

```sh
ftp> cd <whichever directory>
ftp> lcd <whichever local directory>
ftp> get <whicever .tgz file>
```

3. Close the FTP connection

```sh
ftp> bye
421 Timeout.
```

## Method 2: Transfer using wget

```sh
$ wget --user=<username> --ask-password ftp://my.cmems-du.eu/Core/INSITU_GLO_TS_REP_OBSERVATIONS_013_001_b/CORIOLIS-GLOBAL-EasyCORA-OBS/<path_to_archive>.tgz
Password for user 'username': <enter your password>
```
