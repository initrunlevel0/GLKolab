#!/usr/bin/python
# GLKolab Server
# Using Pickle to Serialize or Deserialize object class

import socket
import os
import sys
import random
import pickle
import string
from thread import *
from Tkinter import *
import ttk

# Global Variable
user = {}
commandStack = []
drawObject = []

# Start a GUI
root = Tk()
root.title('GLKolab Server')

root.geometry('565x94+250+143')

lblMasukanNomorPort = ttk.Label(root)
lblMasukanNomorPort.place(relx=0.04, rely=0.11, height=20, width=312)
lblMasukanNomorPort.configure(borderwidth="2")
lblMasukanNomorPort.configure(text='''Masukkan nomor port untuk menjalankan GLKolab''')

nomorPort = StringVar()
txtNomorPort = ttk.Entry(root, textvariable=nomorPort)
txtNomorPort.place(relx=0.04,rely=0.32,relheight=0.28,relwidth=0.7)
txtNomorPort.configure(background="white")
txtNomorPort.configure(font="TkTextFont")
txtNomorPort.configure(width=396)

def continue_gui():
	root.destroy()

btnJalankanServer = Button (root, command=continue_gui)
btnJalankanServer.place(relx=0.76,rely=0.32,height=26,width=120)
btnJalankanServer.configure(activebackground="#f4bcb2")
btnJalankanServer.configure(text='''Jalankan Server''')

root.mainloop()

class DrawObject:
	def __init__(self):
		raise NotImplementedError
class Text(DrawObject):
	def __init__(self):
		raise NotImplementedError

class VertexedObject(DrawObject):
	def __init__(self):
		raise NotImplementedError

class BezierCurve(VertexedObject):
	def __init__(self):
		raise NotImplementedError

class Line(VertexedObject):
	def __init__(self):
		raise NotImplementedError

class Pencil(VertexedObject):
	def __init__(self):
		raise NotImplementedError
# Command retrieving function
def retrieve_command(conn):
	result = ""
	byte = conn.recv(1)
	while byte != '\0':
		result = result + byte
		byte = conn.recv(1)
	

	return result.split()


def send_command(conn, command):
	conn.send(command + '\0')

# Client handling function
def clientthread(conn, addr):
	this_user_name = ""

	# Protocol Command
	# introduce<space>name
	# addObject<space>newObjectPickle
	# modifyObject<space>objectId, newObjectPickle
	# removeObject<space>objectId


	# Command retrieving part

	while True:
		command = retrieve_command(conn)
		if len(command) > 0:
			# introduce
			if command[0] == 'introduce':
				if(len(command) == 2):
					this_user_name = command[1]
					user[addr] = command[1]
					for key, u in user.iteritems():
						if u != this_user_name:
							commandStack.append({"command": "introduce", "params": this_user_name, "destination": u, 'sent': False})

			# addObject<space>(Object Marshalling)
			# return: New Object ID
			elif command[0] == 'addObject':
				if(len(command) == 2):
					new_object = pickle.loads(eval(command[1]))
					new_object.id = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(30))
					new_object.selected = False

					drawObject.append(new_object)
					send_command(conn, new_object.id)

					# Synchronize
					for key, u in user.iteritems():
						if u != this_user_name:
							commandStack.append({"command": "addObject", "params": repr(pickle.dumps(new_object)), "destination": u, 'sent': False})
			# modifyObject<space>(Object Marshalling)
			# return: "Y"
			elif command[0] == 'modifyObject':
				if(len(command) == 2):
					new_object = pickle.loads(eval(command[1]))
					new_object.selected = False

					# Find that object
					for obj in drawObject:
						if obj.id == new_object.id:
							drawObject[drawObject.index(obj)] = new_object
							break

					for key, u in user.iteritems():
						if u != this_user_name:
							commandStack.append({"command": "modifyObject", "params": repr(pickle.dumps(new_object)), "destination": u, 'sent': False})
					send_command(conn, "Y")
			
			# removeObject<space>(Object Marshalling)
			# return: "Y"
			elif command[0] == 'removeObject':
				if(len(command) == 2):
					new_object = pickle.loads(eval(command[1]))
					
					# Find that object
					for obj in drawObject:
						if obj.id == new_object.id:
							drawObject.remove(obj)
							break

					for key, u in user.iteritems():
						if u != this_user_name:
							commandStack.append({"command": "removeObject", "params": repr(pickle.dumps(new_object)), "destination": u, 'sent': False})
					send_command(conn,"Y")
			elif(command[0] == 'pull'):
				pulled_object = []
				for obj in commandStack:
					if obj['destination'] == this_user_name and obj['sent'] == False:
						pulled_object.append(obj)
						obj['sent'] = True

				send_command(conn, repr(pickle.dumps(pulled_object)))
				if len(pulled_object) > 0:
					print repr(pickle.dumps(pulled_object))
		
			elif(command[0] == 'requestAllObject'):
				send_command(conn, repr(pickle.dumps(drawObject)))


# Server Starting
HOST = ''                 # Symbolic name meaning the local host
PORT = int(nomorPort.get()) 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

s.listen(10)
# Infinite loop to retrieve connection from client
while True:
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])

	start_new_thread(clientthread, (conn,addr))

conn.close()

