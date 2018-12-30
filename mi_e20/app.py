import sys, os, configparser, miio
from PyQt5 import uic
from PyQt5.QtWidgets import QListWidgetItem, QMainWindow, QApplication, QWidget, QFileDialog
from PyQt5.QtCore import QStringListModel
from threading import Thread
from http.server import HTTPServer, SimpleHTTPRequestHandler

from mi_e20.core import Transport
from shutil import copyfile



config_name = 'mi_e20/config.ini'
config_code = 'utf-8'
config_item_name = 'item-'

form_base = 'mi_e20/template/app.ui'
form_row = 'mi_e20/template/row.ui'

base_file_path = 'mi_e20/base'



class ServerBase(SimpleHTTPRequestHandler):
	protocol_version = "HTTP/1.1"


class Server(Thread):
	port = 80
	ip = None
	_server = None
	_showInfo = None

	def __init__(self, ip, showInfo):
		Thread.__init__(self)
		self.ip = ip
		self._showInfo = showInfo


	def run(self):
		try:
			self._server = HTTPServer((self.ip, self.port), ServerBase)
			self._showInfo('run http server')
			self._server.serve_forever()

		except Exception as e:
			self._showInfo(str(e))


	def stop(self):
		if self._server:
			self._server.shutdown()
			self._server = None







class Row (QWidget):
	_base_file = None
	_user_file = None
	_hidden = None
	_custom = None

	_conf = None
	_n = None

	def __init__ (self):
		super(Row, self).__init__()
		uic.loadUi(form_row, self)

		self.cb_custom.stateChanged.connect(lambda:self._setCustom(self.cb_custom.isChecked()))
		self.cb_hidden.stateChanged.connect(lambda:self._setHidden(self.cb_hidden.isChecked()))

		self.btn_file.clicked.connect(self._updateFile)

	def getFileData(self):
		data = b''
		if not self._hidden:
			if self._custom:
				with open(self._user_file, 'rb+') as f:
					data = f.read()
			else:
				with open(base_file_path + '/' + self._base_file, 'rb+') as f:
					data = f.read()

		return data


	def setBaseInfo(self, n, conf):
		self._n = n
		self._conf = conf

		item_conf = conf[config_item_name + n]

		self._base_file = item_conf['base_file']
		self._user_file = item_conf['user_file']
		self._hidden = item_conf.getboolean('hidden')
		self._custom = item_conf.getboolean('custom')

		self.cb_custom.setChecked(self._custom)
		self.cb_hidden.setChecked(self._hidden)

		self.l_number.setText(n)
		self.l_info.setText(item_conf['info'])
		self._updateState()

	def _updateFile(self):
		file = QFileDialog.getOpenFileName(self, 'Выберите mp3 файл', '', 'Sound Files (*.mp3)')[0]
		if file:
			self._setUserFile(file)

	def _setUserFile(self, file):
		self._user_file = file
		self._conf.set(config_item_name + self._n, 'user_file', file)
		self._updateState()

	def _setCustom(self, b):
		self._custom = b
		self._updateState()
		self._conf.set(config_item_name + self._n, 'custom', str(b))

	def _setHidden(self, b):
		self._hidden = b
		self._updateState()
		self._conf.set(config_item_name + self._n, 'hidden', str(b))

	def _updateState(self):
		b = self._hidden
		b0 = self._custom

		self.btn_file.setEnabled(not b and b0)
		self.cb_custom.setEnabled(not b)
		self.l_file.setEnabled(not b and b0)

		self.l_file.setText(os.path.basename(self._user_file) if b0 else self._base_file)




class WindowApp(QMainWindow):
	_count = 109
	_rows = None

	_server_ip = None
	_server_worker = None
	_server_file = None

	_robot_ip = None
	_robot_tocken = None

	_conf_Def = 'DEFAULT'

	def __init__(self):
		super(WindowApp, self).__init__()
		uic.loadUi(form_base, self)

		self._rows = list()

		self.list_info_model = QStringListModel();
		self.list_info.setModel(self.list_info_model);

		self.e_server_ip.textChanged.connect(self._on_server_ip)
		self.e_robot_ip.textChanged.connect(self._on_robot_ip)
		self.e_robot_tocken.textChanged.connect(self._on_robot_tocken)


		self.btn_make.clicked.connect(self._on_make)

		self.btn_server_start.clicked.connect(self._on_server_start)
		self.btn_server_stop.clicked.connect(self._on_server_stop)
		self.btn_server_file.clicked.connect(self._on_server_file)
		self.btn_server_send.clicked.connect(self._on_server_send)

		self.btn_robot_info.clicked.connect(self._on_robot_info)
		self.btn_robot_info_sound.clicked.connect(self._on_robot_info_sound)


		self._cfg = configparser.ConfigParser()

		with open(config_name) as f:
			self._cfg.read_file(f)

		for i in range(self._count):
			n = str(i)
			self._addRow(n)

		self._server_ip = self._get_conf_param('server_ip')
		self.e_server_ip.setText(self._server_ip)

		self._robot_ip = self._get_conf_param('robot_ip')
		self.e_robot_ip.setText(self._robot_ip)

		self._robot_tocken = self._get_conf_param('robot_tocken')
		self.e_robot_tocken.setText(self._robot_tocken)

		self._server_file = self._get_conf_param('server_file')
		self.l_server_file.setText(os.path.basename(self._server_file))
		
		self._server_check_state()
		self._robot_check_state()



	def _get_conf_param(self, p):
		return self._cfg.get(self._conf_Def, p)

	def _set_conf_param(self, p, v):
		return self._cfg.set(self._conf_Def, p, v)

	def _on_robot_info(self):
		r = miio.Vacuum(self._robot_ip, self._robot_tocken)
		self.showInfo(str(r.raw_command('get_status', [])))

	def _on_robot_info_sound(self):
		r = miio.Vacuum(self._robot_ip, self._robot_tocken)
		self.showInfo(str(r.raw_command('get_sound_progress', [])))



	def _on_make(self):
		try:
			t = Transport(self._rows)
			data = t.create()

			file = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', '*.pkg')[0]
			if file:
				if file[-4:] != '.pkg':
					file += '.pkg'

				with open(file, 'wb') as f:
					f.write(data)

		except Exception as e:
			self.showInfo(str(e))


	def _on_server_start(self):
		server_worker = Server(self._server_ip, self.showInfo)
		server_worker.start()

		self._server_worker = server_worker
		self._server_check_state()


	def _on_server_stop(self):
		if self._server_worker:
			self._server_worker.stop()
			self._server_worker = None
			self._server_check_state()


	def _server_check_state(self):
		self.btn_server_start.setEnabled(True if self._server_ip and not self._server_worker else False)
		self.btn_server_stop.setEnabled(True if self._server_worker else False)
		self.btn_server_send.setEnabled(True if self._server_worker and self._server_file else False)

	def _on_server_ip(self, ip):
		self._server_ip = ip
		self._set_conf_param('server_ip', ip)
		self._server_check_state()

	def _on_server_file(self):
		file = QFileDialog.getOpenFileName(self, 'Выберите pkg файл', '', '*.pkg')[0]

		self._server_file = file
		self._set_conf_param('server_file', file)
		self.l_server_file.setText(os.path.basename(file))
		self._server_check_state()

	def  _on_server_send(self):
		copyfile(self._server_file, '_.pkg')
		url = 'http://' + self._server_ip + '/_.pkg'

		r = miio.Vacuum(self._robot_ip, self._robot_tocken)
		result = r.raw_command('dnld_install_sound', [{"url":url, "sver":1, "md5":"fc8f45999775089449019df9dbc3b2a9", "sid":3}])
		self.showInfo(str(result))


	def _on_robot_ip(self, ip):
		self._robot_ip = ip
		self._set_conf_param('robot_ip', ip)
		self._robot_check_state()


	def _on_robot_tocken(self, tocken):
		self._robot_tocken = tocken
		self._set_conf_param('robot_tocken', tocken)
		self._robot_check_state()


	def _robot_check_state(self):
		self.btn_robot_info.setEnabled(True if self._robot_ip and self._robot_tocken else False)
		self.btn_robot_info_sound.setEnabled(True if self._robot_ip and self._robot_tocken else False)


	def _addRow(self, n):
		row = Row()
		row.setBaseInfo(n, self._cfg)

		listWidget = QListWidgetItem(self.list_rows)

		listWidget.setSizeHint(row.size())
		self.list_rows.addItem(listWidget)
		self.list_rows.setItemWidget(listWidget, row)

		self._rows.append(row)


	def showInfo(self, msg):
		l = self.list_info_model.stringList()
		l.append(msg)
		self.list_info_model.setStringList(l)
		self.list_info.scrollToBottom()

	def end(self):
		with open(config_name, 'w') as f:
			self._cfg.write(f)

		self._on_server_stop()




def main():
	app = QApplication(sys.argv)
	window = WindowApp()
	window.show()
	app.exec_()

	window.end()


if __name__ == '__main__':
	main()