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

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
 #variables globales
username = ""
isInContact = False

# funcion para enviar los mensajes al servidor
def request(req_socket, user):
	while True:
		# mientras esten conectados
		if isInContact == True:
			# enviamos el audio
			audio = pyaudio.PyAudio()
 			# start Recording
			stream = audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
			message = stream.read(CHUNK)
			req_socket.send_json({"op": "inContact", "destination": username, "message": message})
			req_socket.recv_string()
	stream.stop_stream()
	stream.close()
	audio.terminate()
# funcion para recibir los mensajes del servidor
def reply(rep_socket, req_socket, user):
	# uso de variables globales
	global username
	global isInContact
	# esperamos mensajes
	while True:
		msg = rep_socket.recv_json() # capturamos el mensaje
		if msg["op"] == "contact": # si la operacion es contact
			# preguntamos al usuario si desea aceptar la llamada
			print("{} quiere conectarse contigo, ¿aceptas? (s/n)".format(msg["origin"]))
			# capturamos la respuesta
			answer = input("respuesta conexion >> ")
			# enviamos la respuesta al servidor
			rep_socket.send_string(answer)
		elif msg["op"] == "confirm": # si el mensaje se confirma la llamada
			# asignamos el nombre de usuario de destino a quien nos contacta
			username = msg["destination"]
			# nos ponemos en estado de llamada aactiva
			isInContact = True
			# lanzamos el hilo para comenzar a enviar informacion
			threading.Thread(target = request, args = (req_socket, user)).start()
			rep_socket.send_string("ok")
		elif msg["op"] == "inContact": # si ya estan conectados
			#reproducimos el audio
			p = pyaudio.PyAudio()
			stream = p.open(format=pyaudio.paInt16,
		                channels=CHANNELS,
		                rate=RATE,
		                output=True)
			stream.write(msg["message"])
			print("{}: {}".format(username, msg["message"]))
			rep_socket.send_string("ok")
		else:
			rep_socket.send_string("ok")
	stream.stop_stream()
	stream.close()
	p.terminate()


def options(user, req_socket):
	print("Bienvenido a el chat super chat")
	print("1. hacer una llamada")
	print("0. salir")

	option = input("ingrese opcion: ")
	if option == "1":
		# si se quiere llamar a alguien, solicitamos el usuario al cual desea contactar
		username = input("ingrese el nombre de usuario a contactar: ")
		# mandamos la solicitud al usuario
		req_socket.send_json({"op": "contact", "origin": user, "destination": username})
		req_socket.recv_string()
	elif option == "0":
		exit()
	elif option == "s":
		print("Confirme su respuesta (s/n)")
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
	# inicializamos  el socket (esperamos conexiones)
	rep_socket.bind("tcp://*:{}".format(myport))
	# nos registramos en el servidor
	req_socket.send_json({"op":"register", "user": user, "ip": myip, "port": myport})
	req_socket.recv_string()
	# lanzamos el hilo para esuchar los mensajes del servidor
	threading.Thread(target = reply, args = (rep_socket, req_socket, user)).start()
	# mostramos el menu
	options(user, req_socket)
	

# inicializamos la funcion main
if __name__ == '__main__':
	main()
