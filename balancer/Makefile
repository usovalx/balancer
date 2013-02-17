all: window_ui.py filter_ui.py

UIC=python2-pyuic4 -x

window_ui.py: window.ui
	$(UIC) $< -o $@

filter_ui.py: filter.ui
	$(UIC) $< -o $@
