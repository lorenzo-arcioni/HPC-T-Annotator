import sys
from PyQt5 import  QtCore, QtGui, QtWidgets
import os
import json

from main_splash_GUI import Ui_Form
from main_GUI import Ui_MainWindow

class SplashWindow(QtWidgets.QMainWindow):

    def Warning_message(self, text):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(text)
        msg.setWindowTitle("Warning")
        msg.exec_()

    def Minimize(self):
        self.MainWindow.showMinimized()

    def Enter(self):
        self.close()
        self.MainWindow.setWindowFlags( 
            QtCore.Qt.FramelessWindowHint
        )
        self.MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.MainWindow.setFixedSize(1238, 830)
        self.MainWindow.show()
        self.Main_window_load()

    def Exit(self):
        sys.exit(0)

    def Check_all_settings(self):
        if self.x.account.currentText() != None and self.x.account.currentText() != "" and \
           self.x.number_of_processes.value() > 0 and \
           self.x.partition.currentText() != None and self.x.partition.currentText() != "" and\
           self.x.memory_per_node.value() > 0 and \
           self.x.wall_time.value() > 0 and \
           (self.x.diamond.isChecked() or self.x.blast.isChecked()) and \
           self.x.input_path.text() != None and self.x.input_path.text() != "" and \
           self.x.binary_path.text() != None and self.x.binary_path.text() != "" and \
           self.x.db_path.text() != None and self.x.db_path.text() != "" and \
           self.x.outfmt.text() != None and self.x.outfmt.text() != "":

           return True

        return False

    def Avvia(self):
        if self.Check_all_settings():
            print("Tutto Ok")
            self.Generate()
        else:
            self.Warning_message("You must fill all field!")
    
    def Main_window_load(self):
        #Main Window data load
        data = self.Get_data_from_confFile()

        if data:
            self.x.account.addItems(data["account"])
            self.x.partition.addItems(data["partition"])
            self.x.outfmt.setText(data["outfmt"])
            self.x.binary_path.setText(data["binary"])
        else:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Configuration file not found, please run the insertion script first!")
            msg.setWindowTitle("Warning")
            msg.buttonClicked.connect(self.Exit)
            msg.exec_()

    def Get_data_from_confFile(self):
        if os.path.isfile(os.getcwd() + "\\config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        else: 
            return list()

    def Generate(self):
        account   = self.x.account.currentText()
        nop       = self.x.number_of_processes.value()
        partition = self.x.partition.currentText()
        mpn       = self.x.memory_per_node.value()
        wall_time = self.x.wall_time.value()
        dmnd      = self.x.diamond.isChecked()
        in_path   = self.x.input_path.text()         
        bin_path  = self.x.binary_path.text()
        db_path   = self.x.db_path.text()
        outfmt    = self.x.outfmt.text()
        #Anaconda nel config file?

        with open("start.sh", "w") as f:
            with open("start_base.txt", "r") as base:
                f.write(base.read().format(account, partition, nop, in_path, outfmt, int(dmnd)))
                base.close()
            f.close()
        
        with open("read.py", "w") as f:
            with open("read_base.txt", "r") as base:
                f.write(base.read().format(mpn, wall_time, account, partition, bin_path, db_path))
                base.close()
            f.close()

    def __init__(self):
        super(SplashWindow, self).__init__()

        # build ui
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        #Frameless splash window
        self.setWindowFlags(
            self.windowFlags() | 
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        #Button programming splashwindow
        self.ui.enter.clicked.connect(self.Enter)
        self.ui.exit.clicked.connect(self.Exit)

        #Main Window connections
        self.MainWindow = QtWidgets.QMainWindow()
        self.x = Ui_MainWindow()
        self.x.setupUi(self.MainWindow)
        self.x.annulla.clicked.connect(self.Exit)
        self.x.avvia.clicked.connect(self.Avvia)
        self.x.btn_close.clicked.connect(self.Exit)
        self.x.btn_minimize.clicked.connect(self.Minimize)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = SplashWindow()
    main.show()
    sys.exit(app.exec_())