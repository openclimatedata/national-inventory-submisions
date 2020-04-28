import argparse
#import requests
import time
import pandas as pd
#import os
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from random import randrange

max_tries = 10

root = Path(__file__).parents[1]

descr = ("Download UNFCCC National Inventory Submissions lists "
         "and create list of submissions as CSV file")
parser = argparse.ArgumentParser(description=descr)
parser.add_argument(
    'year',
    help='Year to download'
)

args = parser.parse_args()
year = args.year

print("Fetching submissions for {}".format(year))

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

if int(year) == 2020:
    url = (
            "https://unfccc.int/ghg-inventories-annex-i-parties/{}".format(year)
            )

print(url)

#result = requests.get(url)

# set options for headless mode
options = webdriver.firefox.options.Options()
options.add_argument('-headless')

# create profile for headless mode and automatical downloading
profile = webdriver.FirefoxProfile()

# set up selenium driver
driver = webdriver.Firefox(options = options, firefox_profile = profile)
driver.get(url)


html = BeautifulSoup(driver.page_source, "html.parser")


table = html.find("table")

# check if table found. if not the get command didn't work, likely because of a captcha on the site
### TODO replace by error message
if not(table):
    # try to load htm file from disk
    print('Download failed, trying to load manually downloaded file')
    file = open("manual_page_downloads/National-Inventory-Submissions-{}.html".format(year))
    content = file.read()
    html = BeautifulSoup(content, "html.parser")
    table = html.find("table")
    if not(table):
        print("Manually downloaded file " + "manual_page_downloads/National-Inventory-Submissions-{}.html".format(year) + 
              " not found")
        exit()
    
links = table.findAll('a')

targets = []  # sub-pages
downloads = []
no_downloads = []

# Check links for Zipfiles or subpages
for link in links:
    if "href" not in link.attrs:
        continue
    href = link.attrs["href"]
    if "/documents/" in href:
        if "title" in link.attrs.keys():
            title = link.attrs["title"]
        else:
            title = link.contents[0]
        if href.startswith("/documents"):
            href = "https://unfccc.int" + href
        # Only add pages in the format https://unfccc.int/documents/65587
        # to further downloads
        if str(Path(href).parent).endswith("documents"):
            targets.append({"title": title, "url": href})
    elif href.endswith(".zip"):
        if href.startswith("/files"):
            href = "https://unfccc.int" + href
        country = Path(href).name.split("-")[0].upper()
        title =  "{} {}".format(country, link.contents[0])
        print("\t".join([title, href]))
        downloads.append({"Title": title, "URL": href})

# Go through sub-pages.
for target in targets:
    time.sleep(randrange(5, 15))
    url = target["url"]
    i = 0
    while i < max_tries:
        try:
            #subpage = requests.get(url, timeout=15.5)
            #html = BeautifulSoup(subpage.content, "html.parser")
            driver.get(url)
            html = BeautifulSoup(driver.page_source, "html.parser")
            title = html.find("h1").contents[0]
            break
        except AttributeError:
            print("Error fetching " + target["url"])
            print("Retrying ...")
            time.sleep(randrange(5, 15))
            i += 1
            continue
    
    if i == max_tries:
        print("Aborting after {}".format(max_tries) + " tries")
        quit()

    h2 = html.find("h2", text="Versions")
    if h2:
        div = h2.findNext("div")
        links = div.findAll("a")
        if len(links) > 1:
            print("Warning: More than one link found. Downloading only the first file.")
        zipfile = links[0].attrs["href"]
        downloads.append({"Title": title, "URL": zipfile})
        print("\t".join([title, url, zipfile]))
    else:
        no_downloads.append((title, url))

if len(no_downloads) > 0:
    print("No downloads for ", no_downloads)

driver.close()
df = pd.DataFrame(downloads)
df.to_csv(root / "data/submissions-{}.csv".format(year), index=False)
