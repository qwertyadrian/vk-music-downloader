generate_resources:
	pyrcc5 -compress 9 gui/audio_res.qrc -o gui/audio_res.py

generate_ui: generate_resources
	pyuic5 gui/audio.ui --import-from=gui -o gui/audio_gui.py --resource-suffix=
	pyuic5 gui/help_dialog.ui --import-from=gui -o gui/help_dialog.py --resource-suffix=
	pyuic5 gui/about_dialog.ui --import-from=gui -o gui/about_dialog.py --resource-suffix=
	pyuic5 gui/captcha_dialog.ui --import-from=gui -o gui/captcha_dialog.py --resource-suffix=

build: generate_ui
	pyinstaller -F -w -i gui/resources/images/logo.ico audio.py --additional-hooks-dir hooks