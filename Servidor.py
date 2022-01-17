import sys, socket, threading,re
from threading import Semaphore
from collections import OrderedDict
MSG_DESCONEXION = "#salir"
lista_usuarios = []
lista_clientes=[]
contactos = []
PCG_dado = 0

class Servidor:

	"""
	Constructor de la clase Servidor
	"""
	def __init__(self):
		self.clientes =[]
		self.lista_usuarios = []
		self.nombres_clientes=[]
		self.servidor = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.servidor.bind(('localhost',1080))
		print("Iniciando servidor")
		self.servidor.listen()
		self.servidor.setblocking(False)
		print("¡El servidor ha iniciado con éxito!")
		aceptar = threading.Thread(target=self.aceptarCon)
		procesar = threading.Thread(target=self.manejador_cliente)
		aceptar.daemon = True
		aceptar.start()

		procesar.daemon = True
		procesar.start()

		while True:
			msg = input('->')
			lista_msg = msg.split()
			if msg == MSG_DESCONEXION:
				self.servidor.close()
				sys.exit()
			elif lista_msg[0] == "@msg":
				msg = msg.replace("msg","")
				self.mandar_a_todos(msg,self.servidor,"servidor")
			elif lista_msg[0] == "@respd":
				msg = msg.replace(lista_msg[0],"")
				msg = msg.replace(lista_msg[1],"")
				msg = "servidor te ha enviado un mensaje:" + msg
				cliente_temp = self.buscarCliente(lista_msg[1])
				if cliente_temp == 'ninguno':
					print("ERROR: Usuario no encontrado, intenta de nuevo...")
				else:
					cliente_temp.send(msg.encode())
					#c.send(("@respd " + lista_res[0] + " " + respuesta).encode())
			elif lista_msg[0] == "@usuarios":
				usrs = str(self.lista_usuarios)
				self.mandar_a_todos(usrs,self.servidor,"servidor")
			else:
				pass

	"""
	Función auxiliar que envía un mensaje dado a los demás usuarios conectados al servidor
	"""
	def mandar_a_todos(self, msg, cliente,nombre):
		for c in self.clientes:
			try:
				if c != cliente:
					c.send((nombre + " a todos:" + msg).encode())
			except:
				self.clientes.remove(c)

	"""
	Función que acepta las nuevas conexiones al servidor
	"""
	def aceptarCon(self):
		print("aceptarCon iniciado")
		while True:
			try:
				cliente, direccion = self.servidor.accept()
				cliente.setblocking(False)
				self.clientes.append(cliente)
			except:
				pass

	"""
	Función auxiliar que recibe el nombre de un usuario y retorna el socket cliente correspondiente,
	 en caso contrarió devuelve un mensaje
	"""
	def buscarCliente(self,nombre):
		for i in self.nombres_clientes:
			if nombre == i[0]:
				return i[1]
		return 'ninguno'

	def buscar_nombre_cliente(self,nombre):
		for i in self.nombres_clientes:
			if nombre == i[0]:
				return i[0]
		return 'ninguno'
	
	def buscarContactos(self,nombre):
		contactos_personales = []
		#print(contactos)
		#print("aaaa")
		for i in contactos:
			#print("HIJOLE"+str(i[0]))
			if nombre == i[0]:
				contactos_personales.append(str(i[1]) + "|" + str(i[2]))
		return contactos_personales

	"""
	Función que recorre la lista de clientes para recoger sus mensajes y análizar estos para dar una
	respuesta apropiada para cada uno
	"""
	def manejador_cliente(self):
		print("Manejador de clientes iniciado")
		while True:
			if len(self.clientes) > 0:
				for c in self.clientes:
					try:
						respuesta = c.recv(1024)
						if respuesta:
							respuesta = respuesta.decode('UTF-8')
							print("cliente respondio >> " + str(respuesta))
							lista_res = respuesta.split()
							print(respuesta)
							if lista_res[1] == "#cliente":
								respuesta = re.sub(f"\#cliente|\'|\ {lista_res[2]}","",respuesta)
								respuesta = respuesta.replace(lista_res[0],"")
								msg = lista_res[0] + " te ha enviado un mensaje:" + respuesta
								cliente_temp = self.buscarCliente(lista_res[2])
								if cliente_temp == 'ninguno':
									c.send(("ERROR: Usuario no encontrado, intenta de nuevo...").encode())
								else:
									cliente_temp.send(msg.encode())
									c.send(("@respd " + lista_res[0] + " " + respuesta).encode())
							elif lista_res[1] == "#usuarios":
								c.send(("@lista " + str(self.lista_usuarios)).encode())
							elif lista_res[1] == "#nombre":
								print(respuesta)
								lista_nombre_correo = respuesta.split("|")
								print(str(lista_nombre_correo))
								self.lista_usuarios.append((str(lista_nombre_correo[1]),str(lista_nombre_correo[2])))
								print(str(self.lista_usuarios))
								self.nombres_clientes.append((str(lista_res[0]), c))
								usrs = str(self.lista_usuarios)
								c.send(usrs.encode())
								conts = str(self.buscarContactos(lista_res[0]))
								c.send(("@contactos " + conts).encode())
								c.send(("Para desplegar la lista de comandos escribe #ayuda").encode())
							elif lista_res[1] == "#bloquear":
								c.send(("Has bloqueado al usuario " + lista_res[2] + "").encode())
								cliente_temp = self.buscarCliente(lista_res[2])
								cliente_temp.send(("El usuario " + lista_res[0] + " te ha bloqueado, no puedes mandarle más mensajes").encode())
							elif lista_res[1] == "#desbloquear":
								c.send(("Has desbloqueado al usuario " + lista_res[2] + "").encode())
								cliente_temp = self.buscarCliente(lista_res[2])
								cliente_temp.send(("El usuario " + lista_res[0] + " te ha desbloqueado").encode())
							elif lista_res[1] == "#ayuda":
								c.send(("\nLista de comandos:\n1) #cliente [destinatario] [tu_mensaje] (para enviar un mensaje a algún usuario en específico)\n2) #usuarios (para desplegar la lista de usuarios)\n3) #ayuda (para desplegar comandos)\n4) #agregar_contacto [correo_del_contacto] [probabilidad_de_contacto] (para agregar un contacto) \n6) #lista_contactos (Para obtener la lista de tus contactos y su PCT) \n5) #salir (para salir de la aplicación)").encode())
							elif lista_res[1] == "#agregar_contacto":
								
								cliente_temp = self.buscar_nombre_cliente(lista_res[2])
								if cliente_temp != 'ninguno':
									
									contactos.append((lista_res[0],cliente_temp,lista_res[3]))
									
									c.send(("Se ha agregado exitosamente a tu nuevo contacto \n").encode())
									#print(contactos)
									conts = str(self.buscarContactos(lista_res[0]))
									c.send(("@contactos " + conts).encode())
								else:
									c.send(("ERROR: no se encontro el usuario").encode())
							elif lista_res[1] == "#lista_contactos":
								#print(contactos)
								#print(self.buscarContactos(lista_res[0]))
								conts = str(self.buscarContactos(lista_res[0]))
								c.send(("@contactos " + conts).encode())
							elif lista_res[1] == "#pedir_PCG":
								msg = "@pedir_PCG " + lista_res[0]
								cliente_temp = self.buscarCliente(lista_res[2])
								if cliente_temp == 'ninguno':
									
									c.send(("ERROR: Usuario no encontrado, intenta de nuevo...").encode())
								else:
									print("Voy a mandar: " + msg + " a " + str(cliente_temp))
									cliente_temp.send(msg.encode())
									print("Ya se lo envie")
									#c.send(("@respd " + lista_res[0] + " " + respuesta).encode())
							elif lista_res[1] == "#PCG":
								msg = "@PCG_dado " + lista_res[2] + " " + lista_res[0]
								cliente_temp = self.buscarCliente(lista_res[3])
								if cliente_temp == 'ninguno':
									c.send(("ERROR: Usuario no encontrado, intenta de nuevo...").encode())
								else:
									print("Voy a mandar: " + msg)
									cliente_temp.send(msg.encode())
							elif lista_res[1] == "#salir":
								nombre_c = ""
								for parte in lista_res[2:]:
									nombre_c = nombre_c + " " + parte
								print((nombre_c[1:],str(lista_res[0])))
								self.lista_usuarios.remove((nombre_c[1:],lista_res[0]))
							else:
								respuesta = respuesta.replace(lista_res[0], "")
								self.mandar_a_todos(respuesta,c,lista_res[0])
								c.send(("@resp texto").encode())
							print("@ok")
					except:
						pass

	
if len(sys.argv) < 2:
	print("se esperaban banderas")
elif sys.argv[1] == "-s" :
	Servidor()
else:
	print("bandera no reconocida")
