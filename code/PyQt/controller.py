# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 13:35:23 2022

@author: dx.lai
"""


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog
# import cv2

from need.ui import Ui_MainWindow
import need.XrayWireCalc as xcalc

class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

    def setup_control(self):
        self.ui.LoadfileButton.clicked.connect(self.open_file)
        self.ui.CalcButton.clicked.connect(self.calc)



    def open_file(self):
        filename, filetype = QFileDialog.getOpenFileName(self,
                  "Open file",
                  "./")                 # start path
        print(filename, filetype)

        self.ui.filePath.setText(filename)
        self.ui.info.setText("loaded")

        return filename


    def calc(self):
        filename = self.ui.filePath.text()
        self.ui.info.setText("calculating...")

        xcalc.calc(filename)
        self.ui.info.setText("calculation completed")






if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec_())
