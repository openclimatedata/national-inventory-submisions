import pandas as pd
import requests
import shutil
import time
from datetime import date
from selenium import webdriver
from random import randrange

from pathlib import Path
root = Path(__file__).parents[1]

###############
### TODO
### sort into proper folders (BUR X/country)
###############

submissions = pd.read_csv(root / "data/submissions-bur.csv")

# use the CRF data url,for some reson visinting the BUR url is not enough to generate the necessary cookies
url = "https://unfccc.int/ghg-inventories-annex-i-parties/2020"

BUR_folders = {
        'BUR1': 'first_bur_files',
        'BUR2': 'second_bur_files',
        'BUR3': 'third_bur_files',
        'BUR4': 'fourth_bur_files',
        'BUR5': 'fifth_bur_files'
        }

# Ensure download path ans subfolders exist
present_BURs = submissions.Kind.unique()

download_path = root / "downloads/BUR"
if not download_path.exists():
    download_path.mkdir(parents=True)

for BUR in present_BURs:
    download_path_BUR = root / "downloads/BUR" / BUR_folders[BUR]
    if not download_path_BUR.exists():
        download_path_BUR.mkdir(parents=True)

# set options for headless mode
options = webdriver.firefox.options.Options()
options.add_argument('-headless')

# create profile for headless mode 
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2)

# set up selenium driver
driver = webdriver.Firefox(options = options, firefox_profile = profile)

# visit the main data page once to create cookies
driver.get(url)
time.sleep(10)

# get the session id cookie
cookies_selenium = driver.get_cookies()
cookies = {}
for cookie in cookies_selenium:
    cookies[cookie['name']] = cookie['value']

print(cookies)

new_downloaded = []

for idx, submission in submissions.iterrows():
    print("=" * 60)
    bur = submission.Kind
    title = submission.Title
    url = submission.URL
    country = submission.Country
    country = country.replace(' ', '_')
    print(title)

    local_filename = download_path / BUR_folders[bur] / country / url.split('/')[-1]
    if not local_filename.exists():
        if not local_filename.parent.exists():
            local_filename.parent.mkdir()
        r = requests.get(url, stream=True, cookies = cookies)
        with open(str(local_filename), 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        
        new_downloaded.append(submission)
        print("Download => download/BUR/" + BUR_folders[bur] + "/" + country + "/" + local_filename.name)
        
        # sleep a bit to avoid running into captchas
        time.sleep(randrange(5, 15))
    else:
        print("=> Already downloaded " + local_filename.name)

driver.close()

df = pd.DataFrame(new_downloaded)
df.to_csv(download_path / "00_new_downloads-{}.csv".format(date.today()), index=False)