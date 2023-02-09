import sys
import datetime as dt

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
import psycopg2


class MainWin(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self._date = dt.datetime.today().date()
        self._dateObjectNames = ('mainDate', 'addDate', 'logDate',)
        self.initUi()

    def initUi(self):
        self.setWindowTitle('DCC')

        self.mainLayout = QGridLayout(self)
        self.setLayout(self.mainLayout)
        self.setGeometry(700, 300, 341, 407)

        self.tabs = QTabWidget(self)

        # Вкладка Главная
        self.mainTab = QWidget(self)
        layout = QGridLayout()
        self.mainTab.setLayout(layout)

        self.helloLabel = QLabel('Добро пожаловать!', self)
        self.helloLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.mainDateSubLayout = QWidget(self)
        dateLayout = QGridLayout()
        self.mainDateSubLayout.setLayout(dateLayout)

        self.setDateSubLayout(dateLayout, self._dateObjectNames[0])

        self.cashTable = QTableWidget(self)
        self.cashTable.setColumnCount(2)
        self.cashTable.setRowCount(1)

        self.cashTable.setHorizontalHeaderItem(0, QTableWidgetItem('Карта'))
        self.cashTable.setHorizontalHeaderItem(1, QTableWidgetItem('Наличные'))
        self.cashTable.verticalHeader().hide()

        self.updateCashTable()

        layout.addWidget(self.helloLabel, 0, 0)
        layout.addWidget(self.mainDateSubLayout, 1, 0)
        layout.addWidget(self.cashTable, 2, 0)

        # Вкладка Добавление
        self.addTab = QWidget(self)
        layout = QGridLayout()
        self.addTab.setLayout(layout)

        self.addDateSubLayout = QWidget(self)
        dateLayout = QGridLayout()
        self.addDateSubLayout.setLayout(dateLayout)

        self.setDateSubLayout(dateLayout, self._dateObjectNames[1])

        self.addSubLayout = QWidget(self)
        subLayout = QGridLayout()
        self.addSubLayout.setLayout(subLayout)

        self.orderIdLabel = QLabel('Номер заказа:', self)
        self.orderIdLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.orderIdEdit = QLineEdit(self)
        cursor = createConnection().cursor()
        cursor.execute("SELECT orderid FROM cashlogs")
        lastId = cursor.fetchall()[-1][0]
        self.orderIdEdit.setText(lastId)

        self.cashLabel = QLabel('Сумма:', self)
        self.cashLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.cashEdit = QLineEdit(self)
        self.cashEdit.setText('')

        subLayout.addWidget(self.orderIdLabel, 0, 0)
        subLayout.addWidget(self.orderIdEdit, 0, 1)
        subLayout.addWidget(self.cashLabel, 1, 0)
        subLayout.addWidget(self.cashEdit, 1, 1)

        self.addButtonsLayout = QWidget(self)
        buttonsLayout = QGridLayout()
        self.addButtonsLayout.setLayout(buttonsLayout)

        self.addCashButton = QPushButton('Наличные', self)
        self.addCashButton.clicked.connect(self.addCash)

        self.addCardButton = QPushButton('Карта', self)
        self.addCardButton.clicked.connect(self.addCard)

        buttonsLayout.addWidget(self.addCashButton, 0, 0)
        buttonsLayout.addWidget(self.addCardButton, 0, 1)

        layout.addWidget(self.addDateSubLayout, 0, 0)
        layout.addWidget(self.addSubLayout, 1, 0)
        layout.addWidget(self.addButtonsLayout, 2, 0)

        # Вкладка История
        self.logTab = QWidget(self)
        layout = QGridLayout()
        self.logTab.setLayout(layout)

        self.logDateSubLayout = QWidget(self)
        dateLayout = QGridLayout()
        self.logDateSubLayout.setLayout(dateLayout)

        self.setDateSubLayout(dateLayout, self._dateObjectNames[2])

        self.logTable = QTableWidget(self)
        self.logTable.setColumnCount(3)

        self.logTable.setHorizontalHeaderLabels(['Номер заказа', 'Сумма', 'Способ оплаты'])
        self.logTable.verticalHeader().hide()

        self.updateLogTable()

        layout.addWidget(self.logDateSubLayout, 0, 0)
        layout.addWidget(self.logTable, 1, 0)

        # Вкладка Редактирование
        self.editTab = QWidget(self)
        self.editLayout = QGridLayout()
        self.editTab.setLayout(self.editLayout)

        self.editSubLayout = QWidget(self)
        subLayout = QGridLayout()
        self.editSubLayout.setLayout(subLayout)

        self.editOrderIdLabel = QLabel('Номер заказа:', self)
        self.editOrderIdLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.editOrderIdEdit = QLineEdit(self)
        self.editOrderIdEdit.setText('')

        subLayout.addWidget(self.editOrderIdLabel, 0, 0)
        subLayout.addWidget(self.editOrderIdEdit, 0, 1)

        self.deleteOrderButton = QPushButton('Удалить', self)
        self.deleteOrderButton.clicked.connect(self.deleteOrder)

        self.editOrderButton = QPushButton('Редактировать', self)
        self.editOrderButton.clicked.connect(self.showEditOrder)

        self.editLayout.addWidget(self.editSubLayout, 0, 0)
        self.editLayout.addWidget(self.deleteOrderButton, 1, 0)
        self.editLayout.addWidget(self.editOrderButton, 2, 0)

        self.tabs.addTab(self.mainTab, 'Главная')
        self.tabs.addTab(self.addTab, 'Добавление')
        self.tabs.addTab(self.logTab, 'Отчет')
        self.tabs.addTab(self.editTab, 'Редактирование')

        self.mainLayout.addWidget(self.tabs)

    def setDateSubLayout(self, dateLayout, objectName):
        dateLabel = QLabel('{day}'.format(day=self._date), self)
        dateLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        dateLabel.setObjectName(objectName)

        prevDateButton = QPushButton('<', self)
        prevDateButton.clicked.connect(self.prevDate)

        nextDateButton = QPushButton('>', self)
        nextDateButton.clicked.connect(self.nextDate)

        todayButton = QPushButton('Сегодня', self)
        todayButton.clicked.connect(self.today)

        dateLayout.addWidget(prevDateButton, 0, 0)
        dateLayout.addWidget(dateLabel, 0, 1)
        dateLayout.addWidget(nextDateButton, 0, 2)
        dateLayout.addWidget(todayButton, 1, 1)

    def prevDate(self):
        self._date = self._date - dt.timedelta(days=1)
        for obj in self._dateObjectNames:
            dateLabel = self.findChild(QLabel, obj)
            dateLabel.setText('{day}'.format(day=self._date))
        self.updateCashTable()
        self.updateLogTable()

    def nextDate(self):
        self._date = self._date + dt.timedelta(days=1)
        for obj in self._dateObjectNames:
            dateLabel = self.findChild(QLabel, obj)
            dateLabel.setText('{day}'.format(day=self._date))
        self.updateCashTable()
        self.updateLogTable()

    def today(self):
        self._date = dt.datetime.today().date()
        for obj in self._dateObjectNames:
            dateLabel = self.findChild(QLabel, obj)
            dateLabel.setText('{day}'.format(day=self._date))
        self.updateCashTable()
        self.updateLogTable()

    def addCash(self):
        values = self.addValues(self.cashEdit.text(), 'Наличные')
        if values is not None:
            connect = createConnection()
            cursor = connect.cursor()
            cursor.execute("SELECT orderid FROM cashlogs WHERE orderid='{id}'".format(id=values['orderid']))
            row = cursor.fetchall()
            if row:
                QMessageBox.warning(self, 'Внимание',
                                    'Заказ с номером {id} уже существует!'.format(id=values['orderid']))
            else:
                cursor.execute(
                    "INSERT INTO cashlogs (orderid, cash, payment, date) VALUES {values}"
                    .format(values=tuple(values.values()))
                )
                connect.commit()
                QMessageBox.information(self, 'Информация', 'Заказ {id} за {cash} {payment} успешно добавлен.'
                                        .format(id=values['orderid'], cash=values['cash'], payment=values['payment']))
        self.updateCashTable()
        self.updateLogTable()

    def addCard(self):
        values = self.addValues(self.cashEdit.text(), 'Карта')
        if values is not None:
            connect = createConnection()
            cursor = connect.cursor()
            cursor.execute("SELECT orderid FROM cashlogs WHERE orderid='{id}'".format(id=values['orderid']))
            row = cursor.fetchall()
            if row:
                QMessageBox.warning(self, 'Внимание',
                                    'Заказ с номером {id} уже существует!'.format(id=values['orderid']))
            else:
                cursor.execute(
                    "INSERT INTO cashlogs (orderid, cash, payment, date) VALUES {values}"
                    .format(values=tuple(values.values()))
                )
                connect.commit()
                QMessageBox.information(self, 'Информация', 'Заказ {id} за {cash} {payment} успешно добавлен.'
                                        .format(id=values['orderid'], cash=values['cash'], payment=values['payment']))
        self.updateCashTable()
        self.updateLogTable()

    def deleteOrder(self):
        connect = createConnection()
        cursor = connect.cursor()
        orderId = self.editOrderIdEdit.text()
        if len(orderId) <= 5 and len(orderId) != 0:
            orderId = orderId.rjust(5, '0')
            cursor.execute("SELECT orderid FROM cashlogs WHERE orderid='{id}'".format(id=orderId))
            row = cursor.fetchall()
            if row:
                cursor.execute("DELETE FROM cashlogs WHERE orderid='{id}'".format(id=orderId))
                connect.commit()
                QMessageBox.information(self, 'Информация', 'Заказ {id} Успешно удален.'.format(id=orderId))
            else:
                QMessageBox.warning(self, 'Внимание', 'Заказ с номером {id} не найден!'.format(id=orderId))
        else:
            QMessageBox.warning(self, 'Внимание', 'Длина номера заказа не должна быть от 1 до 5 знаков!')
        self.updateCashTable()
        self.updateLogTable()

    def showEditOrder(self):
        self.editOrderLayout = QWidget(self)
        layout = QGridLayout()
        self.editOrderLayout.setLayout(layout)

        self.editCashLabel = QLabel('Сумма:', self)
        self.editCashLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.editCashEdit = QLineEdit(self)
        self.editCashEdit.setText('')

        self.comboLayout = QLabel('Способ оплаты:')
        self.comboLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.comboBox = QComboBox(self)
        self.comboBox.addItems(['Карта', 'Наличные'])

        self.saveButton = QPushButton('Сохранить', self)
        self.saveButton.clicked.connect(self.saveOrder)

        layout.addWidget(self.editCashLabel, 0, 0)
        layout.addWidget(self.editCashEdit, 0, 1)
        layout.addWidget(self.comboLayout, 1, 0)
        layout.addWidget(self.comboBox, 1, 1)

        self.editLayout.addWidget(self.editOrderLayout, 3, 0)
        self.editLayout.addWidget(self.saveButton, 4, 0)

        self.editOrderButton.clicked.disconnect()
        self.editOrderButton.setText('Скрыть')
        self.editOrderButton.clicked.connect(self.hideEditOrder)

    def hideEditOrder(self):
        self.editOrderLayout.deleteLater()
        self.comboBox.deleteLater()
        self.saveButton.deleteLater()
        self.editOrderButton.clicked.disconnect()
        self.editOrderButton.setText('Редактировать')
        self.editOrderButton.clicked.connect(self.showEditOrder)

    def saveOrder(self):
        try:
            cash = self.editCashEdit.text()
            values = {
                'orderid': self.editOrderIdEdit.text(),
                'cash': float(cash.replace(',', '.')),
                'payment': self.comboBox.currentText(),
            }
        except ValueError:
            values = {
                'orderid': self.editOrderIdEdit.text(),
                'cash': None,
                'payment': self.comboBox.currentText(),
            }
        if len(values['orderid']) <= 5 and len(values['orderid']) != 0:
            values['orderid'] = values['orderid'].rjust(5, '0')
            print(values)
            if values is not None:
                connect = createConnection()
                cursor = connect.cursor()
                cursor.execute("SELECT orderid FROM cashlogs WHERE orderid='{id}'".format(id=values['orderid']))
                row = cursor.fetchall()
                if row:
                    if values['cash'] is not None:
                        cursor.execute(
                            "UPDATE cashlogs SET cash={cash}, payment='{payment}' WHERE orderid='{id}'"
                            .format(cash=values['cash'], payment=values['payment'], id=values['orderid'])
                        )
                        connect.commit()
                        QMessageBox.information(self, 'Информация', 'Заказ {id} успешно обновлен.\n'
                                                                    'Новые значения:\n'
                                                                    'Сумма - {cash};\n'
                                                                    'Способ оплаты - {payment}.'
                                                .format(id=values['orderid'], cash=values['cash'],
                                                        payment=values['payment']))
                    else:
                        cursor.execute(
                            "UPDATE cashlogs SET payment='{payment}' WHERE orderid='{id}'"
                            .format(payment=values['payment'], id=values['orderid'])
                        )
                        connect.commit()
                        QMessageBox.information(self, 'Информация', 'Заказ {id} успешно обновлен.\n'
                                                                    'Новые значения:\n'
                                                                    'Способ оплаты - {payment}.'
                                                .format(id=values['orderid'], payment=values['payment']))
                else:
                    QMessageBox.warning(self, 'Внимание',
                                        'Заказ с номером {id} не найден!'.format(id=values['orderid']))
            self.updateCashTable()
            self.updateLogTable()
        else:
            QMessageBox.warning(self, 'Внимание', 'Длина номера заказа не должна быть от 1 до 5 знаков!')

    def addValues(self, cash, payment):
        values = {}
        values['orderid'] = self.orderIdEdit.text()
        if len(values['orderid']) <= 5 and len(values['orderid']) != 0:
            values['orderid'] = values['orderid'].rjust(5, '0')
        else:
            QMessageBox.warning(self, 'Внимание', 'Длина номера заказа не должна быть от 1 до 5 знаков!')
            return None
        try:
            values['cash'] = float(cash.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, 'Внимание', 'В поле Сумма введите целое или дробное число!')
            return None
        values['payment'] = payment
        values['date'] = str(self._date)
        return values

    def updateCashTable(self):
        cardSum = 0
        cashSum = 0

        cursor = createConnection().cursor()
        cursor.execute(
            "SELECT cash FROM cashlogs WHERE date='{date}' and payment='Карта'".format(date=str(self._date))
        )

        rows = cursor.fetchall()

        for row in rows:
            cardSum += row[0]

        cursor = createConnection().cursor()
        cursor.execute(
            "SELECT cash FROM cashlogs WHERE date='{date}' and payment='Наличные'".format(date=str(self._date))
        )

        rows = cursor.fetchall()

        for row in rows:
            cashSum += row[0]

        self.cardItem = QTableWidgetItem(str(round(cardSum, 2)) + ' руб.')
        self.cardItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cashItem = QTableWidgetItem(str(round(cashSum, 2)) + ' руб.')
        self.cashItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cashTable.setItem(0, 0, self.cardItem)
        self.cashTable.setItem(0, 1, self.cashItem)
        self.cashTable.setColumnWidth(0, 146)
        self.cashTable.setColumnWidth(1, 147)

    def updateLogTable(self):
        self.logTable.setRowCount(1)
        cursor = createConnection().cursor()
        cursor.execute(
            "SELECT * FROM cashlogs WHERE date='{date}'".format(date=str(self._date))
        )

        rows = cursor.fetchall()

        if len(rows) != 0:
            self.logTable.setRowCount(len(rows))
            for index, row in enumerate(rows):
                orderRow = QTableWidgetItem(row[1])
                orderRow.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                cashRow = QTableWidgetItem(str(row[2]) + ' руб.')
                cashRow.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                paymentRow = QTableWidgetItem(row[3])
                paymentRow.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.logTable.setItem(index, 0, orderRow)
                self.logTable.setItem(index, 1, cashRow)
                self.logTable.setItem(index, 2, paymentRow)
        else:
            for index in range(3):
                emptyRow = QTableWidgetItem('-')
                emptyRow.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.logTable.setItem(0, index, emptyRow)

        if len(rows) > 8:
            self.logTable.setColumnWidth(0, 92)
            self.logTable.setColumnWidth(1, 82)
            self.logTable.setColumnWidth(2, 102)
        else:
            self.logTable.setColumnWidth(0, 98)
            self.logTable.setColumnWidth(1, 87)
            self.logTable.setColumnWidth(2, 108)


def createConnection():
    db = psycopg2.connect(
        database='dcc',
        user='jarder',
        password='enejymata',
        host='localhost',
        port='5432'
    )
    return db

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec_())
