import os
import re

from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QTableWidgetItem, QHeaderView
from PyQt5 import QtCore
from sentinelsat import SentinelAPI
from collections import OrderedDict

if __name__ == "__main__":

        products = OrderedDict()

        api = SentinelAPI('helga1289', 'gordeeva120689', 'https://scihub.copernicus.eu/dhus')


        tiles = ['T44UPF', 'T44UNF', 'T44UNE']
        kwg = {'platformname': 'Sentinel-2',  # словарь параметров для запроса
                'producttype': 'S2MSI1C',
                'date': ('NOW-14DAYS', 'NOW')
                #'cloudcoverpercentage': (cloudFrom, cloudTo)
                }
        # kwg['tileid'] = 'T44UPF'
        # requests = api.query(**kwg)
        # products.update(requests)
        # print('--------')

        for tile in tiles:
                kw = kwg.copy()
                kw['tileid'] = tile
                pp = api.query(**kw)
                products.update(pp)

        print('Найдено сцен в количестве {}'.format(len(products)))