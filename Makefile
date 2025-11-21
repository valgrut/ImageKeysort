ROOT_DIR=./
NAME=main.py
SCSS_STYLES=static/app-styles.scss
QSS_STYLES=static/app-styles.qss
# PYTEST_ARGS="-v"  # -v | -vv |  
PYTEST_ARGS=""  # Empty

config:
	( \
	python3 -m venv venv; \
	source ${ROOT_DIR}/venv/bin/activate; \
	pip install -r ${ROOT_DIR}/requirements.txt; \
	pyrcc5 ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py; \
	deactivate; \
	)
	# - at the start makes makefile to ignore the potential error:
	- pyrcc5.exe ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py

run: config qss
	( \
	source ${ROOT_DIR}/venv/bin/activate; \
	pyrcc5 ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py; \
	python3 ${ROOT_DIR}/src/${NAME}; \
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
	pyinstaller --onefile ${ROOT_DIR}/${NAME}

clean:
	rm -rf dist
	rm -rf build
	rm image-keysort.spec
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -delete

phony: config, run, test, build, clean, qss
