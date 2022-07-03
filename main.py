import datetime
import os
import re
import shutil
import time

from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from sentinelsat import SentinelAPI
from collections import OrderedDict
from datetime import date

import resources_rc

work_path = os.getcwd()

#Список зон для запросов
zonesKeys = ['Ob_reservoir', 'Baikal_lake']


#наборы тайлов
Ob_reservoir = ('44UPF', '44UNF', '44UNE')
Baikal_lake = ('49UCB', '49UDB', '49UCA', '49UCV')

#словарь названий со значением списка тайлов
tiles = {}
tiles['Ob_reservoir'] = Ob_reservoir
tiles['Baikal_lake'] = Baikal_lake


zones = ('Обское водохранилище', 'Озеро Байкал') #список зон


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



class copyFiles(QThread):
    def __init__(self):
        QThread.__init__(self)


    def stop(self):
        self.terminate()
        self.exit()
        self.quit()

    def __del__(self):
        self.wait()

    def copy(self):
        loadDataWindow.info_label.setVisible(True)
        print('Копирование в процессе...')
        loadDataWindow.info_label.setText('Копирование в процессе...')
        folders = os.listdir(work_path + os.sep + download_path)
        print(folders)
        a = str(datetime.date.today())
        dateFolder = a.replace('-', '')
        print(dateFolder)

        if os.path.isdir('D:/folder/' + dateFolder):
            for folder in folders:
                files = os.listdir(work_path + os.sep + download_path + os.sep + folder)
                for file in files:
                    shutil.copy(work_path + os.sep + download_path + os.sep + folder + os.sep + file,
                                'D:/folder/' + dateFolder)
        else:
            os.makedirs('D:/folder/' + dateFolder)
            for folder in folders:
                files = os.listdir(work_path + os.sep + download_path + os.sep + folder)
                for file in files:
                    shutil.copy(work_path + os.sep + download_path + os.sep + folder + os.sep + file,
                                'D:/folder/' + dateFolder)
        print('Копирование завершено')
        loadDataWindow.info_label.setText('Завершено')

class downloadProducts(QThread):
    def __init__(self, products, path, zone):
        QThread.__init__(self)
        self.products = products
        self.path = path
        self.zone = zone

    def __del__(self):
        self.wait()

    def stop(self):
        self.terminate()
        self.exit()
        self.quit()

    def _download(self, products, path, zone):
        loadDataWindow.download_btn.setEnabled(False)
        if len(products) > 0:
            if os.path.isdir(path):
                try:
                    loadDataWindow.info_label.setText('Данные загружаются. Ожидайте')
                    api.download_all(products, directory_path = work_path + os.sep + download_path + os.sep + zone, max_attempts=5, checksum=True)
                    loadDataWindow.done()
                    print('Данные скачаны в {}',
                          work_path + os.sep + download_path + os.sep + zone)
                    loadDataWindow.info_label.setText('Данные скачаны в {}'.
                                                      format(work_path + os.sep + download_path))

                except:
                    print('Не удалось скачать данные для "{}"'.format(zone))
                    loadDataWindow.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
            else:
                os.makedirs(path)
                try:
                    loadDataWindow.info_label.setText('Данные загружаются. Ожидайте')
                    api.download_all(products, directory_path=path,
                                     max_attempts=5, checksum=True)
                    loadDataWindow.done()
                    loadDataWindow.info_label.setText('Данные скачаны в {}'.
                                                      format(work_path + os.sep + download_path))
                    print('Данные скачаны в {}',
                          work_path + os.sep + download_path + os.sep + zone)

                except:
                    print('Не удалось скачать данные для "{}"'.format(zone))
                    loadDataWindow.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
        loadDataWindow.download_btn.setEnabled(True)


    def run(self):
        self._download(self.products, self.path, self.zone)

checked_items = []
class LoadDataWindow(QDialog):
    def __init__(self):
        super(LoadDataWindow, self).__init__()
        path = resource_path('loadData.ui')
        loadUi(path, self)
        self.back_btn.clicked.connect(self.returnToMW)
        self.openMap_btn.clicked.connect(self.openMap)
        self.download_btn.clicked.connect(self.download)
        self.copy_btn.clicked.connect(self.copy_files)

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
        item.setFlags(Qt.ItemIsEnabled)
        if checked:
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)
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
            sender.currentItem().setCheckState(Qt.Checked) #отметить
            nTiles = tiles[zonesKeys[sender.row(sender.currentItem())]]
            info = '{} - {}'.format(name, nTiles) #строка информации
            checked_items.append(zonesKeys[sender.row(sender.currentItem())])
            print(checked_items)
            self.zonesInfoList.appendPlainText(info)
        elif sender.currentItem().checkState() == 2: #если элемент был отмечен
            sender.currentItem().setCheckState(Qt.Unchecked) #снять отметку
            checked_items.remove(zonesKeys[sender.row(sender.currentItem())])
            print(checked_items)

            self.zonesInfoList.clear()
            for item in checked_items:
                print('---{}---'.format(item))
                name = zones[zonesKeys.index(item)]
                print(name)
                #print(zonesKeys[item])
                print(tiles[item])
                nTiles = tiles[item]
                print(nTiles)
                info = '{} - {}'.format(name, nTiles)
                self.zonesInfoList.appendPlainText(info)
            # for item in self.zonesInfoList.findItems(name, Qt.MatchContains): #по тексту выбранного элепента находится совпадение в списке информации
            #     self.zonesInfoList.takeItem(self.zonesInfoList.row(item)) # элемент удаляется



            #print('удалить')
        #print(sender.currentItem().checkState())

    #функция возвращения на стартовое меню
    def returnToMW(self):
        widget.setCurrentIndex(0)


    # def dateInfo(self):
    #     QDateFrom = self.dateFrom.date()  # дата начала в QDate формате
    #     dateFrom = re.sub("-", "", str(QDateFrom.toPyDate()))  # перевод QDate вид в yyyymmdd формат
    #     print(dateFrom)
    #
    #     QDateTo = self.dateTo.date()
    #     dateTo = re.sub("-", "", str(QDateTo.toPyDate()))
    #     print(dateTo)
    #
    #     date = [dateFrom, dateTo]
    #     return date
    #
    # def cloudInfo(self):
    #     try:
    #         cloudFrom = int(self.cloudFrom.text())  # значения облачности
    #         cloudTo = int(self.cloudTo.text())
    #     except:
    #         cloudFrom = 0  # при пустых значениях устанавливаются значения по умолчанию
    #         cloudTo = 94
    #         # print(type(cloudFrom))
    #     print(cloudFrom)
    #     print(cloudTo)
    #
    #     cloud = [cloudFrom, cloudTo]
    #     return cloud

    # def zonesDownload(self, dict_query_kwargs):
    #     for zone in checked_items:
    #         print(zone)
    #         for tile in tiles[zone]:
    #             products = OrderedDict()
    #             try:
    #                 print(tile)
    #                 kwg = dict_query_kwargs.copy()
    #                 kwg['tileid'] = tile
    #                 requests = api.query(**kwg)
    #                 products.update(requests)
    #                 print('--------')
    #                 #self.info_label.setText()
    #             except:
    #                 self.info_label.setVisible(True)
    #                 self.info_label.setText(
    #                     'Ошибка в введёной дате, либо Ошибка подключения к сервису ESA, проверьте адресс, логин и пароль')
    #             list_keys = list(products.keys())
    #         print('Найдено сцен в количестве {}'.format(len(products)))
    #         for elem in list_keys:
    #             print(products[elem]['title'])
    #             self.zonesInfoList.appendPlainText(products[elem]['title'])
    #             prod_inf = [products, zone]
    #         return prod_inf
    #         #self.zoneDownload(products, zone)

    # def zoneDownload(self, products, zone):
    #     if len(products) > 0:
    #         if os.path.isdir(work_path + os.sep + download_path + os.sep + zone):
    #             try:
    #                 api.download_all(products, directory_path=work_path + os.sep + download_path + os.sep + zone,
    #                                  max_attempts=5, checksum=True)
    #                 self.info_label.setVisible(True)
    #                 self.info_label.setText(
    #                     'Данные скачаны в {}'.format(work_path + os.sep + download_path + os.sep + zone))
    #                 print('Данные скачаны в {}',
    #                       work_path + os.sep + download_path + os.sep + zone)
    #             except:
    #                 self.info_label.setVisible(True)
    #                 self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
    #                 print('Не удалось скачать данные для "{}"'.format(zone))
    #         else:
    #             os.makedirs(work_path + os.sep + download_path + os.sep + zone)
    #             try:
    #                 api.download_all(products, directory_path=work_path + os.sep + download_path + os.sep + zone,
    #                                  max_attempts=5, checksum=True)
    #                 self.info_label.setVisible(True)
    #                 self.info_label.setText(
    #                     'Данные скачаны в {}'.format(work_path + os.sep + download_path + os.sep + zone))
    #                 print('Данные скачаны в {}',
    #                       work_path + os.sep + download_path + os.sep + zone)
    #             except:
    #                 self.info_label.setVisible(True)
    #                 self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
    #                 print('Не удалось скачать данные для "{}"'.format(zone))



    def copy_files(self):
        self.info_label.setVisible(True)
        print('Копирование в процессе...')
        self.info_label.setText('Копирование в процессе...')
        folders = os.listdir(work_path + os.sep + download_path)
        print(folders)
        a = str(datetime.date.today())
        dateFolder = a.replace('-', '')
        print(dateFolder)

        if os.path.isdir('D:/folder/' + dateFolder):
            for folder in folders:
                files = os.listdir(work_path + os.sep + download_path + os.sep + folder)
                for file in files:
                    shutil.copy(work_path + os.sep + download_path + os.sep + folder + os.sep + file,
                                'D:/folder/' + dateFolder)
        else:
            os.makedirs('D:/folder/' + dateFolder)
            for folder in folders:
                files = os.listdir(work_path + os.sep + download_path + os.sep + folder)
                for file in files:
                    shutil.copy(work_path + os.sep + download_path + os.sep + folder + os.sep + file,
                                'D:/folder/' + dateFolder)
        print('Копирование завершено')
        self.info_label.setText('Копирование завершено')


    #функция загрузки
    def download(self):

        self.info_label.setVisible(True)
        # self.info_label.setText('Идёт загрузка. Ожидайте')


        #date = self.dateInfo()
        # self.download_btn.setEnabled(False)  # отключение кнопки загрузки
        # self.stop_btn.setEnabled(True)

        QDateFrom = self.dateFrom.date() #дата начала в QDate формате
        dateFrom = re.sub("-","", str(QDateFrom.toPyDate())) #перевод QDate вид в yyyymmdd формат
        print(dateFrom)

        QDateTo = self.dateTo.date()
        dateTo = re.sub("-","", str(QDateTo.toPyDate()))
        print(dateTo)

        #cloud = self.cloudInfo()
        try:
            cloudFrom = int(self.cloudFrom.text()) #значения облачности
            cloudTo = int(self.cloudTo.text())
        except:
            cloudFrom = 0 #при пустых значениях устанавливаются значения по умолчанию
            cloudTo = 94
        #print(type(cloudFrom))
        print(cloudFrom)
        print(cloudTo)

        try:
            dict_query_kwargs = {'platformname': platform,  # словарь параметров для запроса
                                 'producttype': product_type,
                                 'date': (dateFrom, dateTo),
                                 'cloudcoverpercentage': (cloudFrom, cloudTo)
                                 }
        except:
            self.info_label.setVisible(True)
            self.info_label.setText(
                'Ошибка запроса данных на сервисе ESA, проверьте введённый интервал дат или имя спутника и тип продукта')
            print(
                'Ошибка запроса данных на сервисе ESA, проверьте введённый интервал дат или имя спутника и тип продукта')

        #prod_info = self.zonesDownload(dict_query_kwargs)
        # self.info_label.setText('Идёт загрузка. Ожидайте')
        # path = work_path + os.sep + download_path + os.sep + prod_info[1]
        # self.downloadProduct = downloadProducts(prod_info[0], path, prod_info[1])
        # self.downloadProduct.setTerminationEnabled(True)
        # self.downloadProduct.start() #старт потока

        #перебор выбранных зон для скачивания
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
                time.sleep(1)

            path = work_path + os.sep + download_path + os.sep + zone
            try: #создание объекта класса загрузки файлов зоны
                self.downloadProduct = downloadProducts(products, path, zone)
                self.downloadProduct.setTerminationEnabled(True)
                self.downloadProduct.start() #старт потока
                self.connect(self.downloadProduct, pyqtSignal("finished(True)"), self.done)
            except:
                self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))

            self.info_label.setVisible(True)
            # self.info_label.setText(
            #     'Данные скачаны в {}'.format(work_path + os.sep + download_path + os.sep + zone))

            # if len(products) > 0:
            #     if os.path.isdir(work_path + os.sep + download_path + os.sep + zone):
            #         try:
            #             api.download_all(products, directory_path = work_path + os.sep + download_path + os.sep + zone, max_attempts=5, checksum=True)
            #             self.info_label.setVisible(True)
            #             self.info_label.setText('Данные скачаны в {}'.format(work_path + os.sep + download_path + os.sep + zone))
            #             time.sleep(4)
            #             print('Данные скачаны в {}',
            #                                     work_path + os.sep + download_path + os.sep + zone)
            #         except:
            #             self.info_label.setVisible(True)
            #             self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
            #             print('Не удалось скачать данные для "{}"'.format(zone))
            #     else:
            #         os.makedirs(work_path + os.sep + download_path + os.sep + zone)
            #         try:
            #             api.download_all(products, directory_path = work_path + os.sep + download_path + os.sep + zone, max_attempts=5, checksum=True)
            #             self.info_label.setVisible(True)
            #             self.info_label.setText(
            #                 'Данные скачаны в {}'.format(work_path + os.sep + download_path + os.sep + zone))
            #             print('Данные скачаны в {}',
            #                   work_path + os.sep + download_path + os.sep + zone)
            #         except:
            #             self.info_label.setVisible(True)
            #             self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
            #             print('Не удалось скачать данные для "{}"'.format(zone))

    def stopDownload(self):
        self.downloadProduct.stop()
        self.downloadProduct.wait()

    def done(self):
        self.download_btn.setEnabled(True)

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