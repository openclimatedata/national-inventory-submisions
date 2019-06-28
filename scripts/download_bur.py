import pandas as pd
import zipfile
import re
import requests
import shutil

from pathlib import Path
root = Path(__file__).parents[1]

submissions = pd.read_csv(root / "data/submissions-bur.csv")

# Ensure download path exists and remove earlier versions.
download_path = root / "downloads/BUR"

for idx, submission in submissions.iterrows():
    print("=" * 60)
    title = submission.Title
    url = submission.URL
    print(title)

    local_filename = download_path / url.split('/')[-1]
    if not local_filename.exists():
        r = requests.get(url, stream=True)
        with open(str(local_filename), 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print("Download => download/BUR/" + local_filename.name)
    else:
        print("=> Already downloaded " + local_filename.name)
