import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import uic
from PyQt5.QtWidgets import QListWidgetItem, QMainWindow, QApplication, QWidget, QFileDialog
import configparser
import os.path


config_name = 'config.ini'
config_code = 'utf-8'
config_item_name = 'item-'

form_base = 'untitled.ui'
form_row = 'row.ui'





class Row (QWidget):
	_file_name = None
	_is_hidden = None
	_conf = None
	_n = None

	def __init__ (self):
		super(Row, self).__init__()
		uic.loadUi(form_row, self)

		self.cb_hidden.stateChanged.connect(lambda:self._setEnable(self.cb_hidden.isChecked()))
		self.btn_file.clicked.connect(self._updateFile)

	def _updateFile(self):
		file = QFileDialog.getOpenFileName(self, 'Выберите mp3 файл', '', 'Sound Files (*.mp3)')[0]
		if file:
			self._file_name = file
			self.l_file.setText(os.path.basename(file))

	def setBaseInfo(self, n, conf):
		self._n = n
		self._conf = conf

		item_conf = conf[config_item_name + n]

		file = item_conf['file']
		info = item_conf['info']
		hidden = item_conf.getboolean('hidden')

		self._file_name = file
		self.cb_hidden.setChecked(hidden)
		self.l_number.setText(n)
		self.l_info.setText(info)
		self.l_file.setText(file)


	def _setEnable(self, b):
		self._is_hidden = b
		self.btn_file.setEnabled(not b)
		self.l_file.setEnabled(not b)

		#self._conf.set(config_item_name + self._n, 'hidden', str(b))






class WindowApp(QMainWindow):
	_server_ip = None
	_robot_ip = None
	_robot_tocken = None

	def __init__(self):
		super(WindowApp, self).__init__()
		uic.loadUi(form_base, self)

		self.e_server_ip.textChanged.connect(self._on_server_ip)
		self.e_robot_ip.textChanged.connect(self._on_robot_ip)
		self.e_robot_tocken.textChanged.connect(self._on_robot_tocken)

		self._cfg = configparser.ConfigParser()
		self._cfg.read(config_name, encoding=config_code)

		count = self._cfg.getint('DEFAULT', 'count')

		self._cfg.get('DEFAULT', 'server_ip')
		self._cfg.get('DEFAULT', 'robot_ip')
		self._cfg.get('DEFAULT', 'robot_tocken')

		self._on_server_ip(self._cfg.get('DEFAULT', 'server_ip'))
		self._on_robot_ip(self._cfg.get('DEFAULT', 'robot_ip'))
		self._on_robot_tocken(self._cfg.get('DEFAULT', 'robot_tocken'))

		#range(count)
		for i in range(10):
			n = str(i)
			self._addRow(n)


	def _on_server_ip(self, ip):
		self._server_ip = ip
		if self._server_ip:
			self.btn_server_stop.setEnabled(True)
			self.btn_server_start.setEnabled(True)
		else:
			self.btn_server_stop.setEnabled(False)
			self.btn_server_start.setEnabled(False)

	def _on_robot_ip(self, ip):
		self._robot_ip = ip
		if self._robot_ip and self._robot_tocken:
			self.btn_robot_info.setEnabled(True)
		else:
			self.btn_robot_info.setEnabled(False)

	def _on_robot_tocken(self, tocken):
		self._robot_tocken = tocken
		if self._robot_ip and self._robot_tocken:
			self.btn_robot_info.setEnabled(True)
		else:
			self.btn_robot_info.setEnabled(False)


	def _addRow(self, n):
		row = Row()
		row.setBaseInfo(n, self._cfg)

		listWidget = QListWidgetItem(self.list_rows)

		listWidget.setSizeHint(row.size())
		self.list_rows.addItem(listWidget)
		self.list_rows.setItemWidget(listWidget, row)


	def saveConf(self):
		self._cfg.write()



def main():
	app = QApplication(sys.argv)
	window = WindowApp()
	window.show()
	app.exec_()


if __name__ == '__main__':
	main()