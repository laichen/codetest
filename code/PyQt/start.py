# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 13:37:23 2022

@author: dx.lai
"""


from PyQt5 import QtWidgets

from controller import MainWindow_controller

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec_())