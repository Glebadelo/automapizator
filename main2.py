import os
import re
import subprocess

from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QTableWidgetItem, QHeaderView
from PyQt5 import QtCore
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from collections import OrderedDict

import resources_rc

#наборы тайлов
OB_reservoir = ('T44UPF', 'T44UNF', 'T44UNE')


#словари названий со значениями
tiles = {}
tiles['Ob_reservoir'] = OB_reservoir

zones = ('Обское водохранилище', 'Что-то там ещё') #список зон

address = 'https://scihub.copernicus.eu/dhus'
login = 'helga1289'
password = 'gordeeva120689'
product_type = 'S2MSI1C'
platform = 'Sentinel-2'
download_path = 'downloads'

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()
        path = resource_path('MainWindow.ui')
        loadUi(path, self)
        self.LDWindow_btn.clicked.connect(self.openLDWindow)

    def openLDWindow(self):
        widget.setCurrentIndex(1)



class LoadDataWindow(QDialog):
    def __init__(self):
        super(LoadDataWindow, self).__init__()
        path = resource_path('loadData.ui')
        loadUi(path, self)
        self.download_btn.clicked.connect(self.download)


        #Заполнение списка зон
        for zone in zones:
            chkBox = self.LBItem(False)
            self.zonesList.addItem(chkBox)
            chkBox.setText(zone)

        #подключение к api
        try:
            api = SentinelAPI(login, password,
                              address)  # подключение к сервису ESA предоставленя данных с КА Sentinel-1, 2, 3
            print('Подключение успешно')
        except:
            print(
                'Ошибка в введёной дате, либо Ошибка подключения к сервису ESA, проверьте адресс, логин и пароль')


    #Создание чекбокса в листбоксе
    def LBItem(self, checked):
        #QtWidgets.QListWidgetItem.is
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        if checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)
        return item


    def zoneSelected(self):
        print('gegg')
        name = self.zonesList.currentItem().text()
        if self.zonesList.currentItem().checkState == True:
            info = 'По зоне {} найдено 4 сцен'.format(name)
            self.zonesInfoList.addItem(info)
        else:
            print('rgeg')

    def returnToMW(self):
        widget.setCurrentIndex(0)

    def download(self):
        folders = os.listdir(os.getcwd() + os.sep + download_path)
        for folder in folders:



            filePath = os.getcwd() + os.sep + 'downloads' + os.sep + folder + os.sep
            print(filePath)
            scriptPath = os.getcwd() + os.sep + 'script' + os.sep + 's2_8432.xml'
            print(scriptPath)
            outputPath = os.getcwd() + os.sep + 'output' + os.sep
            print(outputPath)
            if os.system(
                    r'for /r {0} %X in (*.zip) do (gpt {1} -Pinput1="%X" -Poutput1="{2}%~nX")'.format(
                             filePath, scriptPath, outputPath)) == 0:
                print('Преобразование файлов . продукта "{}" в GeoTIFF прошло успешно')








if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    widget = QStackedWidget()

    mainWindow = MainWindow()
    widget.addWidget(mainWindow)

    loadDataWindow = LoadDataWindow()
    widget.addWidget(loadDataWindow)

    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Выход")