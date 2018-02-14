import zmq
import sys
import time
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
	# creamos un socket
	s = context.socket(zmq.REQ)
	# nos conectamos al servidor a traves de socket por medio de tcp
	s.connect("tcp://{}:{}".format(ip, port))
	# mostramos un mensaje de confirmacion
	print("Connecting to server {} at {}".format(ip, port))

	# si la operacion es listar
	if operation == "list":
		# hacemos la peticion al servidor para listar
		s.send_json({"op": "list"})
		# cargamos la respuesta del servidor en files
		files = s.recv_json()
		# mostramos la lista de archivos
		print(files)
	# si la operacion es descargar
	elif operation == "download":
		# solicitamos el nombre del archivo
		name = input("File to download? ")
		# hacemos la solicitud al servidor pidiendo el numero de partes del archivo
		s.send_json({"op": "fileparts", "file": name})
		# obtenemos dicho valor
		numberParts = s.recv_json()
		if type(numberParts) == str:
			print(numberParts)
			exit()
		part = 0 # indice para solicitar partes
		# creamos un nuevo archivo, donde almacenaremos las partes enviadas por el servidor
		# para recrear el archivo original
		start = time.time() # hora de inicio de descarga del archivo
		with open(name, "wb") as output:
			# mientras el indice sea menor al numero de partes del archivo 
			while (part < numberParts):
				# solicitamos la parte correspondiente al servidor
				s.send_json({"op": "download", "file": name, "part": part})
				# recibimos esa parte
				file = s.recv()
				# escribimos dicha parte en el archivo creado
				output.write(file)
				# incrementamos el indice
				part +=1
		end = time.time() # hora de finalizacion de descarga del archivo
		print(end - start) # mostramos cuanto tiempo se tardo la descarga
	else: # si la operacion no existe
		print("Error!!!, unsupported operation")

# inicializamos la funcion main
if __name__ == '__main__':
	main()
