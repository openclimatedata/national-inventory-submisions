import argparse
import requests
import time
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

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
    "national-inventory-submissions-{}".format(year)
)

if int(year) < 2017:
    url = ("https://unfccc.int/process/transparency-and-reporting/reporting-and-review-under-the-convention/greenhouse-gas-inventories/submissions-of-annual-greenhouse-gas-inventories-for-2017/submissions-of-annual-ghg-inventories-{}".format(year))

result = requests.get(url)

html = BeautifulSoup(result.content, "html.parser")
table = html.find("table")
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
    url = target["url"]
    while True:
        try:
            subpage = requests.get(url, timeout=15.5)
            html = BeautifulSoup(subpage.content, "html.parser")
            title = html.find("h1").contents[0]
            break
        except AttributeError:
            print("Error fetching " + target["url"])
            print("Retrying ...")
            time.sleep(1)
            continue

    h2 = html.find("h2", text="Versions")
    if h2:
        div = h2.findNext("div")
        links = div.findAll("a")
        if len(links) > 1:
            raise ValueError("More than one link found. Please update script"
                             " to handle multiple links.")
        zipfile = links[0].attrs["href"]
        downloads.append({"Title": title, "URL": zipfile})
        print("\t".join([title, url, zipfile]))
    else:
        no_downloads.append((title, url))

if len(no_downloads) > 0:
    print("No downloads for ", no_downloads)

df = pd.DataFrame(downloads)
df.to_csv(root / "data/submissions-{}.csv".format(year), index=False)
