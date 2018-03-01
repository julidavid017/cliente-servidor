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
group = ""

# funcion para enviar los mensajes al servidor
def request(req_socket, msg):
	audio = pyaudio.PyAudio()
	stream = audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
	while True:
		# enviamos el audio
		# iniciamos la grabacion
		message = stream.read(CHUNK)
		req_socket.send_json({"op": "inContact", "destination": group, "message": message.decode('UTF-16', 'ignore')})
		req_socket.recv_string()
	stream.stop_stream()
	stream.close()
	audio.terminate()
	
# funcion para recibir los mensajes del servidor
def reply(rep_socket, req_socket):
	# esperamos mensajes
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=True)
	while True:
		msg = rep_socket.recv_json() # capturamos el mensaje
		if msg["op"] == "confirm": # si el mensaje se confirma la llamada
			# lanzamos el hilo para comenzar a enviar informacion
			threading.Thread(target = request, args = (req_socket, "")).start()
			rep_socket.send_string("ok")
		elif msg["op"] == "inContact": # si ya estan conectados
			#reproducimos el audio
			stream.write(msg["message"].encode('UTF-16','ignore'))
			#print("{}: {}".format(username, msg["message"]))
			rep_socket.send_string("ok")
		else:
			rep_socket.send_string("ok")
	stream.stop_stream()
	stream.close()
	p.terminate()
	


def options(user, req_socket):
	global group
	print("Bienvenido a el chat super chat")
	print("1. hacer una llamada")
	print("0. salir")

	option = input("ingrese opcion: ")
	if option == "1":
		# si se quiere llamar a alguien, solicitamos el usuario al cual desea contactar
		group = input("ingrese el nombre del grupo: ")
		# mandamos la solicitud al usuario
		req_socket.send_json({"op": "group", "origin": user, "destination": group})
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
	# inicializamos  el socket (esperamos conexiones)
	rep_socket.bind("tcp://*:{}".format(myport))
	# nos registramos en el servidor
	req_socket.send_json({"op":"register", "user": user, "ip": myip, "port": myport})
	req_socket.recv_string()
	# lanzamos el hilo para esuchar los mensajes del servidor
	threading.Thread(target = reply, args = (rep_socket, req_socket)).start()
	# mostramos el menu
	options(user, req_socket)
	

# inicializamos la funcion main
if __name__ == '__main__':
	main()
