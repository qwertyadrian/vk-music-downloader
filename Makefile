generate_resorces:
	pyrcc5 -compress 9 gui/audio_res.qrc -o gui/audio_res.py

generate_ui: generate_resorces
	pyuic5 gui/audio.ui --import-from=gui -o gui/audio_gui.py --resource-suffix=
	pyuic5 gui/help_dialog.ui --import-from=gui -o gui/help_dialog.py --resource-suffix=
	pyuic5 gui/about_dialog.ui --import-from=gui -o gui/about_dialog.py --resource-suffix=

build: generate_ui
	pyinstaller -F -w -i src/logo.ico audio.py