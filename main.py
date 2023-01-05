import sys
from PyQt5 import  QtCore, QtGui, QtWidgets
import os
import json
import DB_insert
import tarfile
import shutil

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

    #Enter button actions
    def Enter(self):
        #self.close()
        self.MainWindow.setWindowFlags( 
            QtCore.Qt.FramelessWindowHint
        )
        self.MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.MainWindow.setFixedSize(1238, 900)
        self.MainWindow.show()
        self.Main_window_load()
    
    #Conf button actions
    def Conf(self):
        #self.close()
        self.ConfWindow.setWindowFlags( 
            QtCore.Qt.FramelessWindowHint
        )
        self.ConfWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ConfWindow.setFixedSize(540, 660)
        self.ConfWindow.show()

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
           self.x.outfmt.text() != None and self.x.outfmt.text() != "" and \
           self.x.serial_partition.text().split(":")[1] != '' and \
           self.x.anaconda.text().split(":")[1] != '':

           return True

        return False

    #Saving generated files
    def File_save(self):
        dialog = QtWidgets.QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        return folder_path

    #Start generation
    def Start(self):
        if self.Check_all_settings():
            self.Generate()
        else:
            self.Warning_message("You must fill all field!")

    #Main windo loading process    
    def Main_window_load(self):
        #Main Window data load
        data = self.Get_data_from_confFile()

        if data["accounts"] != [] and data["partitions"] != []:
            self.x.account.addItems(data["accounts"])
            self.x.partition.addItems(data["partitions"])
            self.x.outfmt.setText(data["outfmt"])
            self.x.bin_path.addItems(data["bin_paths"])
            self.x.tools.addItems(data["tools"])
            self.x.db_path.addItems(data["db_paths"])
            if data["anaconda"]:
                self.x.anaconda.setText("Valid Anaconda module: " + data["anaconda"])
                self.x.anaconda.setStyleSheet("color: green;")
            if data["serial_partition"]:
                self.x.serial_partition.setText("Valid partition: " + data["serial_partition"])
                self.x.serial_partition.setStyleSheet("color: green;")

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
        dir       = self.File_save()
        if dir != None and dir != "":
            account          = self.x.account.currentText()
            nop              = self.x.number_of_processes.value()
            partition        = self.x.partition.currentText()
            mpn              = self.x.memory_per_node.value()
            wall_time        = self.x.wall_time.value()
            dmnd             = self.x.diamond.isChecked()
            in_path          = self.x.input_path.text()         
            bin_path         = self.x.bin_path.currentText()
            db_path          = self.x.db_path.currentText()
            outfmt           = self.x.outfmt.text()
            tool             = self.x.tools.currentText()
            threads          = self.x.threads.value()
            anaconda         = self.x.anaconda.text().split(":")[1]
            pa_env           = self.x.pa_env.isChecked()
            serial_partition = self.x.serial_partition.text().split(":")[1]

            with open(dir + "/start.sh", "w") as f:
                with open("Bases/start_base.txt", "r") as base:
                    f.write(base.read().format(account, serial_partition, anaconda, in_path, nop, in_path, outfmt, int(dmnd), tool, bin_path, db_path, anaconda))
                    base.close()
                f.close()

            with open(dir + "/script.sh", "w") as f:
                with open("Bases/script_base.txt", "r") as base:
                    f.write(base.read().format(account, serial_partition))
                    base.close()
                f.close()
            
            with open(dir + "/read.py", "w") as f:
                with open("Bases/read_base.txt", "r") as base:
                    diamond_options = open("Bases/diamond_additional_options.txt", "r").read().replace("\n", "")
                    blast_options   = open("Bases/blast_additional_options.txt", "r").read().replace("\n", "")
                    f.write(base.read().format(outfmt, int(dmnd), bin_path, db_path, tool, mpn, wall_time, threads, account, partition, diamond_options, blast_options))
                    base.close()
                f.close()

            if pa_env:
                shutil.copy("pa_env.tar.gz", dir)

            shutil.copy("checker.sh", dir)
            shutil.copy("cancel.sh", dir)
            shutil.copy("monitor.sh", dir)
            #shutil.copy("script.sh", dir)
            shutil.copy("slurm_error_checker.sh", dir)
            shutil.copy("time_calculator.py", dir)

            tmp = os.getcwd()

            os.chdir(dir)

            file_obj= tarfile.open("hpc_annotator.tar.gz","w:gz")
    
            #Add other files to tar file

            if pa_env:
                file_obj.add("pa_env.tar.gz")

            file_obj.add("read.py")
            file_obj.add("start.sh")
            file_obj.add("checker.sh")        
            file_obj.add("cancel.sh")
            file_obj.add("monitor.sh")
            file_obj.add("script.sh")
            file_obj.add("slurm_error_checker.sh")
            file_obj.add("time_calculator.py")    

            #close file
            file_obj.close()

            if pa_env:
                os.remove("pa_env.tar.gz")

            os.remove("checker.sh")
            os.remove("cancel.sh")
            os.remove("monitor.sh")
            os.remove("script.sh")
            os.remove("slurm_error_checker.sh")
            os.remove("time_calculator.py")
            os.remove("read.py")
            os.remove("start.sh")

            os.chdir(tmp)

            self.Info_message("Scripts correctly generated!")
            self.MainWindow.close()

    #Insert data in the json config file
    def Insert(self):
        data = {"accounts": [],
                "partitions": [],
                "db_paths": [],
                "bin_paths": [],
                "tools": ['blastx', 'blastp'],
                "outfmt": "",
                "anaconda": "",
                "serial_partition": ""}
                
        with open("config.json", "r") as f:
            try:
                data = json.loads(f.read())
            except Exception as e:
                print(str(e))
            f.close()
        
        if self.y.account.text()     != "" : data["accounts"].append(self.y.account.text())
        if self.y.ppartition.text()  != "" : data["partitions"].append(self.y.ppartition.text())
        if self.y.db_path.text()     != "" : data["db_paths"].append(self.y.db_path.text())
        if self.y.bin_path.text()    != "" : data["bin_paths"].append(self.y.bin_path.text())
        if self.y.outfmt.text()      != "" : data["outfmt"]    = self.y.outfmt.text()
        if self.y.anaconda.text()    != "" : data["anaconda"]  = self.y.anaconda.text()
        if self.y.spartition.text()  != "" : data["serial_partition"]  = self.y.spartition.text()

        with open("config.json", "w") as f:
            json.dump(data, f, indent = 4)
            f.close()
        
        msg = QtWidgets.QMessageBox(self)
        msg.setText("Data correctly stored!")
        msg.setWindowTitle("Success")
        msg.buttonClicked.connect(self.ConfWindow.close)
        msg.exec_()

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
            QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        infos = """The following interface allows various information to be entered into a configuration file:
-Name of the project account on the Slurm system
-Path of the executable file
-Name of the Slurm parallel partition or queue
-Name of the Slurm serial partition or queue
-BLAST-like output format
-Path to the database of interest
-Name of the Slurm Anaconda module to be loaded on the HPC machine
Through this interface, it is possible to enter permanent and useful information when using the main interface.
It is also possible to make an entry with partial information, and each time an entry is made, the data of previous entries are not overwritten.

For example, for the addition of the NR, TrEMBL and SwissProt database, it is sufficient to enter the location address in the NR database filesystem in the 'Database path' field:
        /g100_scratch/home/BANCHE_OMOLOGY/NR/nr
Then click insert, write the second path
        /g100_scratch/home/BANCHE_OMOLOGY/TR/tr
Then click insert, write the third path
        /g100_scratch/home/BANCHE_OMOLOGY/NR/sp
And finally click insert again!

Now, in the main panel, we'll have the three databases in a combo_box."""

        #Button programming splashwindow
        self.ui.enter.clicked.connect(self.Enter)
        self.ui.exit.clicked.connect(self.Exit)
        self.ui.config.clicked.connect(self.Conf)

        #Main Window connections
        self.MainWindow = QtWidgets.QMainWindow()
        self.x = Ui_MainWindow()
        self.x.setupUi(self.MainWindow)
        self.x.reset.clicked.connect(self.Reset)
        self.x.start.clicked.connect(self.Start)
        self.x.btn_close.clicked.connect(self.MainWindow.close)
        self.x.btn_minimize.clicked.connect(self.MainWindow.showMinimized)
        self.x.diamond.clicked.connect(self.En_dis_functions)
        self.x.blast.clicked.connect(self.En_dis_functions)
        self.x.blast.setChecked(True)
        self.x.tools.setEnabled(False)

        #Conf panel connections
        self.ConfWindow = QtWidgets.QMainWindow()
        self.y = DB_insert.Ui_MainWindow()
        self.y.setupUi(self.ConfWindow)
        self.y.insert.clicked.connect(self.Insert)
        self.y.btn_close.clicked.connect(self.ConfWindow.close)
        self.y.btn_minimize.clicked.connect(self.ConfWindow.showMinimized)
        self.y.btn_info.clicked.connect(lambda: self.Info_message(infos))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = SplashWindow()
    main.show()
    sys.exit(app.exec_())