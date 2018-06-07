Scipts to download submission from the UNFCCC's
[National Inventory Submissions page](https://unfccc.int/process/transparency-and-reporting/reporting-and-review-under-the-convention/greenhouse-gas-inventories-annex-i-parties/national-inventory-submissions-2018)

Currently downloads files from the 2018 submission page.
Requires Python 3.
Dependencies can be installed in a virtual environment with `make venv`

Run

```
make data-2018
```

to generate or update a list of all available submissions in `data` as a CSV file for the year 2018, or any other year from 2008.

Run any of (adjusting the year as needed)
```
make download-crf-2018
make download-nir-2018
make download-sef-2018
```

to download and unzip all files into `downloads`.
Zip files are stored in `archive`.

On Windows (or if make is not available the Python scripts can be run directly as well,
the libraries in `script/requirements.txt` need to be available.

To update the list of files for a specific year:
```
python scripts/process.py 2018
```

To download (CRD, NIR, or SEF as category):

```
python scripts/download.py CRF 2018
```
