# ckan-downloader
An interactive command-line utility for downloading data from a CKAN data portal.

Provide a CSV with or specify some dataset IDs to start downloading all resources attached to those datasets into folders. 

## Installation
```
pip install ckan-downloader
```

## Example usage
```
$ python -m ckan_downloader

CKAN Downloader 0.1.0

What is the data portal URL? 
> geoscience.data.qld.gov.au

Test connection to https://geoscience.data.qld.gov.au/api/action/site_read was successful.

Do you have a CSV with the dataset IDs to download? (y/n) 
> y

What is the CSV file path? 
> tests/test1.csv

Does this CSV have a header row? (y/n) 
> y

The name of the field/column containing the dataset IDs is needed. The options are:
   id, PID, Report Title
Which field has the IDs? 
> PID

Which directory should the downloads be saved in? 
> downloads

Starting dataset cr109373
Downloading CR109373 Report Geometry (https://geoscience.data.qld.gov.au/dataset/e2f7ae5f-e62a-403d-ba55-539074a5380c/resource/geo-doc363732-cr109373/download/%252FReport%25252f109373%25252fDocument%25252f363732%25252f109373.zip) to downloads/cr109373/109373.zip
Downloading WHOLE REPORT (https://gsq-horizon.s3-ap-southeast-2.amazonaws.com/QDEX/109373/cr_109373_1.pdf) to downloads/cr109373/cr_109373_1.pdf
Starting dataset cr108134
Downloading CR108134 Report Geometry (https://geoscience.data.qld.gov.au/dataset/61d06582-c2cf-48ce-a5de-162e71f38ab3/resource/geo-doc361522-cr108134/download/%252FReport%25252f108134%25252fDocument%25252f361522%25252f108134.zip) to downloads/cr108134/108134.zip
Downloading WHOLE REPORT (https://gsq-horizon.s3-ap-southeast-2.amazonaws.com/QDEX/108134/cr_108134_1.pdf) to downloads/cr108134/cr_108134_1.pdf

```

## Future improvements
* add command line options to skip interactive mode
* search by spatial extent
* include or skip certain filetypes
* use progress bars