import sys
from PyQt5 import  QtCore, QtGui, QtWidgets
import os
import json

from main_splash_GUI import Ui_Form
from main_GUI import Ui_MainWindow

class SplashWindow(QtWidgets.QMainWindow):

    #Reset editable field of the main window
    def Reset(self):
        self.x.number_of_processes.setValue(0)
        self.x.memory_per_node.setValue(0)
        self.x.wall_time.setValue(0)
        self.x.input_path.setText("")

    #Generate warning dialog
    def Warning_message(self, text):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(text)
        msg.setWindowTitle("Warning")
        msg.exec_()
    
    #Generate information dialog
    def Info_message(self, text):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Success")
        msg.exec_()

    #Minimize main window
    def Minimize(self):
        self.MainWindow.showMinimized()

    #Enter button actions
    def Enter(self):
        self.close()
        self.MainWindow.setWindowFlags( 
            QtCore.Qt.FramelessWindowHint
        )
        self.MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.MainWindow.setFixedSize(1238, 830)
        self.MainWindow.show()
        self.Main_window_load()

    #Exit from application
    def Exit(self):
        sys.exit(0)

    #Check that all field are filled
    def Check_all_settings(self):
        if self.x.account.currentText() != None and self.x.account.currentText() != "" and \
           self.x.number_of_processes.value() > 0 and \
           self.x.partition.currentText() != None and self.x.partition.currentText() != "" and\
           self.x.memory_per_node.value() > 0 and \
           self.x.wall_time.value() > 0 and \
           (self.x.diamond.isChecked() or self.x.blast.isChecked()) and \
           self.x.input_path.text() != None and self.x.input_path.text() != "" and \
           self.x.bin_path.currentText() != None and self.x.bin_path.currentText() != "" and \
           self.x.db_path.currentText() != None and self.x.db_path.currentText() != "" and \
           self.x.outfmt.text() != None and self.x.outfmt.text() != "":

           return True

        return False

    #Saving generated files
    def file_save(self):
        dialog = QtWidgets.QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        return folder_path

    #Start generation
    def Start(self):
        if self.Check_all_settings():
            print("Tutto Ok")
            self.Generate()
            self.Info_message("Scripts correctly generated!")
        else:
            self.Warning_message("You must fill all field!")

    #Main windo loading process    
    def Main_window_load(self):
        #Main Window data load
        data = self.Get_data_from_confFile()

        if data:
            self.x.account.addItems(data["accounts"])
            self.x.partition.addItems(data["partitions"])
            self.x.outfmt.setText(data["outfmt"])
            self.x.bin_path.addItems(data["bin_paths"])
            self.x.tools.addItems(data["tools"])
            self.x.db_path.addItems(data["db_paths"])

            self.x.db_path.setEditable(True)
            self.x.bin_path.setEditable(True)
        else:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Configuration file not found, please run the insertion script first!")
            msg.setWindowTitle("Warning")
            msg.buttonClicked.connect(self.Exit)
            msg.exec_()

    #Get all data from config json file
    def Get_data_from_confFile(self):
        if os.path.isfile(os.getcwd() + "/config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        else: 
            return list()

    #Generate the scripts
    def Generate(self):
        dir = self.file_save()
        account   = self.x.account.currentText()
        nop       = self.x.number_of_processes.value()
        partition = self.x.partition.currentText()
        mpn       = self.x.memory_per_node.value()
        wall_time = self.x.wall_time.value()
        dmnd      = self.x.diamond.isChecked()
        in_path   = self.x.input_path.text()         
        bin_path  = self.x.bin_path.currentText()
        db_path   = self.x.db_path.currentText()
        outfmt    = self.x.outfmt.text()
        tool      = self.x.tools.currentText()
        #Anaconda nel config file?

        with open(dir + "/start.sh", "w") as f:
            with open("Bases/start_base.txt", "r") as base:
                f.write(base.read().format(account, partition, nop, in_path, outfmt, int(dmnd)))
                base.close()
            f.close()
        
        with open(dir + "/read.py", "w") as f:
            with open("Bases/read_base.txt", "r") as base:
                f.write(base.read().format(mpn, wall_time, account, partition, bin_path, db_path, tool))
                base.close()
            f.close()

    #Enable/Disable tools ComboBox
    def En_dis_functions(self):

        if self.x.diamond.isChecked():
            self.x.tools.setEnabled(True)
        else:
            self.x.tools.setEnabled(False)

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
        self.x.reset.clicked.connect(self.Reset)
        self.x.start.clicked.connect(self.Start)
        self.x.btn_close.clicked.connect(self.Exit)
        self.x.btn_minimize.clicked.connect(self.Minimize)
        self.x.diamond.clicked.connect(self.En_dis_functions)
        self.x.blast.clicked.connect(self.En_dis_functions)
        self.x.blast.setChecked(True)
        self.x.tools.setEnabled(False)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = SplashWindow()
    main.show()
    sys.exit(app.exec_())