import datetime
import os
import re
import shutil
import time

from PyQt5.QtGui import QIntValidator, QIcon, QPixmap, QPainter, QColor
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from sentinelsat import SentinelAPI
from collections import OrderedDict
from datetime import date
import resources_rc


#Работа с конфигкрационным файлом

try:                                                                   # Модуль для работы с файлами конфигурации
    import configparser
except ImportError:
    import ConfigParser as configparser

work_path = os.getcwd()

file_settings = r'Config.ini'

#Список зон для запросов
zonesKeys = ['Ob_reservoir', 'Baikal_lake']


#наборы тайлов
#Ob_reservoir = ('44UPF', '44UNF', '44UNE')
# Baikal_lake = ('49UCB', '49UDB', '49UCA', '49UCV')

tiles = [('44UPF', '44UNF', '44UNE'), ('49UCB', '49UDB', '49UCA', '49UCV')]
print('tiles до = {}'.format(tiles))
print('tiles до = {}'.format(type(tiles)))
# словарь названий со значением списка тайлов
zoneTiles = {}
for zone in zonesKeys:
    zoneTiles[zone] = tiles[zonesKeys.index(zone)]
print(zoneTiles)



zones = ('Обское водохранилище', 'Озеро Байкал') #список зон


address = 'https://scihub.copernicus.eu/dhus'
login = 'helga1289'
password = 'gordeeva120689'
product_type = 'S2MSI1C'
platform = 'Sentinel-2'
download_path = 'downloads'
path_archive = 'D:/PycharmProjects/automapizator/folder'

list_settings = []


def create_config_SAD(path):
    """Функция создания файла конфигурации,
       с опциями "по умолчанию", которые "зашиты"
       в программе, если файл Config.ini
       будет отсутствовать
    """
    try:
        config = configparser.ConfigParser()  # Создаём файл конфигурации
        config.add_section('Settings_ESA')
        config.add_section('Zones_names')
        config.add_section('Zones_tiles')
        config.add_section('Settings_paths')  # Создаём секцию [Settings_paths]

        # Добавляем опций в секцию
        config.set('Settings_ESA', 'address', 'https://scihub.copernicus.eu/dhus')  # адрес сервиса Sentinel-1-2-3
        config.set('Settings_ESA', 'login', 'helga1289')  # логин
        config.set('Settings_ESA', 'password', 'gordeeva120689')  # пароль
        config.set('Settings_ESA', 'platform', 'Sentinel-2')  # имя платформы
        config.set('Settings_ESA', 'product_type', 'S2MSI1C')  # тип продукта
        config.set('Zones_names', 'zones', 'Обское_водохранилище Озеро_Байкал') # список имён зон для отображения
        config.set('Zones_names', 'zonesKeys', 'Ob_reservoir Baikal_lake')
        config.set('Zones_tiles', 'Ob_reservoir', '44UPF 44UNF 44UNE')      # список имён тайлов зоны
        config.set('Zones_tiles', 'Baikal_lake', '49UCB 49UDB 49UCA 49UCV')  # список имён тайлов зоны
        config.set('Settings_paths', 'path_downloads','downloads')  # каталог для скаченных файлов
        config.set('Settings_paths', 'path_archive',
                    'D:/PycharmProjects/automapizator/folder')

        with open(path,
                  "w") as config_file:  # Открывает файл (или создаёт, если отсутствует) для записи в режиме write only
            config.write(config_file)
        print('Файл конфигурации успешно создан: {}'.format(path))
    except:
        print('Ошибка создания файла конфигурации. Не удалось создать файл конфигурации')


def get_config_SAD(path):
    '''Функция получения объекта файла конфигурации
    '''

    try:
        if not os.path.exists(path):  # если файл конфигурации не найден,
            create_config_SAD(path)  # то файл конфигурации создатся, используя настройки по умолчанию

        config = configparser.ConfigParser()
        config.read(path)  # считываем файл конфигурации

        return config

    except:
        print('Ошибка доступа к файлу конфигурации')


def get_settings_config_SAD(path, section, settings):
    '''Функция получения информации из опций файла конфигурации
    '''
    config = get_config_SAD(path)  # получение файла конфигурации
    value_section = config.get(section, settings)  # получение значения опции из секции

    if section == 'list_tiles' or section == 'Zones_names':
        return value_section.split(' ')  # преобразуем строку в список, разделяя элементы по пробелам
    else:
        return value_section  # возвращает опцию в виде строки

def get_tiles_config_SAD(path, section):
    tiles = []
    config = get_config_SAD(path)
    for zone in config[section]:
        value_section = config.get(section, zone)
        tiles.append(value_section.split(' '))
    return tiles

def create_list_settings(path):
    ''' Функция заполнения списка данными из файла конфигурации.
         В случае отсутсвия доступа к каталогу с файлом конфигурации -
         список будет сформирован из значений по умолчанию.
    '''

    if os.path.exists(os.path.split(path)[
                          0]):  # проверка: существует ли данный путь при помощи метода split получаем множество из двух элементов: пути и файла
        try:
            list_settings.append(get_settings_config_SAD(path, 'Settings_ESA', 'address', ))
            list_settings.append(get_settings_config_SAD(path, 'Settings_ESA', 'login', ))
            list_settings.append(get_settings_config_SAD(path, 'Settings_ESA', 'password', ))
            list_settings.append(get_settings_config_SAD(path, 'Settings_ESA', 'platform'))
            list_settings.append(get_settings_config_SAD(path, 'Settings_ESA', 'product_type'))
            list_settings.append(get_settings_config_SAD(path, 'Zones_names', 'zones'))
            list_settings.append(get_settings_config_SAD(path, 'Zones_names', 'zonesKeys'))
            list_settings.append(get_tiles_config_SAD(path, 'Zones_tiles'))
            list_settings.append(get_settings_config_SAD(path, 'Settings_paths', 'path_downloads'))
            list_settings.append(get_settings_config_SAD(path, 'Settings_paths', 'path_archive'))
            print('Файл конфигурации {} успешно прочтён'.format(path))
        except:
            print(
                'Ошибка конфигурации. Не удалось создать файл конфигурации, будут применены параметры по умолчанию')



create_list_settings(work_path + os.sep + file_settings)
address = list_settings[0]
login = list_settings[1]
password = list_settings[2]
platform = list_settings[3]
product_type = list_settings[4]
zones = list_settings[5]
zonesKeys = list_settings[6]
tiles = list_settings[7]
download_path = list_settings[8]
path_archive = list_settings[9]
print('tiles после = {}'.format(tiles))
print('tiles после = {}'.format(type(tiles)))

zoneTiles = {}
for zone in zonesKeys:
    zoneTiles[zone] = tiles[zonesKeys.index(zone)]
print(zoneTiles)


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

# class MainWindow(QDialog):
#
#     def __init__(self):
#         super(MainWindow, self).__init__()
#         path = resource_path('MainWindow.ui')
#         loadUi(path, self)
#         self.LDWindow_btn.clicked.connect(self.openLDWindow)
#
#     def openLDWindow(self):
#         widget.setCurrentIndex(1)

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

        if os.path.isdir('D:/PycharmProjects/' + dateFolder):
            for folder in folders:
                files = os.listdir(work_path + os.sep + download_path + os.sep + folder)
                for file in files:
                    shutil.copy(work_path + os.sep + download_path + os.sep + folder + os.sep + file,
                                'D:/folder' + os.sep + dateFolder)
        else:
            os.makedirs('D:/folder/' + dateFolder)
            for folder in folders:
                files = os.listdir(work_path + os.sep + download_path + os.sep + folder)
                for file in files:
                    shutil.copy(work_path + os.sep + download_path + os.sep + folder + os.sep + file,
                                'D:/folder' + os.sep + dateFolder)
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
        loadDataWindow.copy_btn.setEnabled(False)
        if len(products) > 0:
            if os.path.isdir(path):
                try:
                    loadDataWindow.info_label.setText("")
                    loadDataWindow.info_label.setStyleSheet("color: rgba(71, 230, 98, 90)")
                    loadDataWindow.info_label.setText('Данные загружаются. Ожидайте')
                    api.download_all(products, directory_path = work_path + os.sep + download_path + os.sep + zone, max_attempts=5, checksum=True)
                    loadDataWindow.done()
                    print('Данные скачаны в {}',
                          work_path + os.sep + download_path + os.sep + zone)
                    loadDataWindow.info_label.setText('Данные скачаны в {}'.
                                                      format(work_path + os.sep + download_path))

                except:
                    loadDataWindow.info_label.setStyleSheet("color: rgb(255, 6, 60)")
                    print('Не удалось скачать данные для "{}"'.format(zone))
                    loadDataWindow.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
            else:
                os.makedirs(path)
                try:
                    loadDataWindow.info_label.setStyleSheet("color: rgba(71, 230, 98, 90)")
                    loadDataWindow.info_label.setText('Данные загружаются. Ожидайте')
                    api.download_all(products, directory_path=path,
                                     max_attempts=5, checksum=True)
                    loadDataWindow.done()
                    loadDataWindow.info_label.setText('Данные скачаны в {}'.
                                                      format(work_path + os.sep + download_path))
                    print('Данные скачаны в {}',
                          work_path + os.sep + download_path + os.sep + zone)

                except:
                    loadDataWindow.info_label.setStyleSheet("color: rgb(255, 6, 60)")
                    print('Не удалось скачать данные для "{}"'.format(zone))
                    loadDataWindow.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))

            if loadDataWindow.geoTiff_CB.checkState() == 2:
                #folders = os.listdir(os.getcwd() + os.sep + download_path)
                for folder in checked_items:
                    print(folder)

                    outputPath = os.getcwd() + os.sep + 'outputTIFF' + os.sep + folder + os.sep
                    print(outputPath)
                    if os.path.isdir(outputPath) == False:
                        os.makedirs(outputPath)

                    filePath = os.getcwd() + os.sep + 'downloads' + os.sep + folder + os.sep
                    print(filePath)

                    if loadDataWindow.RB_B8.isChecked():
                        scriptPath = os.getcwd() + os.sep + 'script' + os.sep + 's2_8432.xml'
                        type = '_B2B3BB4B8'
                    else:
                        scriptPath = os.getcwd() + os.sep + 'script' + os.sep + 's2_bands_resample.xml'
                        type = '_B2B3BB4B8B11'
                    print(scriptPath)

                    loadDataWindow.info_label.setStyleSheet("color: rgba(71, 230, 98, 90)")
                    loadDataWindow.info_label.setText('Процесс преобразования файлов в GeoTIFF запущен')
                    if os.system(
                            r'for /r {0} %X in (*.zip) do (gpt {1} -Pinput1="%X" -Poutput1="{2}%~nX{3}")'.format(
                                filePath, scriptPath, outputPath, type)) == 0:
                        print('Преобразование файлов в GeoTIFF прошло успешно')
                        loadDataWindow.info_label.setText('Преобразование файлов в GeoTIFF прошло успешно')
        loadDataWindow.download_btn.setEnabled(True)
        loadDataWindow.copy_btn.setEnabled(True)

        if loadDataWindow.images_CB.checkState() == 2:
            loadDataWindow.download_btn.setEnabled(False)
            loadDataWindow.copy_btn.setEnabled(False)
            self.info_label.setStyleSheet("color: rgba(71, 230, 98, 90)")
            loadDataWindow.info_label.setText('Процесс создания изображения запущен')

            arcpy = os.getcwd() + os.sep + 'ArcGIS10.6' + os.sep + 'python.exe'
            acrmap_create_maps = os.getcwd() + os.sep + 'arcmap_create_maps-res.py'
            if os.system(r'{0} {1}'.format(arcpy, acrmap_create_maps)) == 0:
                print('Создание изображений прошло успешно')
                self.info_label.setStyleSheet("color: rgba(71, 230, 98, 90)")
                loadDataWindow.info_label.setText('Создание изображений прошло успешно')


            loadDataWindow.download_btn.setEnabled(True)
            loadDataWindow.copy_btn.setEnabled(True)



    def run(self):
        self._download(self.products, self.path, self.zone)

checked_items = []
class LoadDataWindow(QDialog):
    def __init__(self):
        super(LoadDataWindow, self).__init__()
        path = resource_path('loadData.ui')
        loadUi(path, self)
        # Подключение метода к событиям клика по кнопке
        self.openMap_btn.clicked.connect(self.openMap)
        self.download_btn.clicked.connect(self.download)
        self.copy_btn.clicked.connect(self.copy_files)
        self.geoTiff_CB.stateChanged.connect(self.imageCB)

        self.cloudFrom.setValidator(QIntValidator(0, 99)) # Установил ограничение на ввод только чисел от 0 до 99
        self.cloudTo.setValidator(QIntValidator(0, 99))


        self.dateTo.setDate(datetime.datetime.now().date())
        dt = self.dateTo.date()
        self.dateFrom.setDate(dt.addDays(-1))

        self.info_label.setVisible(False) #скрытие информационной строки
        self.dwnPath_label.setText(work_path + os.sep + download_path) #вывод полного пути до каталога загрузки

        self.folder_btn.clicked.connect(self.openFolder)
        self.help_btn.clicked.connect(self.openManual)


        # QP1 = QPixmap('icons/question-solid.svg')
        # Qpain = QPainter(QP1)
        # Qpain.setCompositionMode(QPainter.CompositionMode_SourceIn)
        # color = QColor.fromRgba64(97, 141, 250, 98)
        # Qpain.setBrush(color)
        # Qpain.setPen(color)
        # Qpain.drawRect(QP1.rect())
        # self.help_btn.setIcon(QIcon(QP1))

        self.help_btn.setIcon(QIcon(QPixmap('icons/question-solid.svg')))
        self.folder_btn.setIcon(QIcon(QPixmap('icons/folder-solid.svg')))

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
            chkBox.setText(zone.replace('_', ' '))

        self.zonesList.itemClicked.connect(self.zoneClicked) #событие нажатия элемента списка зон



    def openManual(self):
        os.startfile(os.getcwd() + os.sep + 'Инструкция.docx')

    def openFolder(self):
        os.startfile(work_path)

    def imageCB(self):
        sender = self.sender()
        if sender.checkState() == 2:
            # self.images_CB.setEnabled(True)
            self.RB_B8.setCheckable(True)
            self.RB_B11.setCheckable(True)
            self.RB_B8.setChecked(True)
        else:
            # self.images_CB.setEnabled(False)
            # self.images_CB.setCheckState(0)
            #Убрать возможность выбирать радио и снять с них выбор
            self.RB_B8.setCheckable(False)
            self.RB_B11.setCheckable(False)
            self.RB_B8.setChecked(True)
            self.RB_B11.setChecked(False)


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
            #Tiles = tiles[zonesKeys[sender.row(sender.currentItem())]]
            listTiles = tiles[sender.row(sender.currentItem())]
            info = '{} - {}'.format(name, listTiles) #строка информации
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
                name = zones[zonesKeys.index(item)].replace('_', ' ')
                print(name)
                #print(zonesKeys[item])
                #print(tiles[checked_items.index(item)])
                nTiles = tiles[zonesKeys.index(item)]
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

    def copy_files(self):
        self.info_label.setText("")
        self.info_label.setVisible(True)
        try:
            zones = os.listdir(work_path + os.sep + download_path)
            print(zones)
            a = datetime.date.today()
            dateFolder = str(a.year)
            print(dateFolder)
            path = 'D:/PycharmProjects/automapizator/folder/' + dateFolder
            if os.path.isdir(path):
                for zone in zones:
                    files = os.listdir(work_path + os.sep + download_path + os.sep + zone)
                    for file in files:
                        self.info_label.setStyleSheet("color: rgba(71, 230, 98, 90)")
                        print('Копирование в процессе...')
                        self.info_label.setText('Копирование в процессе...')
                        shutil.copy(work_path + os.sep + download_path + os.sep + zone + os.sep + file,
                                    path)
            else:
                os.makedirs(path)
                for zone in zones:
                    files = os.listdir(work_path + os.sep + download_path + os.sep + zone)
                    for file in files:
                        self.info_label.setStyleSheet("color: rgba(71, 230, 98, 90)")
                        print('Копирование в процессе...')
                        self.info_label.setText('Копирование в процессе...')
                        shutil.copy(work_path + os.sep + download_path + os.sep + zone + os.sep + file,
                                    path)
            print('Копирование завершено')
            self.info_label.setStyleSheet("color: rgba(71, 230, 98, 90)")
            self.info_label.setText('Копирование завершено')
        except FileNotFoundError:
            self.info_label.setStyleSheet("color: rgb(255, 6, 60)")
            self.info_label.setText('Сначала загрузите данные, для создания нужных каталогов')


    #функция загрузки
    def download(self):
        self.info_label.setText("")
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
            self.info_label.setStyleSheet("color: rgb(255, 6, 60)")
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
            print('Зона - {}'.format(zone))
            print(tiles[checked_items.index(zone)])
            products = OrderedDict()
            for tile in tiles[checked_items.index(zone)]:
                print(tile)
                try:
                    kwg = dict_query_kwargs.copy()
                    kwg['tileid'] = tile
                    requests = api.query(**kwg)
                    products.update(requests)
                    print('--------')
                    #self.info_label.setText()
                except:
                    self.info_label.setStyleSheet("color: rgb(255, 6, 60)")
                    self.info_label.setVisible(True)
                    self.info_label.setText(
                        'Ошибка в введёной дате, либо Ошибка подключения к сервису ESA, проверьте адресс, логин и пароль')
                list_keys = list(products.keys())
            print('Найдено сцен в количестве {}'.format(len(products)))
            for elem in list_keys:
                print(products[elem]['title'])
                self.zonesInfoList.appendPlainText(products[elem]['title'])

            path = work_path + os.sep + download_path + os.sep + zone
            try: #создание объекта класса загрузки файлов зоны
                self.downloadProduct = downloadProducts(products, path, zone)
                self.downloadProduct.setTerminationEnabled(True)
                self.downloadProduct.start() #старт потока
                self.connect(self.downloadProduct, pyqtSignal("finished(True)"), self.done)
            except:
                self.info_label.setStyleSheet("color: rgb(255, 6, 60)")
                self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))
            # for elem in list_keys:
            #     print(products[elem]['title'])
            #     self.zonesInfoList.appendPlainText(products[elem]['title'])
            #
            # path = work_path + os.sep + download_path + os.sep + zone
            # try: #создание объекта класса загрузки файлов зоны
            #     self.downloadProduct = downloadProducts(products, path, zone)
            #     self.downloadProduct.setTerminationEnabled(True)
            #     self.downloadProduct.start() #старт потока
            #     self.connect(self.downloadProduct, pyqtSignal("finished(True)"), self.done)
            # except:
            #     self.info_label.setStyleSheet("color: rgb(255, 6, 60)")
            #     self.info_label.setText('Не удалось скачать данные для "{}"'.format(zone))

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

    # mainWindow = MainWindow()
    # widget.addWidget(mainWindow)

    loadDataWindow = LoadDataWindow()
    widget.addWidget(loadDataWindow)

    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Выход")