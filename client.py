import zmq
import sys
import time
import threading
import pyaudio
import socket

get_myip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
get_myip.connect(("gmail.com",80))
myip = get_myip.getsockname()

def request():
	while True:
		req_socket.send_json()
		req_socket.recv_string()

def reply():
	while True:
		rep_socket.recv_json()
		rep_socket.send_sting()

# Funcion main
def main():
	# verificamos la cantidad de parametros
	if len(sys.argv) != 4:
		# si faltan argumentos mostramos un error
		print("Error 404")
		# salimos
		exit()
	# recogiendo datos de conexion
	ip = sys.argv[1] # ip del servidor
	port = sys.argv[2] # puerto del servidor
	operation = sys.argv[3] # operacion a realizar

	# creamos un contexto para la conexion (por ahora es magico)
	context = zmq.Context()
	# creamos un socket de tipo request
	req_socket = context.socket(zmq.REQ)
	# nos conectamos al servidor a traves de socket por medio de tcp
	req_socket.connect("tcp://{}:{}".format(ip, port))
	# creamos un socket de tipo reply
	rep_socket = context.socket(zmq.REP)
	rep_socket.bind("tcp://*:{}".format(1234))

	print("Connecting to server {} at {}".format(ip, port))
	req_socket.send_json({"op":"register", "user": operation, "ip": myip[0], "port": 1234})
	print(req_socket.recv_string())

# inicializamos la funcion main
if __name__ == '__main__':
	main()
