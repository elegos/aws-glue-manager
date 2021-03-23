.PHONY: all clean test build-dist copy-icons

all : clean test dist

clean :
	rm -rf dist/*

test :
	pipenv run python -m pytest tests/

build-dist :
	pipenv run pyinstaller --name "AWSGlueManager" --windowed --onefile main.py

copy-icons :
	mkdir -p dist/ui
	cp -r ui/icons dist/ui

dist : build-dist copy-icons
