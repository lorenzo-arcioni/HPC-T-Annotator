from PyQt5 import  QtCore, QtGui, QtWidgets
import os
import sys
import json

from DB_insert_GUI import Ui_MainWindow

class DB_insert(QtWidgets.QMainWindow):

    infos = """The following interface allows various information to be entered into a configuration file:
-Name of the project account on the Slurm system
-Path of the executable file
-Name of the Slurm partition or parallel queue
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

    #Exit from application
    def Exit(self):
        sys.exit(0)

    #Minimize main window
    def Minimize(self):
        self.showMinimized()
    
    #Generate information dialog
    def Info_message(self, text):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("About")
        msg.exec_()

    #Insert data in the json config file
    def Insert(self):
        data = {"accounts": [],
                "partitions": [],
                "db_paths": [],
                "bin_paths": [],
                "tools": ['blastx', 'blastp'],
                "serial_partition": ""}
                
        with open("config.json", "r") as f:
            try:
                data = json.loads(f.read())
            except Exception as e:
                print(str(e))
            f.close()
        
        if self.window.account.text()     != "" : data["accounts"].append(self.window.account.text())
        if self.window.ppartition.text()  != "" : data["partitions"].append(self.window.ppartition.text())
        if self.window.db_path.text()     != "" : data["db_paths"].append(self.window.db_path.text())
        if self.window.bin_path.text()    != "" : data["bin_paths"].append(self.window.bin_path.text())
        if self.window.outfmt.text()      != "" : data["outfmt"]    = self.window.outfmt.text()
        if self.window.anaconda.text()    != "" : data["anaconda"]  = self.window.anaconda.text()
        if self.window.spartition.text()  != "" : data["serial_partition"]  = self.window.spartition.text()

        with open("config.json", "w") as f:
            json.dump(data, f, indent = 4)
            f.close()
        
        msg = QtWidgets.QMessageBox(self)
        msg.setText("Data correctly stored!")
        msg.setWindowTitle("Success")
        msg.buttonClicked.connect(self.Exit)
        msg.exec_()
            
    def __init__(self):
        super(DB_insert, self).__init__()
        self.window = Ui_MainWindow()
        self.window.setupUi(self)

        # setting  the fixed size of window
        self.setFixedSize(540, 660)

        #Frameless splash window
        self.setWindowFlags(
            self.windowFlags() | 
            QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        #Window connections
        self.window.insert.clicked.connect(self.Insert)
        self.window.btn_close.clicked.connect(self.Exit)
        self.window.btn_minimize.clicked.connect(self.Minimize)
        self.window.btn_info.clicked.connect(lambda: self.Info_message(self.infos))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = DB_insert()
    main.show()
    sys.exit(app.exec_())