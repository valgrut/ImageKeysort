
ROOT_DIR	:= $(abspath .)
VENV_DIR	?= $(ROOT_DIR)/.venv

NAME		?= main.py
APP_NAME    ?= image-keysort
APP_MODULE	?= src.main
REQ_FILE    ?= requirements.txt

SCSS_STYLES	?= static/app-styles.scss
QSS_STYLES	?= static/app-styles.qss

PYTEST_ARGS	?= "-v"  # -v | -vv |
# PYTEST_ARGS=""  # Empty

# RUN_ARGS = python3 -m src.main
# RUN_ARGS = python3 -m src.main --src-path ~/Pictures/ --presets-path ~/Pictures/test_options.json
# RUN_ARGS = /usr/bin/python3 -m src.main --src-path ~/Repositories/WorkstationSetup/scripts/image-sorter/testing-data/downloads/ --set-copy-mode
RUN_ARGS ?= python3 -m src.main --src-path ~/Pictures/ --presets-path ~/Repositories/WorkstationSetup/scripts/image-sorter/presets/data.json
# RUN_ARGS = python3 -m src.main --src-path /home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/testing-data/downloads
# RUN_ARGS = python3 -m src.main --src-path C:\Users\Kyuubi\Repositories\WorkstationSetup\scripts\image-sorter\testing-data\downloads

config:
	( \
	python3 -m venv venv; \
	source ${ROOT_DIR}/venv/bin/activate; \
	pip install -r ${ROOT_DIR}/requirements.txt; \
	pyrcc5 ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py; \
	deactivate; \
	)
	# '-' at the start makes makefile to ignore the potential error:
	- pyrcc5.exe ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py

# TODO: tady duplikatne vytvarim ty resource files, zbytecne. Prvne se vola config, takze v run to uz byt nemusi.
run: config qss
	( \
	source ${ROOT_DIR}/venv/bin/activate; \
	pyrcc5 ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py; \
	cd ${ROOT_DIR}; \
	$(RUN_ARGS) ; \
	deactivate; \
	)

test: config
	( \
	source ${ROOT_DIR}/venv/bin/activate; \
	PYTHONPATH=${ROOT_DIR}/src pytest ${PYTEST_ARGS} ${ROOT_DIR}/tests/*; \
	deactivate; \
	)
	# PYTHONPATH=${ROOT_DIR}/src pytest -v tests/; \

qss:
	qtsass $(SCSS_STYLES) -o $(QSS_STYLES)

build:
	pyinstaller --onefile ${ROOT_DIR}/src/${NAME}

clean:
	rm -rf dist
	rm -rf build
	# rm image-keysort.spec
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -delete

phony: config, run, test, build, clean, qss
