.SILENT: help
help:
	echo Options:
	echo make data-bur: Download BUR submissions data
	echo make download-bur: Download BUR submissions
	echo make data-2019: Download NIR submissions data for 2019
	echo make download-crf-2019: Download NIR submissions data for 2019
	echo Download options: "crf, ""nir" and "sef" .

data-%: venv
	./venv/bin/python scripts/process.py $(word 2, $(subst -, , $@))

data-bur: venv
	./venv/bin/python scripts/process_bur.py

download-bur: venv
	./venv/bin/python scripts/download_bur.py

download-crf-%: venv
	./venv/bin/python scripts/download.py CRF $(word 3, $(subst -, , $@))

download-nir-%: venv
	./venv/bin/python scripts/download.py NIR $(word 3, $(subst -, , $@))

download-sef-%: venv
	./venv/bin/python scripts/download.py SEF $(word 3, $(subst -, , $@))

venv: scripts/requirements.txt
	[ -d ./venv ] || python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -Ur scripts/requirements.txt
	touch venv

clean:
	rm -rf data/*.csv
	rm -rf downloads/*
	rm -rf archive/*

.PHONY: clean download
