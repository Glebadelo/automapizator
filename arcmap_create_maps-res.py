# -*- coding: utf-8 -*-

import arcpy
#from arcpy import arcpy
#from arcgis.widgets._mapview._raster.engine import arcpy
#import glob
import os
import datetime
#import shutil
#import ftplib




# list_sat_name = ['S2A', 'S2B']        # список имён СПУТНИКОВ


F_type = ''  # тип продукта извлекаемый из имени файла MSI1C/S2MSI1C
date = ''
poloj = ''  # переменная для присвоения даты из имени геотифа
name_KA = ''  # имя КА ('S2A'или'S2B')
tile = ''
time = ''  # время
Inftext = ''  # переменная наполняемая данными: имя КА, тип_продукта, дата, время: 'S5P_NO2-20200928-0723'


def func_create_map_by_arc_map():
    """ Функция создания тем.карты в ArcMap
    """
    #input_name_dir = r'C:\Users\ota\Desktop\MyNew\SSS'  # путь к файлам исходникам с полным именем (для извлечения информации о спутнике, дате, времени, продукте)   # S2A_MSIL1C_20220626T053651_N0400_R005_T44UPF_20220626T073225.zip
    input_dir = os.getcwd() + os.sep + 'outputTIFF'  # - путь к входным файлам вида   # layer1.tif layer2.tif....
    template_dir = os.getcwd() + os.sep + 'Shablon'  # - путь к шаблонам (проектам ArcMap)
    output_dir = os.getcwd() + os.sep + 'outputMap'  # - путь к каталогам для выходных данных (куда сохранять готовые карты в формате jpg)
    if os.path.isdir(output_dir) == False:
        os.makedirs(output_dir)
    mxd = 0

    for zone in os.listdir(input_dir + os.sep):
        print(zone)
        list_catalog_tifs = os.listdir(input_dir + os.sep + zone + os.sep)
        print(list_catalog_tifs)# список всего что находится в каталоге с исходниками
        list_tifs = []                             # список который будет наполняться только именами файлов с раширением '.tif'  ['layer1.tif', 'layer2.tif',...]
        for files in list_catalog_tifs:
            if files[-4:] == '.tif' and os.path.isfile(
                    input_dir + os.sep + zone + os.sep + files):  # если окончание файла заканчивается на '.tif' и это является файлом
                print('files - ', files)
                list_tifs.append(files)
                print(list_tifs)

        for filename1 in list_tifs:
            for filename2 in list_tifs:
                mxd = 0

                a = filename1.split('_')
                b = filename2.split('_')
                if a[2] == b[2] and a[5] != b[5]:
                    name_KA = a[0]  # берём первый элемент из списка - имя спутника:  'S2B' или 'S2A'
                    # F_type = a[1]  # получаем тип продукта: #'MSIL1C'
                    poloj = a[4]  # для получения информации, какой шаблон использовать
                    tile = a[5]  # номер тайла для
                    date = a[2][0:8]  # '20220626'
                    time = a[2][9:13]  # '0536'

                    if poloj == 'R005':
                        mxd = arcpy.mapping.MapDocument(template_dir + os.sep + 'R005.mxd')

                        lyr = 0

                        for lyr in arcpy.mapping.ListLayers(mxd):
                            # if lyr.name == r"L1" and a[5] == 'T44UPF':
                            if lyr.name == r"L1":
                                lyr.replaceDataSource(input_dir + os.sep, "RASTER_WORKSPACE",
                                                      filename1)  # изменяем источник даты для растра (layer1.tif) в проекте ArcMap
                            # elif lyr.name == r"L2" and b[5] == 'T44UNF':
                            elif lyr.name == r"L2":
                                lyr.replaceDataSource(input_dir + os.sep, "RASTER_WORKSPACE",
                                                      filename2)  # и так далее для других слоёв ...

                        for elm in arcpy.mapping.ListLayoutElements(mxd,
                                                                    "TEXT_ELEMENT"):  # заполняем зарамочное в проекте arcmap, введя дату и имя файлов для текстовых элементов

                            if elm.name == "SatilInfo1":

                                if name_KA == 'S2A':
                                    elm.text = 'КА Sentinel-2A/MSI, © ESA, разрешение 10 м'  # вводим название спутника
                                elif name_KA == 'S2B':

                                    elm.text = 'КА Sentinel-2B/MSI, © ESA, разрешение 10 м'  # вводим название спутника

                            if elm.name == 'SatilInfo2':
                                elm.text = 'Спектральные каналы R: 0,76-0,90 мкм; G: 0,63-0,68 мкм; B: 0,53-0,57 мкм'
                            if elm.name == "DateInfo":
                                elm.text = date[-2:] + '.' + date[4:6] + '.' + date[0:4] + ' ' + time[0:2] + ':' + time[
                                                                                                                   1:3] + ' UTC'  # вводим в нижнюю строку информацию о дате и времени
                        outName = date[
                                  2:] + time + '.jpg'  # outName=F_type+"_"+date.replace(".","-")+".png"   - экспорт карты в формат png . при помощи метода .replace - меняем точки в стрке data на тире

                        arcpy.mapping.ExportToJPEG(mxd, output_dir + os.sep + outName, resolution=192)
                        del mxd

                    if poloj == 'R048':
                        mxd = arcpy.mapping.MapDocument(template_dir + os.sep + 'R048.mxd')

                        lyr = 0
                        for lyr in arcpy.mapping.ListLayers(mxd):
                            if lyr.name == r"L1" and a[5] == 'T44UPF':
                                lyr.replaceDataSource(input_dir + os.sep + zone + os.sep, "RASTER_WORKSPACE",
                                                      filename1)  # изменяем источник даты для растра (layer1.tif) в проекте ArcMap
                            elif lyr.name == r"L2" and b[5] == 'T44UNF':
                                lyr.replaceDataSource(input_dir + os.sep + zone + os.sep, "RASTER_WORKSPACE",
                                                      filename2)  # и так далее для других слоёв ...

                        for elm in arcpy.mapping.ListLayoutElements(mxd,
                                                                    "TEXT_ELEMENT"):  # заполняем зарамочное в проекте arcmap, введя дату и имя файлов для текстовых элементов

                            if elm.name == "SatilInfo1":

                                if name_KA == 'S2A':
                                    elm.text = 'КА Sentinel-2A/MSI, © ESA, разрешение 10 м'  # вводим название спутника
                                elif name_KA == 'S2B':

                                    elm.text = 'КА Sentinel-2B/MSI, © ESA, разрешение 10 м'  # вводим название спутника

                            if elm.name == 'SatilInfo2':
                                elm.text = 'Спектральные каналы R: 0,76-0,90 мкм; G: 0,63-0,68 мкм; B: 0,53-0,57 мкм'
                            if elm.name == "DateInfo":
                                elm.text = date[-2:] + '.' + date[4:6] + '.' + date[0:4] + ' ' + time[0:2] + ':' + time[
                                                                                                                   1:3] + ' UTC'  # вводим в нижнюю строку информацию о дате и времени
                        outName = date[
                                  2:] + time + '.jpg'  # outName=F_type+"_"+date.replace(".","-")+".png"   - экспорт карты в формат png . при помощи метода .replace - меняем точки в стрке data на тире
                        arcpy.mapping.ExportToJPEG(mxd, output_dir + os.sep + outName, resolution=192)
                        del mxd

    






func_create_map_by_arc_map()