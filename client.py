import zmq
import sys
import time
import threading
import pyaudio
import socket

#-------- trucazo para obtener la ip de la interfaz utilizada en linux ------#
#get_myip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#get_myip.connect(("gmail.com",80))
#myip = get_myip.getsockname()

username = ""
isInContact = False

# funcion para enviar los mensajes al servidor
def request(req_socket, user):
	while True:
		if isInContact == True:
			message = input("send: ")
			req_socket.send_json({"op": "inContact", "destination": username, "message": message})
			req_socket.recv_string()
# funcion para recibir los mensajes del servidor
def reply(rep_socket, req_socket, user):
	global username
	global isInContact
	while True:
		msg = rep_socket.recv_json()
		if msg["op"] == "contact":
			print("{} quiere conectarse contigo, ¿aceptas? (s/n)".format(msg["origin"]))
			answer = input("respuesta conexion >> ")
			rep_socket.send_string(answer)
		elif msg["op"] == "confirm":
			username = msg["destination"]
			isInContact = True
			threading.Thread(target = request, args = (req_socket, user)).start()
			rep_socket.send_string("ok")
		elif msg["op"] == "inContact":
			print("{}: {}".format(username, msg["message"]))
			rep_socket.send_string("ok")
		else:
			rep_socket.send_string("ok")


def options(user, req_socket):
	print("Bienvenido a el chat super chat")
	print("1. hacer una llamada")
	print("0. salir")

	option = input("ingrese opcion: ")
	if option == "1":
		username = input("ingrese el nombre de usuario a contactar: ")
		req_socket.send_json({"op": "contact", "origin": user, "destination": username})
		req_socket.recv_string()
	elif option == "0":
		exit()
	else:
		print("Error!!!")


# Funcion main
def main():
	# verificamos la cantidad de parametros
	# formato de entrada: <serverip> <serverport> <username> <clientip> <clientport>
	if len(sys.argv) != 6:
		# si faltan argumentos mostramos un error
		print("Error 404")
		# salimos
		exit()
	# recogiendo datos de conexion
	ip = sys.argv[1] # ip del servidor
	port = sys.argv[2] # puerto del servidor
	user = sys.argv[3] # nombre de usuario
	myip = sys.argv[4] # ip cliente
	myport = sys.argv[5] # puerto cliente

	# creamos un contexto para la conexion (por ahora es magico)
	context = zmq.Context()
	# creamos un socket de tipo request
	req_socket = context.socket(zmq.REQ)
	# nos conectamos al servidor a traves de socket por medio de tcp
	req_socket.connect("tcp://{}:{}".format(ip, port))
	# creamos un socket de tipo reply
	rep_socket = context.socket(zmq.REP)
	rep_socket.bind("tcp://*:{}".format(myport))
	req_socket.send_json({"op":"register", "user": user, "ip": myip, "port": myport})
	req_socket.recv_string()
	threading.Thread(target = reply, args = (rep_socket, req_socket, user)).start()

	options(user, req_socket)
	

# inicializamos la funcion main
if __name__ == '__main__':
	main()
