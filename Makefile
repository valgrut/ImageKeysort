NAME=image-keysort.py

run:
	python3 ${NAME}

build:
	pyinstaller --onefile ${NAME}

clean:
	rm -rf dist
	rm -rf build
	rm image-keysort.spec

phony: run, test, build, clean
