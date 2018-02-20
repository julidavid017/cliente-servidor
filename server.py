import zmq
import sys
import os
import math

connected_users = {}

def main():
	# si el numero de argumentos es diferente del numero de parametros
	if len(sys.argv) != 3:
		# mostramos un mensaje de error
		print("Error!!!")
		exit()
	# recogemos los datos para arrancar el servidor
	directory = sys.argv[2] # directorio donde se encuentran los archivos
	port = sys.argv[1] # puerto de conexion
	part_size = 1024*1024 # tamaño en MB

	# creamos un contexto para la conexion (por ahora es magico)
	context = zmq.Context()
	# creamos un socket tcp
	s = context.socket(zmq.REP)
	# le decimos al socket que escuche el pueto recibido como parametro
	s.bind("tcp://*:{}".format(port)) # El asterisco representa la interfaz de red por defecto
	# dejamos el servidor esperando mensajes
	while True:
		# capturamos el mensaje
		msg = s.recv_json()
		if(msg["op"] == "register"):
			us_ip = msg["ip"]
			us_port = msg["port"]
			user = msg["user"]
			us_socket = context.socket(zmq.REQ)
			us_socket.connect("tcp://{}:{}".format(us_ip, us_port))
			connected_users[user] = us_socket
			s.send_string("ok")
		print(len(connected_users))
		

# inicializamos la funcion main
if __name__ == '__main__':
	main()