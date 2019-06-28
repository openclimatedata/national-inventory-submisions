data-%: venv
	./venv/bin/python scripts/process.py $(word 2, $(subst -, , $@))

data-bur: venv
	./venv/bin/python scripts/process_bur.py

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
