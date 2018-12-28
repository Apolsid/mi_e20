import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import uic
from PyQt5.QtWidgets import QListWidgetItem, QMainWindow, QApplication, QWidget
import configparser



config_name = 'config.ini'
config_code = 'utf-8'

form_base = 'untitled.ui'
form_row = 'row.ui'





class Row (QWidget):
	def __init__ (self):
		super(Row, self).__init__()
		uic.loadUi(form_row, self)

	def setInfo(self, text):
		self.l_info.setText(text)

	def setNumber(self, n):
		self.l_number.setText(n)





class ExampleApp(QMainWindow):
	def __init__(self):
		super(ExampleApp, self).__init__()
		uic.loadUi(form_base, self)

		self._cfg = configparser.ConfigParser()
		self._cfg.read(config_name, encoding=config_code)

		count = self._cfg.getint('DEFAULT', 'count')
		count = self._cfg.getint('DEFAULT', 'count')

		#range(count)
		for i in range(10):
			n = str(i)
			self._addRow(n)






	def _addRow(self, n):
		item_conf = self._cfg['item-' + n]

		row = Row()
		row.setNumber(n)
		row.setInfo(item_conf['info'])

		myQListWidgetItem = QListWidgetItem(self.listWidget)

		myQListWidgetItem.setSizeHint(row.size())
		self.listWidget.addItem(myQListWidgetItem)
		self.listWidget.setItemWidget(myQListWidgetItem, row)



def main():
	app = QApplication(sys.argv)  # Новый экземпляр QApplication
	window = ExampleApp()  # Создаём объект класса ExampleApp
	window.show()  # Показываем окно
	app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
	main()  # то запускаем функцию main()