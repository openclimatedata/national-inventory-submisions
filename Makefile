all: data/submissions-2018.csv

data/submissions-2018.csv: venv
	./venv/bin/python scripts/process.py

download-crf: data/submissions-2018.csv
	./venv/bin/python scripts/download.py

venv: scripts/requirements.txt
	[ -d ./venv ] || python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -Ur scripts/requirements.txt
	touch venv

clean:
	rm -rf data/*.csv
	rm -rf downloads/*.xlsx
	rm -rf archive/*.zip

.PHONY: clean download
