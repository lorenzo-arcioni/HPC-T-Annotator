@echo off
python3 -m PyQt5.uic.pyuic -x main_GUI.ui -o main_GUI.py
python3 -m PyQt5.uic.pyuic -x DB_insert_GUI.ui -o DB_insert_GUI.py
python3 -m PyQt5.uic.pyuic -x main_splash_GUI.ui -o main_splash_GUI.py
pyrcc5 resources.qrc -o resources_rc.py
echo Fatto!