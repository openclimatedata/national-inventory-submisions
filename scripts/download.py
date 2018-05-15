import argparse
import pandas as pd
import zipfile
import re
import requests
import shutil

from pathlib import Path

descr = 'Download and unzip data from UNFCCC National Inventory Submissions'
parser = argparse.ArgumentParser(description=descr)
parser.add_argument(
    'category',
    help='Category download, CRF, NIR, SEF'
)
parser.add_argument(
    'year',
    help='Year to download'
)

args = parser.parse_args()
year = args.year
category = args.category
print(category, year)
root = Path(__file__).parents[1]

submissions = pd.read_csv(root / "data/submissions-{}.csv".format(year))
regexp = re.compile(r"[-_]{}[-_]".format(category.lower()))
items = submissions[submissions.URL.str.contains(regexp)]

# Ensure download path exists and remove earlier versions.
download_path = root / "downloads/{}{}".format(category, year)
if download_path.exists():
    shutil.rmtree(download_path)
download_path.mkdir(parents=True)

for idx, submission in items.iterrows():
    print("=" * 60)
    title = submission.Title
    url = submission.URL
    print(title)

    archive_path = root / "archive/{}".format(year)
    if not archive_path.exists():
        archive_path.mkdir(parents=True, exist_ok=True)
    local_filename = archive_path / url.split('/')[-1]
    if not local_filename.exists():
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print("Download => archive/{}/".format(year) + local_filename.name)
    else:
        print("=> Already downloaded " + local_filename.name)
    try:
        zipped_file = zipfile.ZipFile(local_filename, 'r')
        zipped_file.extractall(download_path)
        print("Extracted {} files.".format(len(zipped_file.namelist())))
        zipped_file.close()
    # TODO Better error logging/visibilty
    except zipfile.BadZipFile:
        print("Error while trying to extract " + str(download_path))
    except NotImplementedError:
        print("Zip format not supported, please unzip on the command line.")


