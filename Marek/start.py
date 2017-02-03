import sys, os

from PyQt4 import QtCore, QtGui
from TeRi import Ui_MainWindow

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.path_txt_window.setText("Wskarz ścieżkę do pliku txt")
        self.ui.path_xml_window.setText("Wskarz ścieżkę do pliku xml")
        # Wlasne polaczenia slotow
        QtCore.QObject.connect(self.ui.browse_txt_button, QtCore.SIGNAL("clicked()"), self.file_browse_txt_file)
        QtCore.QObject.connect(self.ui.browse_xml_button, QtCore.SIGNAL("clicked()"), self.file_browse_xml_file)

    def file_browse_txt_file(self):
        browserTxt = QtGui.QFileDialog(self)
        plikTxt = open(browserTxt.getOpenFileName())
        if os.path.basename(plikTxt.name)[-4:] == '.txt' or os.path.basename(plikTxt.name)[-4:] == '.csv':
            self.ui.path_txt_window.setText(plikTxt.name)
        else:
            print("Hej")
        #print(os.path.basename(plikTxt.name)[-4:])

    def file_browse_xml_file(self):
        browserXml =QtGui.QFileDialog(self)
        plikXml = open(browserXml.getOpenFileName())
        self.ui.path_xml_window.setText(plikXml.name)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec())
