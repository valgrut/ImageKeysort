ROOT_DIR="./"
NAME=image-keysort.py

run:
    pyrcc5 ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py
	python3 ${ROOT_DIR}/${NAME}

build:
	pyinstaller --onefile ${ROOT_DIR}/${NAME}

clean:
	rm -rf dist
	rm -rf build
	rm image-keysort.spec

phony: run, test, build, clean
