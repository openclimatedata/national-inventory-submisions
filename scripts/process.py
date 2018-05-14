import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

root = Path(__file__).parents[1]



url = (
    "https://unfccc.int/process/transparency-and-reporting/"
    "reporting-and-review-under-the-convention/"
    "greenhouse-gas-inventories-annex-i-parties/"
    "national-inventory-submissions-2018"
)

result = requests.get(url)

html = BeautifulSoup(result.content, "html.parser")
table = html.find('table')
links = table.findAll('a')

targets = []

for link in links:
    href = link.attrs["href"]
    if "/documents/" in href:
        if "title" in link.attrs.keys():
            title = link.attrs["title"]
        else:
            title = link.contents[0]
        if href.startswith("/documents"):
            href = "https://unfccc.int" + href
        targets.append({"title": title, "url": href})

downloads = []
no_downloads = []
for target in targets:
    url = target["url"]
    subpage = requests.get(url)
    html = BeautifulSoup(subpage.content, "html.parser")
    title = html.find("h1").contents[0]
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
df.to_csv(root / "data/submissions-2018.csv", index=False)
