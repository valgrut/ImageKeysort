ROOT_DIR=./
NAME=main.py

config:
	( \
	python3 -m venv venv; \
	source ${ROOT_DIR}/venv/bin/activate; \
	pip install -r ${ROOT_DIR}/requirements.txt; \
	deactivate; \
	)

run: config
	( \
	source ${ROOT_DIR}/venv/bin/activate; \
	pyrcc5 ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py; \
	python3 ${ROOT_DIR}/src/${NAME}; \
	deactivate; \
	)

test: config
	( \
	source ${ROOT_DIR}/venv/bin/activate; \
	PYTHONPATH=${ROOT_DIR}/src pytest ${ROOT_DIR}/tests/*; \
	deactivate; \
	)
	# PYTHONPATH=${ROOT_DIR}/src pytest -v tests/; \

build:
	pyinstaller --onefile ${ROOT_DIR}/${NAME}

clean:
	rm -rf dist
	rm -rf build
	rm image-keysort.spec
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -delete

phony: config, run, test, build, clean
