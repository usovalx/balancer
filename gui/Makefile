all: windowUi.py icons_rc.py

windowUi.py: window.ui
	python2-pyuic4 window.ui -o windowUi.py

icons_rc.py: icons.qrc
	pyrcc4 icons.qrc -o icons_rc.py
