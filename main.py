import os
import re

from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QTableWidgetItem, QHeaderView
from PyQt5 import QtCore
from sentinelsat import SentinelAPI
from collections import OrderedDict

import resources_rc

work_path = os.getcwd()

#Список зон для запросов
zonesKeys = ['Ob_reservoir', 'some_zone']


#наборы тайлов
Ob_reservoir = ('44UPF', '44UNF', '44UNE')
some_zone = ('T44UPF', 'T44UNF', 'T44UNE')

#словарь названий со значением списка тайлов
tiles = {}
tiles['Ob_reservoir'] = Ob_reservoir
tiles['some_zone'] = some_zone


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

checked_items = []
class LoadDataWindow(QDialog):
    def __init__(self):
        super(LoadDataWindow, self).__init__()
        path = resource_path('loadData.ui')
        loadUi(path, self)
        self.back_btn.clicked.connect(self.returnToMW)
        self.openMap_btn.clicked.connect(self.openMap)
        self.download_btn.clicked.connect(self.download)

        self.info_label.setVisible(False) #скрытие информационной строки
        self.dwnPath_label.setText(work_path + os.sep + download_path) #вывод полного пути до каталога загрузки

        #Подключение к сервису ESA
        global api
        try:
            api = SentinelAPI(login, password, address)
        except:
            print('Ошибка в введёной дате, либо Ошибка подключения к сервису ESA, проверьте адресс, логин и пароль')
            self.info_label.setVisible(True)
            self.info_label.setText(
                'Ошибка в введёной дате, либо Ошибка подключения к сервису ESA, проверьте адресс, логин и пароль')


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

    #Функция открытия карты
    def openMap(self):
        try:
            os.startfile(work_path + os.sep + r'map.png')
        except:
            pass


    #Функция вывода информации о зоне
    def zoneClicked(self):
        sender = self.sender()
        name = sender.currentItem().text() #текст выбранного элемента
        #print(sender.currentItem().checkState())
        if sender.currentItem().checkState() == 0: #если элемент был не отмечен
            sender.currentItem().setCheckState(QtCore.Qt.Checked) #отметить
            nTiles = tiles[zonesKeys[sender.row(sender.currentItem())]]
            info = '{} - {}'.format(name, nTiles) #строка информации
            checked_items.append(zonesKeys[sender.row(sender.currentItem())])
            self.zonesInfoList.appendPlainText(info)
        elif sender.currentItem().checkState() == 2: #если элемент был отмечен
            sender.currentItem().setCheckState(QtCore.Qt.Unchecked) #снять отметку
            for item in self.zonesInfoList.findItems(name, QtCore.Qt.MatchContains): #по тексту выбранного элепента находится совпадение в списке информации
                self.zonesInfoList.takeItem(self.zonesInfoList.row(item)) # элемент удаляется
            checked_items.remove(zonesKeys[sender.row(sender.currentItem())])
            #print('удалить')
        #print(sender.currentItem().checkState())

    def returnToMW(self):
        widget.setCurrentIndex(0)

    def download(self):
        QDateFrom = self.dateFrom.date()
        dateFrom = re.sub("-","", str(QDateFrom.toPyDate()))
        print(dateFrom)

        QDateTo = self.dateTo.date()
        dateTo = re.sub("-","", str(QDateTo.toPyDate()))
        print(dateTo)

        try:
            cloudFrom = int(self.cloudFrom.text())
            cloudTo = int(self.cloudTo.text())
        except:
            cloudFrom = 0
            cloudTo = 94
        print(type(cloudFrom))
        print(cloudFrom)
        print(cloudTo)


        try:
            dict_query_kwargs = {'platformname': platform,  # словарь параметров для запроса
                                 'producttype': product_type,
                                 'date': (dateFrom, dateTo)
                                 #'cloudcoverpercentage': (cloudFrom, cloudTo)
                                 }
        except:
            self.info_label.setVisible(True)
            self.info_label.setText(
                'Ошибка запроса данных на сервисе ESA, проверьте введённый интервал дат или имя спутника и тип продукта')
            print(
                'Ошибка запроса данных на сервисе ESA, проверьте введённый интервал дат или имя спутника и тип продукта')


        for zone in checked_items:
            print(zone)
            for tile in tiles[zone]:
                products = OrderedDict()
                try:
                    print(tile)
                    kwg = dict_query_kwargs.copy()
                    kwg['tileid'] = tile
                    requests = api.query(**kwg)
                    products.update(requests)
                    print('--------')
                    #self.info_label.setText()
                except:
                    self.info_label.setVisible(True)
                    self.info_label.setText(
                        'Ошибка в введёной дате, либо Ошибка подключения к сервису ESA, проверьте адресс, логин и пароль')
                list_keys = list(products.keys())
            print('Найдено сцен в количестве {}'.format(len(products)))
            for elem in list_keys:
                print(products[elem]['title'])
                self.zonesInfoList.appendPlainText(products[elem]['title'])

            if len(products) > 0:
                if os.path.isdir(work_path + os.sep + download_path + os.sep + zone):
                    try:
                        api.download_all(products, directory_path = work_path + os.sep + download_path + os.sep + zone, max_attempts=5, checksum=True)
                        self.info_label.setVisible(True)
                        self.info_label.setText('Данные скачаны в {}', work_path + os.sep + download_path + os.sep + zone)
                    except:
                        self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
                else:
                    os.makedirs(work_path + os.sep + download_path + os.sep + zone)
                    try:
                        api.download_all(products, directory_path = work_path + os.sep + download_path + os.sep + zone, max_attempts=5, checksum=True)
                        self.info_label.setVisible(True)
                        self.info_label.setText('Данные скачаны в {}', work_path + os.sep + download_path + os.sep + zone)
                    except:
                        self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))



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