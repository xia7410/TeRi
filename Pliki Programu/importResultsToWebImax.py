import csv
import os
import datetime
from xlrd import open_workbook

from PyQt4 import QtCore


class ImportResultsToCSV(QtCore.QThread):

    def __init__(self, responsible, path_xls_file, excel_sheet_name, parent=None):
        super(ImportResultsToCSV, self).__init__(parent)
        self.responsible = responsible
        self.excel_sheet_name = excel_sheet_name
        self.work_book = open_workbook(path_xls_file)
        self.work_sheet = self.work_book.sheet_by_name(excel_sheet_name)
        self.user_path()

    def run(self):
        self.read_excel_file(self.excel_sheet_name)

    def user_path(self):
        self.userdir = os.path.expanduser('~') + '\\Desktop\\TeRI_Results\\' + str(datetime.date.today()) \
                       + '\\CSV_WebImax'

        print(self.userdir)

        if not os.path.exists(self.userdir):
            os.makedirs(self.userdir)

    def read_excel_file(self, excel_sheet_name):
        # Definuje nazwy paczek z konkretnych TC
        if excel_sheet_name == '2G':
            self.package_list = {'KC201': '', 'KC202': '', 'KC203': '', 'KC204': '', 'KC205': '', 'KC206': '',
                                 'KC207': '', 'KC208': '', 'KC221': '', 'KC222': '', 'KC223': '', 'KC231': '',
                                 'KC233': '', 'KC241': '', 'KC_End': ''}
        elif excel_sheet_name == '3G':
            self.package_list = {'KC401': '', 'KC402': '', 'KC403': '', 'KC404': '', 'KC405': '', 'KC406': '',
                                 'KC408': '', 'KC420': '', 'KC421': '', 'KC422': '', 'KC423': '', 'KC424': '',
                                 'KC425': '', 'KC426': '', 'KC427': '', 'KC428': '', 'KC429': '', 'KC430': '',
                                 'KC431': '', 'KC432': '', 'KC433': '', 'KC434': '', 'KC436': '', 'KC437': '',
                                 'KC_End': ''}
        # Wpisywanie zakresów dla poszczególnych paczek KC
        for item in range(self.work_sheet.nrows):
            # Odczytuje i zapisuje do słownika nazwę paczki dla 2G i 3G
            if self.work_sheet.cell_value(item, 9) in self.package_list.keys():
                self.package_list[self.work_sheet.cell_value(item, 9)] = item
                continue
            elif self.work_sheet.cell_value(item, 0) == 'Passed':
                self.package_list['KC_End'] = item

        for count in range(3, 20):
            if self.work_sheet.cell_value(self.package_list['KC_End'] - count, 0) != '':
                self.package_list['KC_End'] -= count + 1
                break

        self.list_to_write_to_csv = list()
        # Tworzymy listę wszystkich TC z excel`a
        for item_ws in range(self.work_sheet.nrows):
            if self.work_sheet.cell_value(item_ws, 0) == 'Passed':
                break
            # Jeżeli pole w excelu z nazwą TC nie jest puste wykonaj instrukcje
            if self.work_sheet.cell_value(item_ws, 0) != '':
                item_list = list()
                item_list.append(
                    [item_ws, self.work_sheet.cell_value(item_ws, 0), self.work_sheet.cell_value(item_ws, 8),
                     self.responsible, self.work_sheet.cell_value(item_ws, 9), '', '',
                     self.work_sheet.cell_value(item_ws, 16)])
                # Jeżeli kolejne pola z TC są puste wykonaj instrukcję (pouste pola oznaczają komórki złączone)
                if self.work_sheet.cell_value(item_ws + 1, 0) == '':
                    # Sprawdzamy kolejne pola w celu stworzenia listy z tym samym TC ale różnymi parametrami
                    for z_item in range(1, 100):

                        if self.work_sheet.cell_value(item_ws + z_item, 0) == '':
                            item_list.append(
                                [item_ws + z_item, self.work_sheet.cell_value(item_ws + z_item, 0),
                                 self.work_sheet.cell_value(item_ws + z_item, 8),
                                 self.responsible, self.work_sheet.cell_value(item_ws + z_item, 9), '', '',
                                 self.work_sheet.cell_value(item_ws + z_item, 16)]
                            )
                        else:
                            if len(item_list) == 1:
                                self.check_and_format_single_tc(excel_tc=item_list)

                            elif len(item_list) > 1:
                                self.check_tc_list(tc_list=item_list)
                            break
                else:  # if self.work_sheet.cell_value(item_ws + z_item, 0) == '':
                    # Jeżeli długość item_list jest 1 przekazujemy listę do funkcji w celu formatowania i zapisujemy
                    # do list_to_write_to_cvs
                    if len(item_list) == 1:
                        self.check_and_format_single_tc(excel_tc=item_list)

                    elif len(item_list) > 1:
                        self.check_tc_list(tc_list=item_list)
        self.write_to_csv()

    def check_tc_list(self, tc_list):
        package = list(self.package_list.keys())
        package.sort()
        list_to_rm = list()

        for item in tc_list:
            if item[4] in package:
                list_to_rm.append(item)

        if len(list_to_rm) > 0:
            for item in list_to_rm:
                tc_list.remove(item)

        if len(tc_list) == 1:
            self.check_and_format_single_tc(excel_tc=tc_list)
        elif len(tc_list) > 1:
            self.check_and_format_tc_list(tc_list=tc_list)

    def check_and_format_tc_list(self, tc_list):

        for item in tc_list:
            if item[2] == 'P':
                item[2] = 'passed'
            elif item[2] == 'F':
                item[2] = 'failed'
                self.write_to_file(paramiter='Fail', tc=item)
            elif item[2] == 'N/A':
                self.write_to_file(paramiter='N/A', tc=item)
            elif item[2] == '':
                self.write_to_file(paramiter='Null', tc=item)

        pass_list = [x for x in tc_list if x[2] == 'passed']
        fail_list = [x for x in tc_list if x[2] == 'failed']
        na_list = [x for x in tc_list if x[2] == 'N/A']

        if len(pass_list) == len(tc_list):
            self.list_to_write_to_csv.append(tc_list[0])
        elif len(fail_list) == len(tc_list):
            self.list_to_write_to_csv.append(tc_list[0])
        elif (len(pass_list) + len(fail_list)) == len(tc_list):
            self.list_to_write_to_csv.append(fail_list[0])
        elif (len(pass_list) + len(na_list)) == len(tc_list):
            self.list_to_write_to_csv.append(pass_list[0])
        elif (len(fail_list) + len(na_list)) == len(tc_list):
            self.list_to_write_to_csv.append(fail_list[0])
        elif (len(pass_list) + len(fail_list) + len(na_list)) == len(tc_list):
            self.list_to_write_to_csv.append(fail_list[0])

    def check_and_format_single_tc(self, excel_tc):
        package = list(self.package_list.keys())
        package.sort()

        if excel_tc[0][0] >= self.package_list[package[0]] and excel_tc[0][0] <= self.package_list['KC_End']:
            for index, element in enumerate(excel_tc[0]):
                if type(element) is str:
                    excel_tc[0][index] = '_'.join(element.split())

            for index, element in enumerate(package):
                try:
                    if (excel_tc[0][0] > self.package_list[element]) and \
                            (excel_tc[0][0] < self.package_list[package[index + 1]]):
                        excel_tc[0][1] = excel_tc[0][1] + '_' + element
                        break
                except IndexError:
                    if excel_tc[0][0] > self.package_list[package[-1]] and element == package[-1]:
                        pass

        if excel_tc[0][2] == 'P':
            excel_tc[0][2] = 'passed'
            self.list_to_write_to_csv.append(excel_tc[0])
        elif excel_tc[0][2] == 'F':
            excel_tc[0][2] = 'failed'
            self.list_to_write_to_csv.append(excel_tc[0])
            self.write_to_file(paramiter='Fail', tc=excel_tc[0])
        elif excel_tc[0][2] == 'N/A':
            self.write_to_file(paramiter='N/A', tc=excel_tc[0])
        elif excel_tc[0][2] == '':
            self.write_to_file(paramiter='Null', tc=excel_tc[0])
            pass  # write to investigation log

    def write_to_file(self, paramiter, tc):
        if paramiter == 'N/A':
            log_file = open(self.userdir + '\\NA_results.txt', 'a', encoding='utf-8')
            log_file.write('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(tc[1], tc[2], tc[3], tc[4], tc[5],
                                                                           tc[6], tc[7], '\n'))
            log_file.close()

        elif paramiter == 'Null':
            log_file = open(self.userdir + '\\TC_without_result.txt', 'a', encoding='utf-8')
            log_file.write('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(tc[1], tc[2], tc[3], tc[4], tc[5],
                                                                           tc[6], tc[7], '\n'))
            log_file.close()

        elif paramiter == 'Fail':
            log_file = open(self.userdir + '\\TC_with_FAIL_result.txt', 'a', encoding='utf-8')
            log_file.write('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(tc[1], tc[2], tc[3], tc[4], tc[5],
                                                                           tc[6], tc[7], '\n'))
            log_file.close()

    def write_to_csv(self):

        pass