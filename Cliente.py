import sys, socket, threading,re,random
from threading import Semaphore
from collections import OrderedDict
MSG_DESCONEXION = "#salir"
lista_contactos = []
existe_contacto = False
PCG = 0
usuario = ""


class Cliente:

	"""
	Función auxiliar que recibe todos los mensajes que son enviados para el usuario desde el servidor
	"""
	def recibir_mensaje(self):
		self.contactos = []
		self.PCG_pedido = 0
		while True:
			try:
				respuesta = self.cliente.recv(1024)
				if respuesta:
					
					respuesta = respuesta.decode('UTF-8')
					lista_res = respuesta.split()
					if lista_res[0] in self.bloqueados:
						print("\n>> Un usuario que bloqueaste ha intentado mandarte mesaje...")
					#elif lista_res[0] = "#existe_contacto":
						#existe_contacto = bool(lista_res[1])
					elif lista_res[0] == "@contactos":
						#print(respuesta)
						#print("bbbbbbbbbb")
						if lista_res[1] == "[]":
							self.contactos = []
						else:
							self.contactos = respuesta[12:len(respuesta)-1].split(", ")
						print("Tus contactos son: " + str(self.contactos))
						#print(str(self.contactos[0]))
						#("['miguel@gmail', 'regi@gmail', 'sedesoolso@gmail.com']")[2:len(mensaje-2)].split("', '")
					elif lista_res[0] == "@pedir_PCG":
						#print("Me piden pcg")
						#print(self.estado)
						#print(self.actual)
						#print(self.dar_pcg(self.actual))
						self.cliente.send((self.actual + " #PCG " + str(self.dar_pcg(lista_res[1])) + " " + lista_res[1]).encode())
					elif lista_res[0] == "@PCG_dado":
						#print("Ya me dieron su PCG")
						self.PCG_pedido = lista_res[1]
						self.lista_PCG_contactos.append((lista_res[2],lista_res[1]))
						#print(self.lista_PCG_contactos)
					else:
						print("\n>> " + respuesta + "\n")
			except:
				pass
	
	def dar_pcg (self,contacto_emisor):
		suma = 0
		if self.estado == "muy mal" or self.estado == "mal":
			return 1
		if self.estado == "bien":
			return 0.1
		if len(self.contactos) in [0,1]:
			return random.uniform(0.2, 0.6)
		#for contacto in self.contactos:
			#if contacto != contacto_emisor:
				#suma = suma + float(contacto.split("|")[1][:3])*self.pedirPCG(contacto.split("|")[0][1:])
				#print("hola")
		#obtener resultado
		suma = self.probabilidad_de_contagio(contacto_emisor)
		return (suma / len(self.contactos))
	
	def pedirPCG(self,contacto):
		print("--Voy a pedirle el contacto a: " + str(contacto))
		self.cliente.send((str(self.actual) +" #pedir_PCG "+ contacto).encode())
		return self.PCG_pedido
	
	def obtenerPCG(self,contacto_emisor):
		contador = 0
		self.contactos_completos = []
		self.lista_PCG_contactos = []
		#print("Paso 0")
		#print("LISTA PCG: " + str(self.lista_PCG_contactos))
		#print("LISTA contactos PCT: " + str(self.contactos))
		for contacto in self.contactos:
			#print("--------> " + str(contacto.split("|")[0][1:]) + str(contacto_emisor))
			if contacto.split("|")[0][1:] != contacto_emisor:
				self.pedirPCG(contacto.split("|")[0][1:])
				#print("paso1")
		while len(self.lista_PCG_contactos) != len(self.contactos):
			contador = contador +1 
		#print("paso2")
		#print("LISTA PCG: " + str(self.lista_PCG_contactos))
		#print("LISTA contactos PCT: " + str(self.contactos))
		for i in self.contactos:
			#self.lista_PCG_contactos[self.lista_PCG_contactos.index(i.split("|")[0])]
			#self.contactos_completos.append()
			for j in self.lista_PCG_contactos:
				if i.split("|")[0][1:] == j[0]:
					self.contactos_completos.append((j[0],i.split("|")[1],j[1]))
		#print(self.contactos_completos)
		return self.contactos_completos	

	def probabilidad_de_contagio(self,contacto_emisor):
		suma = 0

		lista = self.obtenerPCG(contacto_emisor)
		#print("ajua")
		#print(self.contactos)
		for contacto in lista:
			print("El if: " + contacto[0] + contacto_emisor)
			if contacto[0] != contacto_emisor:
			#suma = suma + float(contacto.split("|")[1][:3])*self.pedirPCG(contacto.split("|")[0][1:])
				suma = suma + float(contacto[1][:3])*float(contacto[2][:3])
		#print("ajua2")
		if len(self.contactos) != 0:
			return (suma / len(self.contactos))
		return suma


	def analizar_respuesta(self,mensaje):
		if mensaje == "muy bien":
			return self.probabilidad_de_contagio("")
		elif mensaje == "bien":
			return 0.1
		elif mensaje in ["mal","muy mal"]:
			return 1


	"""
	Constructor de la clase Cliente
	"""
	def __init__(self, hostname, puerto, usuario):
		self.cliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		print("Conectando al servidor con el nombre: " + str(usuario))
		self.cliente.connect((hostname, puerto))
		print('¡Te has conectado en el servidor!')
		self.nombre_completo = input("Registrate con tu nombre completo\n")
		self.correo = input("Ingresa tu correo electronico\n")
		usuario = self.correo
		self.actual = self.correo
		self.estado = "bien"
		self.lista_PCG_contactos = []
		self.contactos_completos = []
		self.cliente.send((usuario + " #nombre |" + self.nombre_completo + "|" + self.correo).encode())

		#print("<<Para mandar mensajes escribe directamente en la terminal>>")
		
		
		#print()
		

		msg_recv = threading.Thread(target=self.recibir_mensaje)

		msg_recv.daemon = True
		msg_recv.start()
		self.bloqueados = []
		print("Escribe como te sientes actualmente: \n a) muy bien \n b) bien \n c) mal \n d) muy mal \n (Escribe la palabra, no la letra de la opción) \n <<Para obtener ayuda sobre los comandos escribe en la terminal #ayuda>>\n Lista de usuarios conectados actualmente:")
		while True:
			mensaje = input()
			lista_msg = mensaje.split()
			if mensaje != MSG_DESCONEXION:
				if lista_msg[0] == "#bloquear":
					self.bloqueados.append(lista_msg[1])
				elif lista_msg[0] == "#desbloquear":
					self.bloqueados.remove(lista_msg[1])
				#elif lista_msg[0] = "#agregar_contacto":
				#	agregar_contacto(lista_msg[1])
				elif mensaje.lower() in ["muy bien", "bien", "mal", "muy mal"]:
					#self.analizar_respuesta(mensaje)
					print("Has introducido exitosamente tu estado")
					self.estado = mensaje.lower()
				
					print("Tu probabilidad de contagio es: " + str(self.analizar_respuesta(mensaje)))
					print("Para obtener la lista de contactos escribe: #lista_contactos\nSi quieres agregar un contacto: #agregar_contacto [correo_del_contacto] [probabilidad_de_contacto]")
					#mensaje = "#estado " + mensaje
					#self.cliente.send(mensaje.encode())
				mensaje = usuario + " " + mensaje
				self.cliente.send(mensaje.encode())
			else:
				self.cliente.send((usuario + " " + mensaje + " " + self.nombre_completo).encode())
				self.cliente.close()
				sys.exit()
	
	
if len(sys.argv) < 2:
	print("se esperaban banderas")
elif sys.argv[1] == "-c" :
	if len(sys.argv) < 5:
		print("se esperaba un hostname, puerto y usuario")
		exit()
	print("Servidor al que intento conectar: "+ sys.argv[2])
	Cliente(sys.argv[2],int(sys.argv[3]),sys.argv[4])
else:
	print("bandera no reconocida")
