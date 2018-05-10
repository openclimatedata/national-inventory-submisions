Scipts to download submission from the UNFCCC's
[National Inventory Submissions page](https://unfccc.int/process/transparency-and-reporting/reporting-and-review-under-the-convention/greenhouse-gas-inventories-annex-i-parties/national-inventory-submissions-2018)

Currently downloads files from the 2018 submission page.
Requires Python 3.

Run

```
make
```

to generate a list of all available submissions in `data`.

Run
```
make download-crf
```

to download and unzip all CRF file into `downloads`. Zip files are stored in `archive`.

