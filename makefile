.PHONY: install uninstall test clean

install:
	python3 setup.py -q install --user

uninstall:
	rm /home/pranav/.local/lib/python3.6/site-packages/msquared-0.1.0-py3.6.egg

test: install
	python3 -m unittest discover test/ --verbose

clean:
	sudo rm -r build/ dist/ msquared.egg-info/ test/makefile
