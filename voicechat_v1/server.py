import zmq
import sys
import os
import math

connected_users = {}

def main():
	# si el numero de argumentos es diferente del numero de parametros
	# formato: <serverport>
	if len(sys.argv) != 2:
		# mostramos un mensaje de error
		print("Error!!!")
		exit()
	# recogemos los datos para arrancar el servidor
	port = sys.argv[1] # puerto de conexion

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
		if msg["op"] == "register":
			us_ip = msg["ip"]
			us_port = msg["port"]
			user = msg["user"]
			us_socket = context.socket(zmq.REQ)
			us_socket.connect("tcp://{}:{}".format(us_ip, us_port))
			connected_users[user] = us_socket
			s.send_string("ok")
		elif msg["op"] == "contact":
			origin = msg["origin"]
			destination = msg["destination"]
			if connected_users.get(destination) != None:
				s.send_string("ok")
				destination_s = connected_users[destination]
				destination_s.send_json({"op": "contact", "origin": origin})
				answer = destination_s.recv_string()
				if answer == "s":
					origin_s = connected_users[origin]
					origin_s.send_json({"op": "confirm", "destination": destination})
					origin_s.recv_string()
					destination_s.send_json({"op": "confirm", "destination": origin})
					destination_s.recv_string()
		elif msg["op"] == "inContact":
			destination = msg["destination"]
			s.send_string("ok")
			destination_s = connected_users[destination]
			destination_s.send_json(msg)
			destination_s.recv_string()
		
# inicializamos la funcion main
if __name__ == '__main__':
	main()