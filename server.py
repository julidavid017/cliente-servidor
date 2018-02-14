import zmq
import sys
import os
import math

# funcion para la carga de los archivos
def loadFiles(path):
	# declaramos un nuevo diccionario
	files = {}
	dataDir = os.fsencode(path)
	for file in os.listdir(dataDir):
		filename = os.fsdecode(file)
		print("Loading {}".format(filename))
		files[filename] = file
	return files

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
	# cargamos todos los archivos que hay en el direcctorio recibido como parametro
	files = loadFiles(directory)
	# dejamos el servidor esperando mensajes
	while True:
		# capturamos el mensaje
		msg = s.recv_json()
		# si la operacion es listar
		if msg["op"] == "list":
			# enviamos una lista de los archivos que cargamos anteriormente
			s.send_json({"files": list(files.keys())})
		# si el mensaje es descargar
		elif msg["op"] == "download":
			# capturamos el nombre del archivo y la parte a enviar de ese archivo
			filename = msg["file"] # nombre archivo
			part = msg["part"] # parte del archivo
			# verificamos que el archivo exista
			if filename in files:
				# si existe, abrimos el archivos
				with open(directory + filename, "rb") as input:
					# posicionamos el puntero al inicio de la parte solicitada
					input.seek(part_size*part)
					# leemos tantos MB como lo indique el tamaño a partir de dicha posicion
					data = input.read(part_size)
					# enviamos la parte al cliente
					s.send(data)
			else: # si no existe
				# enviamos un mensaje de error
				s.send_json("File not found")
		# si la operacion es enviar el numero de partes
		elif msg["op"] == "fileparts":
			# capturamos el nombre del archivo
			filename = msg["file"]
			# verificamos si existe el archivo
			if filename in files:
				# si existe, le solicitamos al sistema operativo el tamaño de ese archivo en Bytes
				size = os.stat(directory + filename).st_size
				# tomamos esa cantidad de bytes y las convertimos a MBs
				size = (size / part_size)
				# redondeamos el numero de MBs al entero mas proximo por encima, para representar el numero de partes
				size = math.ceil(size)
				# enviamos ese valor al cliente
				s.send_json(size)
			else: # si el archivo no existe
				# enviamos un mensaje de error
				s.send_json("File not found")
		else:# si la operacion no esta definida
			# mostramos un mensaje de error
			print("Unsupported action")

# inicializamos la funcion main
if __name__ == '__main__':
	main()