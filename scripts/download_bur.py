import pandas as pd
import requests
import shutil
import time
import os
from datetime import date
from selenium import webdriver
from random import randrange

from pathlib import Path
root = Path(__file__).parents[1]

###############
# TODO
# download directly via silenium see link below
# https://sqa.stackexchange.com/questions/2197/
# how-to-download-a-file-using-seleniums-webdriver
###############

submissions = pd.read_csv(root / "data/submissions-bur.csv")

# use the CRF data url, for some reson visinting the BUR url
# is not enough to generate the necessary cookies
url = "https://unfccc.int/BURs"

error_file_sizes = [212, 210]

BUR_folders = {
        'BUR1': 'first_BUR_files',
        'BUR2': 'second_BUR_files',
        'BUR3': 'third_BUR_files',
        'BUR4': 'fourth_BUR_files',
        'BUR5': 'fifth_BUR_files'
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
# options.add_argument('-headless')

# create profile for headless mode 
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2)

# set up selenium driver
driver = webdriver.Firefox(options=options, firefox_profile=profile)

# visit the main data page once to create cookies
driver.get(url)
time.sleep(20)

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
    local_filename_underscore = \
        download_path / BUR_folders[bur] / country / \
        url.split('/')[-1].replace("%20", "_").replace(" ", "_")
    if not local_filename.parent.exists():
        local_filename.parent.mkdir()

    if local_filename.exists():
        # rename
        local_filename.rename(local_filename_underscore)
        print("Renamed " + BUR_folders[bur] + "/" + country + "/" + local_filename.name)

    if local_filename_underscore.exists():
        # check file size. if 210 bytes it's the error page
        if Path(local_filename_underscore).stat().st_size in error_file_sizes:
            # found the error page. delete file
            os.remove(local_filename_underscore)
    
    if not local_filename_underscore.exists():
        i = 0  # reset counter
        while not local_filename_underscore.exists() and i < 10:
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
                    
            r = requests.get(url, stream=True, cookies = cookies)
            with open(str(local_filename_underscore), 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            
            # check file size. if 210 bytes it's the error page
            if Path(local_filename_underscore).stat().st_size in error_file_sizes:
                # found the error page. delte file
                os.remove(local_filename_underscore)
            
            # sleep a bit to avoid running into captchas
            time.sleep(randrange(5, 15))
            
        if local_filename_underscore.exists():
            new_downloaded.append(submission)
            print("Download => download/BUR/" + BUR_folders[bur] + "/" + country +
                  "/" + local_filename_underscore.name)
        else:
            print("Failed downloading download/BUR/" + BUR_folders[bur] + "/"
                  + country + "/" + local_filename_underscore.name)
        
    else:
        print("=> Already downloaded " + local_filename_underscore.name)

driver.close()

df = pd.DataFrame(new_downloaded)
df.to_csv(download_path / "00_new_downloads-{}.csv".format(date.today()), index=False)
