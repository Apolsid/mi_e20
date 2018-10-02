from http.server import HTTPServer, SimpleHTTPRequestHandler
import argparse, zlib, sys, pathlib


class Transport(object):
	_head_tag = b'\xca5U<aud\x00'
	_pack = None
	
	_path = None

	_rnd = b'\x00\x00\x00\x00'
	_rnd_len = 4

	def __init__(self, path):
		self._path = path

	def _getHash(self, pack_data):
		h = zlib.crc32(pack_data)
		return 0xffffffff - h

	def create(self):
		if self._pack == None:
			self._pack = Pack(self._path);

		pack_data = self._pack.create()

		data = b''
		data += self._head_tag
		data += (len(pack_data) + self._rnd_len).to_bytes(4, byteorder='little')
		data += self._rnd + pack_data

		data += (self._getHash(pack_data)).to_bytes(8, byteorder='little')

		return data



class Pack(object):
	_head_tag = b'sdns'
	_id = b'\x03\x00\x00\x00'
	_version = b'\x01\x00\x00\x00'
	_const_0 = b'm\x00\x00\x00'
	_const_1 = b'\xcb\x01\x00\x00'

	_len_head = 0x20
	_len_table_head = 0x3E0
	_path = None

	_count = 109

	def __init__(self, path):
		self._path = path

	def _getArr(self):
		i = 0
		arr = list()
		while i < self._count:
			with open(self._path + '/' + str(i) + '.mp3', 'rb+') as f:
				data = f.read()
				arr.append(data)

			i += 1

		return arr
	
	def _createContent(self):
		arr = self._getArr()

		table_head = bytearray(self._len_table_head)
		table_body = b''

		offset = self._len_head + self._len_table_head
		for i in range(len(arr)):
			len_item = len(arr[i])

			table_head[i*8 : i*8 + 8] = offset.to_bytes(4, byteorder='little') + len_item.to_bytes(4, byteorder='little')
			table_body += arr[i]

			offset += len_item
			pass

		content = table_head + table_body;
		return content


	def create(self):
		content = self._createContent()

		head = bytearray(self._len_head)
		head[0x0:0x4] = self._head_tag
		head[0x4:0x8] = self._id
		head[0x8:0xC] = self._const_0
		head[0xC:0x10] = (len(content) - self._len_table_head).to_bytes(4, byteorder='little')
		head[0x10:0x14] = self._const_1
		head[0x14:0x18] = self._version

		return head + content




len_head = 0x410
begin_arr = 0x30
offset_arr = 0x10


def unpack(path_out, path_file):
	with open(path_file, 'rb+') as f:
		data = f.read()

		arr = data[begin_arr: len_head - begin_arr]
		list_file = list()
		i = 0x0;

		while True:
			if len(arr) == i:
				break

			item_begin = offset_arr + int.from_bytes(arr[i: i + 4], byteorder='little')
			item_len = int.from_bytes(arr[i + 4: i + 8], byteorder='little')

			if item_len > 0:
				list_file.append([item_begin, item_len])

			i += 8


		pathlib.Path(path_out).mkdir(parents=True, exist_ok=True) 

		for i in range(len(list_file)):
			item = list_file[i]
			with open(path_out + '/' + str(i) + '.mp3', 'wb') as f:
				f.write(data[item[0] : item[0] + item[1]])



def pack(path):
	t = Transport(path)
	data = t.create()

	with open('out.pkg', 'wb') as f:
		f.write(data)



class MyRequestHandler(SimpleHTTPRequestHandler):
	protocol_version = "HTTP/1.1"

def serv(ip, port):
	server = HTTPServer((ip, port), MyRequestHandler)
	print('***run http server***')
	server.serve_forever()




def run():
	task = sys.argv[1]

	if task == 'pack':
		parser = argparse.ArgumentParser()
		parser.add_argument('type', help='type task')
		parser.add_argument('-p', dest='path', help='path for list mp3', type=str, default='out')
		arg = parser.parse_args()
		pack(arg.path)

	elif task == 'unpack':
		parser = argparse.ArgumentParser()
		parser.add_argument('type', help='type task')
		parser.add_argument('-p', dest='path_out', help='path for list mp3', type=str, default='out')
		parser.add_argument('-f', dest='path_file', help='path for file', type=str, default=None)
		arg = parser.parse_args()
		unpack(arg.path_out, arg.path_file)

	elif task == 'serv':
		parser = argparse.ArgumentParser()
		parser.add_argument('type', help='type task')
		parser.add_argument('--ip', dest='ip', help='ip', type=str, default='127.0.0.1')
		parser.add_argument('--port', dest='port', help='port', type=int, default=7777)
		arg = parser.parse_args()
		serv(arg.ip, arg.port)



if __name__ == '__main__':
	run()