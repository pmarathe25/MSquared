.PHONY: install uninstall test clean

install:
	python3 setup.py -q install --user

uninstall:
	rm /home/pranav/.local/lib/python3.6/site-packages/msquared-0.0.1-py3.6.egg

test: install
	test/MSquaredTest.py

clean:
	rm -r build/ dist/ msquared.egg-info/
