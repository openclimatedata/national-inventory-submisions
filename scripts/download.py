import pandas as pd
import zipfile
import requests
import shutil

from pathlib import Path

root = Path(__file__).parents[1]

submissions = pd.read_csv(root / "data/submissions-2018.csv")

crfs = submissions[submissions.URL.str.contains("-crf-")]
for idx, submission in crfs.iterrows():
    print("=" * 60)
    title = submission.Title
    url = submission.URL
    print(title)

    local_filename = root / "archive" / url.split('/')[-1]
    if not local_filename.exists():
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print("Downloaded => archive/" + local_filename.name)
    else:
        print("=> Already downloaded archive/" + local_filename.name)
    zipped_file = zipfile.ZipFile(local_filename, 'r')
    zipped_file.extractall(root / "downloads")
    print("Extracted {} files.".format(len(zipped_file.namelist())))
    zipped_file.close()
