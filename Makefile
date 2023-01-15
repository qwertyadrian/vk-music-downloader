generate_resources:
	pyrcc5 -compress 9 src/vkmusicd/resources/resources.qrc -o src/vkmusicd/resources/resources.py

generate_ui: generate_resources
	pyuic5 src/vkmusicd/ui_files/mainwindow.ui --import-from=vkmusicd.resources -o src/vkmusicd/gui/mainwindow_ui.py --resource-suffix=
	pyuic5 src/vkmusicd/ui_files/help.ui --import-from=vkmusicd.resources -o src/vkmusicd/gui/help.py --resource-suffix=
	pyuic5 src/vkmusicd/ui_files/about.ui --import-from=vkmusicd.resources -o src/vkmusicd/gui/about.py --resource-suffix=
	pyuic5 src/vkmusicd/ui_files/captcha.ui --import-from=vkmusicd.resources -o src/vkmusicd/gui/captcha.py --resource-suffix=

.PHONY: build
build:
	pyinstaller -F -w -i src/vkmusicd/resources/images/logo.ico src/runapp.py