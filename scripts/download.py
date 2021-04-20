import argparse
import pandas as pd
import zipfile
import re
import requests
import shutil
from datetime import date
import time
from random import randrange
from selenium import webdriver
from pathlib import Path
import os

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

# generate the correct url
url = (
    "https://unfccc.int/process/transparency-and-reporting/"
    "reporting-and-review-under-the-convention/"
    "greenhouse-gas-inventories-annex-i-parties/"
    "submissions/national-inventory-submissions-{}".format(year)
)


if int(year) == 2019:
    url = (
           "https://unfccc.int/process-and-meetings/transparency-and-reporting/"
           "reporting-and-review-under-the-convention/"
           "greenhouse-gas-inventories-annex-i-parties/"
           "national-inventory-submissions-{}".format(year)
          )

if int(year) >= 2020:
    url = (
            "https://unfccc.int/ghg-inventories-annex-i-parties/{}".format(year)
            )


submissions = pd.read_csv(root / "data/submissions-{}.csv".format(year))
regexp = re.compile(r"[-_]{}[-_]".format(category.lower()))
items = submissions[submissions.URL.str.contains(regexp)]
error_file_sizes = [212, 210]

# Ensure download path exists and remove earlier versions.
download_path = root / "downloads/{}{}".format(category, year)
if download_path.exists():
    shutil.rmtree(str(download_path))
download_path.mkdir(parents=True)

# ensure archive path exists
archive_path = root / "archive/{}".format(year)
if not archive_path.exists():
    archive_path.mkdir(parents=True, exist_ok=True)
print("Archiving data to " + str(archive_path.absolute()))


# set options for headless mode
options = webdriver.firefox.options.Options()
#options.add_argument('-headless')

# create profile for headless mode 
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2)

# set up selenium driver
driver = webdriver.Firefox(options=options, firefox_profile=profile)

# visit the main data page once to initiate a session ID
driver.get(url)
time.sleep(10)

# get the session id cookie
cookies_selenium = driver.get_cookies()
cookies = {}
for cookie in cookies_selenium:
    cookies[cookie['name']] = cookie['value']

# print(cookies)
#quit()

new_downloaded = []

for idx, submission in items.iterrows():
    print("=" * 60)
    title = submission.Title
    url = submission.URL
    print(title)
    print(url)

    local_filename = archive_path / url.split('/')[-1]

    if local_filename.exists():
        # check file size. if 210 or 212 bytes it's the error page
        if Path(local_filename).stat().st_size in error_file_sizes:
            # found the error page. delete file
            os.remove(local_filename)

    if not local_filename.exists():
        i = 0  # reset counter
        while not local_filename.exists() and i < 10:
            # for i = 0 and i = 5 try to get a new session ID
            if i == 1 or i == 5:
                driver = webdriver.Firefox(options=options, firefox_profile=profile)

                # visit the main data page once to create cookies
                driver.get(url)
                time.sleep(20)

                # get the session id cookie
                cookies_selenium = driver.get_cookies()
                cookies = {}
                for cookie in cookies_selenium:
                    cookies[cookie['name']] = cookie['value']

            r = requests.get(url, stream=True, cookies=cookies)
            with open(str(local_filename), 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            # check file size. if 210 bytes it's the error page
            if Path(local_filename).stat().st_size in error_file_sizes:
                # found the error page. delete file
                os.remove(local_filename)

            # sleep a bit to avoid running into captchas
            time.sleep(randrange(5, 15))

        if local_filename.exists():
            new_downloaded.append(submission)
            print("Download => archive/{}/".format(year) + local_filename.name)
        else:
            print("Failed to download => archive/{}/".format(year) + local_filename.name)
    else:
        print("=> Already downloaded " + local_filename.name)
    try:
        zipped_file = zipfile.ZipFile(str(local_filename), 'r')
        zipped_file.extractall(str(download_path))
        print("Extracted {} files.".format(len(zipped_file.namelist())))
        zipped_file.close()
    # TODO Better error logging/visibilty
    except zipfile.BadZipFile:
        print("Error while trying to extract " + str(download_path))
    except NotImplementedError:
        print("Zip format not supported, please unzip on the command line.")

driver.close()

df = pd.DataFrame(new_downloaded)
df.to_csv(archive_path / "00_new_downloads-{}.csv".format(date.today()), index=False)