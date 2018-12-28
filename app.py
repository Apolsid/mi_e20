import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import uic
from PyQt5.QtWidgets import QListWidgetItem, QMainWindow, QApplication, QWidget


#import design  # Это наш конвертированный файл дизайна


form_base = 'untitled.ui'
form_row = 'row.ui'


class QCustomQWidget (QWidget):
	def __init__ (self):
		super(QCustomQWidget, self).__init__()
		uic.loadUi(form_row, self)

	def setInfo(self, text):
		self.l_info.setText(text)

	def setNumber(self, n):
		self.l_number.setText(n)

	def setInfo(self, text):
		self.info.setText(text)





class ExampleApp(QMainWindow):
	def __init__(self):
		super(ExampleApp, self).__init__()
		uic.loadUi(form_base, self)

		self.pushButton.clicked.connect(self.browse_folder)


	def browse_folder(self):
		myQCustomQWidget = QCustomQWidget()
		myQListWidgetItem = QListWidgetItem(self.listWidget)

		myQListWidgetItem.setSizeHint(myQCustomQWidget.size())
		print(myQCustomQWidget.size())
		self.listWidget.addItem(myQListWidgetItem)
		self.listWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)



def main():
	app = QApplication(sys.argv)  # Новый экземпляр QApplication
	window = ExampleApp()  # Создаём объект класса ExampleApp
	window.show()  # Показываем окно
	app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
	main()  # то запускаем функцию main()