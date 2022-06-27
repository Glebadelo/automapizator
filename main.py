import os
import re

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


testTiles = ('T44UPF', 'T44UNF')
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
        self.back_btn.clicked.connect(self.returnToMW)

        # Заполнение списка зон
        for zone in zones:
            chkBox = self.LBItem(False)
            self.zonesList.addItem(chkBox)
            chkBox.setText(zone)

        self.zonesList.itemClicked.connect(self.zoneClicked) #событие нажатия элемента списка зон

    # Создание чекбокса в листбоксе
    def LBItem(self, checked):
        # QtWidgets.QListWidgetItem.is
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        if checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)
        return item

    #Функция вывода информации о зоне
    def zoneClicked(self):
        sender = self.sender()
        name = sender.currentItem().text() #текст выбранного элемента
        print(sender.currentItem().checkState())
        if sender.currentItem().checkState() == 0: #если элемент был не отмечен
            sender.currentItem().setCheckState(QtCore.Qt.Checked) #отметить
            info = 'По зоне {} найдено 4 сцен'.format(name) #строка информации
            self.zonesInfoList.addItem(info)
        elif sender.currentItem().checkState() == 2: #если элемент был отмечен
            sender.currentItem().setCheckState(QtCore.Qt.Unchecked) #снять отметку
            for item in self.zonesInfoList.findItems(name, QtCore.Qt.MatchContains): #по тексту выбранного элепента находится совпадение в списке информации
                self.zonesInfoList.takeItem(self.zonesInfoList.row(item)) # элемент удаляется
            print('удалить')
        print(sender.currentItem().checkState())

    def returnToMW(self):
        widget.setCurrentIndex(0)

    def download(self):
        dateFrom = re.sub("-","", self.dateFrom.date())
        dateTo = re.sub("-","", self.dateTo.date())
        cloudFrom = self.cloudFrom.value()
        cloudTo = self.cloudTo.value()

        try:
            dict_query_kwargs = {'platformname': platform,  # словарь параметров для запроса
                                 'producttype': product_type,
                                 'date': (dateFrom, dateTo),
                                 'cloudcoverpercentage': (cloudFrom, cloudTo)
                                 }
        except:
            print(
                'Ошибка запроса данных на сервисе ESA, проверьте введённый интервал дат или имя спутника и тип продукта')






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