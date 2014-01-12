#!/usr/bin/python
# GLKolab: OpenGL based 2D Whiteboard System

# Putu Wiramaswara Widya <initrunlevel0@gmail.com>
# https://github.com/initrunlevel0/GLKolab

### MAIN LIBRARY IMPORT
import ctypes
import pickle
import socket
import sys
import string
import random
import copy
import pyglet
from pyglet.gl import *
import imp

# UI to ask for address, port and name
if(len(sys.argv) != 4):
	import Tkinter
	import ttk
	master = Tkinter.Tk()
	master.title("GLKolab Client")
	master.geometry('661x62+200+200')
	nomorIP = Tkinter.StringVar()
	nomorPort = Tkinter.StringVar()
	nama = Tkinter.StringVar()

	lblPesan = ttk.Label (master)
	lblPesan.place(relx=0.03,rely=0.16,height=20,width=578)
	lblPesan.configure(borderwidth="2")
	lblPesan.configure(text='''Masukkan nomor IP, Port serta nama identitas (sembarang tapi unik) untuk masuk ke GLKolab''')

	entIP = ttk.Entry (master, textvariable=nomorIP)
	entIP.place(relx=0.03,rely=0.48,relheight=0.32,relwidth=0.31)
	entIP.configure(background="white")
	entIP.configure(cursor="fleur")
	entIP.configure(font="TkFixedFont")
	entIP.configure(width=206)

	entPort = ttk.Entry (master, textvariable=nomorPort)
	entPort.place(relx=0.38,rely=0.48,relheight=0.32,relwidth=0.13)
	entPort.configure(background="white")
	entPort.configure(font="TkFixedFont")
	entPort.configure(width=86)

	entNama = ttk.Entry (master, textvariable=nama)
	entNama.place(relx=0.56,rely=0.48,relheight=0.32,relwidth=0.27)
	entNama.configure(background="white")
	entNama.configure(font="TkFixedFont")
	entNama.configure(width=176)

	def continue_gui():
		master.destroy()

	btnJalankan = ttk.Button (master, command=continue_gui)
	btnJalankan.place(relx=0.83,rely=0.48,height=26,width=67)
	btnJalankan.configure(text='''Jalankan''')
	btnJalankan.configure(width=67)
	master.mainloop()
	nomorIP = nomorIP.get()
	nomorPort = nomorPort.get()
	nama = nama.get()
else:
	nomorIP = sys.argv[1]
	nomorPort = sys.argv[2]
	nama = sys.argv[3]


### GLOBAL VARIABLE
window = pyglet.window.Window(800,600) 
window.set_caption("GLKolab")
# Text Label Definition
logoLabel = pyglet.text.HTMLLabel('<font size=5 face="Helvetica" color="white"><strong>GL</strong>Kolab</font>', x=100, y=580, anchor_x='center', anchor_y='center')
cldis = pyglet.clock.ClockDisplay()
toolLabel = {} 
userLoginLabel = {}

canvasDrawObject = []
selected_color = (0.0, 0.0, 0.0)
state = "None"
selected_tool = "Select"
RANGE_VERTEX = 10
resizing = False
selected_point = (0,0,0)


### DRAWING CLASS DEFINITION
class DrawObject:
	selected = False
	def draw(self):
		raise NotImplementedError()
	
	def __init__(self):
		raise NotImplementedError()
	
class Text(DrawObject):
	def draw_selected(self):
		# Draw rectangle of selection
		glLineWidth(1.0)
		glColor3f(0.0,0.0, 0.0)
		glBegin(GL_LINE_LOOP)
		glVertex3f(self.get_far_left(), self.get_far_top(), 0.0)
		glVertex3f(self.get_far_right(), self.get_far_top(), 0.0)
		glVertex3f(self.get_far_right(), self.get_far_bottom(), 0.0)
		glVertex3f(self.get_far_left(), self.get_far_bottom(), 0.0)
		glEnd()

	def draw(self):
		self.text_object.draw()
		if state == "None":
			pass
		elif (self.selected == True):
			self.draw_selected()
		glFlush()

	def get_far_left(self):
		return self.text_object.x

	def get_far_right(self):
		return self.text_object.x + self.text_object.content_width

	def get_far_top(self):
		return self.text_object.y

	def get_far_bottom(self):
		return self.text_object.y - self.text_object.content_height
	def generate_html_text(self):
		self.text_object = pyglet.text.HTMLLabel('<font size=3 face=\'Helvetica\' color=\'black\'>' + self.text + '</font>', x=self.position[0], y=self.position[1], anchor_x='left', anchor_y='top')

	def change_position(self, position):
		self.position = position
		self.generate_html_text()

	def add_new_character(self, character):
		self.text = self.text + character
		self.generate_html_text()

	def __init__(self, position, text):
		self.position = position
		self.text = text
		self.selected = False
		self.generate_html_text()

class VertexedObject(DrawObject):
	
	def draw(self):
		raise NotImplementedError()
		
	def get_far_left(self):
		a = float('inf')
		for v in self.vertex:
			a = min(a, v[0])
		return int(a)

				
	def get_far_right(self):
		a = 0
		for v in self.vertex:
			a = max(a, v[0])
		return int(a)

	
	def get_far_top(self):
		a = 0
		for v in self.vertex:
			a = max(a, v[1])
		return int(a)

			
	def get_far_bottom(self):
		a = float('inf')
		for v in self.vertex:
			a = min(a, v[1])
		return int(a)
	
	
	def get_size_x(self):
		return self.get_far_right() - self.get_far_left()

	def get_size_y(self):
		return self.get_far_bottom() - self.get_far_top()
		pass

	def draw_selected(self):
		# Draw rectangle of selection
		glLineWidth(1.0)
		glColor3f(0.0,0.0, 0.0)
		glBegin(GL_LINE_LOOP)
		glVertex3f(self.get_far_left(), self.get_far_top(), 0.0)
		glVertex3f(self.get_far_right(), self.get_far_top(), 0.0)
		glVertex3f(self.get_far_right(), self.get_far_bottom(), 0.0)
		glVertex3f(self.get_far_left(), self.get_far_bottom(), 0.0)
		glEnd()

	def draw_vertex(self):
		global selected_point
		# Draw dot for every vertex
		for v in self.vertex:
			glPointSize(10.0)
			if(selected_point == v):
				glColor3f(1.0, 0.0, 0.0)
			else:
				glColor3f(0.0, 0.0, 0.0)
			glBegin(GL_POINTS)
			glVertex3f(v[0], v[1], 0.0)
			glEnd()

	def draw_corner_point(self):
		# Draw mini point for every corner
		glPointSize(10.0)
		
		# Top-Left
		glBegin(GL_POINTS)
		glVertex3f(self.get_far_left(), self.get_far_top(), 0.0)
		glEnd()
		
		# Top-Right
		glBegin(GL_POINTS)
		glVertex3f(self.get_far_right(), self.get_far_top(), 0.0)
		glEnd()

		# Bottom-Right
		glBegin(GL_POINTS)
		glVertex3f(self.get_far_right(), self.get_far_bottom(), 0.0)
		glEnd()

		# Bottom-Left
		glBegin(GL_POINTS)
		glVertex3f(self.get_far_left(), self.get_far_bottom(), 0.0)
		glEnd()
		
	def __init__(self):
		self.local_id = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(20))
		self.vertex = []
	

class BezierCurve(VertexedObject):
	curvePrecision = 101
	def draw(self):
		# Draw only its line curve
		c_vertex = ((ctypes.c_float * 3) * len(self.vertex)) (*self.vertex)
		glMap1f(GL_MAP1_VERTEX_3, 0.0, 100.0, 3, len(self.vertex), c_vertex[0])
		glEnable(GL_MAP1_VERTEX_3)
		glLineWidth(2.0)
		glColor3f(self.color[0], self.color[1], self.color[2])
		if (self.isPolygon):
			glBegin(GL_POLYGON)
		else:
			glBegin(GL_LINE_STRIP)
		for i in range(0, self.curvePrecision):
			glEvalCoord1f(i)
		glEnd()
		
		if state == "None":
			pass
			
		
		elif (state == "Drawing") and (self.selected == True):
			self.draw_vertex()	
		elif (state == "Selecting") and (self.selected == True):
			self.draw_selected()
			if selected_tool == "Vertex":
				self.draw_vertex()
			else:
				self.draw_corner_point()
		glFlush()
	def __init__(self, firstX, firstY, isPolygon, color):
		global state
		VertexedObject.__init__(self)
		
		self.vertex = []
		self.isPolygon = isPolygon
		self.color = color
		
		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))

class Pencil(VertexedObject):
	def draw(self):
		glLineWidth(2.0)
		glColor3f(self.color[0], self.color[1], self.color[2])
		glBegin(GL_LINE_STRIP)
		for v in self.vertex:
			glVertex3f(v[0], v[1], 0.0)
		glEnd();

		if (state == "Selecting") and (self.selected == True):
			self.draw_selected()
			self.draw_corner_point()	
		glFlush()
	def __init__(self, firstX, firstY, color):
		global state
		VertexedObject.__init__(self)
		self.vertex = []
		self.selected = False
		self.color = color

		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))

class Line(VertexedObject):
	def draw(self):
		# Draw only its line curve
		glLineWidth(2.0)
		glColor3f(self.color[0], self.color[1], self.color[2])
		if(self.isPolygon):
			glBegin(GL_POLYGON)
		else:
			glBegin(GL_LINE_STRIP)
		for v in self.vertex:
			glVertex3f(v[0], v[1], 0.0)
		glEnd()
		
		if state == "None":
			pass
			
		elif (state == "Drawing") and (self.selected == True):
			self.draw_vertex()	
		elif (state == "Selecting") and (self.selected == True):
			self.draw_selected()

			if selected_tool == "Vertex":
				self.draw_vertex()
			else:
				self.draw_corner_point()
		glFlush()
	def __init__(self, firstX, firstY, isPolygon, color):
		global state
		VertexedObject.__init__(self)
		self.selected = False
		self.isPolygon = isPolygon
		self.color = color
	
		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))
		
### NETWORK CONNECTION PART
objectPushQueue = [] # { "operation": "addObject", "object": "objectMarshall", "pushed": False }


def retrieve_command(conn):
	result = ""
	byte = conn.recv(1)
	while byte != '\0':
		result = result + byte
		byte = conn.recv(1)
	

	return result.split()


def send_command(conn, command):
	conn.send(command + '\0')


HOST = nomorIP
PORT = int(nomorPort)
my_name = nama
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

# Introduce Myself
send_command(s, "introduce " + my_name)

# Request All Object
send_command(s, "requestAllObject")
canvasDrawObject = canvasDrawObject + pickle.loads(eval(retrieve_command(s)[0]))

# s --> Socket Connection


def network_synchronize(conn):
	# PUSH
	for obj in objectPushQueue:
		if(obj['pushed'] == False):
			send_command(s, obj['operation'] + " " + obj['object'])
			result = retrieve_command(s)
			if(obj['operation'] == 'addObject'):
				for drawobj in canvasDrawObject:
					if drawobj.local_id == pickle.loads(eval(obj['object'])).local_id:
						drawobj.id = result[0]
						break
			obj['pushed'] = True

	# PULL
	send_command(s, 'pull')
	result = retrieve_command(s)[0]
	pulled_object = pickle.loads(eval(result))
	for obj in pulled_object:
		if(obj['command'] == 'addObject'):
			new_object = pickle.loads(eval(obj['params']))
			new_object.local_id = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(20))
			canvasDrawObject.append(new_object) 
		elif(obj['command'] == 'modifyObject'):
			new_object = pickle.loads(eval(obj['params']))
			for drawobj in canvasDrawObject:
				if(drawobj.id == new_object.id):
					canvasDrawObject[canvasDrawObject.index(drawobj)] = new_object

		elif(obj['command'] == 'removeObject'):
			new_object = pickle.loads(eval(obj['params']))
			for drawobj in canvasDrawObject:
				if(drawobj.id == new_object.id):
					canvasDrawObject.remove(drawobj)
			pass
	


def network_add_object(obj):
	# Special treatment for Text Object
	#if(isinstance(obj, Text)):
	#	obj = copy.copy(obj)
	#	obj.text_object = None
	#	print "Lalalala" + str(obj)

	objectPushQueue.append({'operation': 'addObject', 'object': repr(pickle.dumps(obj)), 'pushed': False})

def network_modify_object(obj):
	if(hasattr(obj, 'id')):
		objectPushQueue.append({'operation': 'modifyObject', 'object': repr(pickle.dumps(obj)), 'pushed': False})

def network_remove_object(obj):
	if(hasattr(obj, 'id')):
		objectPushQueue.append({'operation': 'removeObject', 'object': repr(pickle.dumps(obj)), 'pushed': False})

### DO DRAWING PRIMITIVE
def getSelectedObject(X, Y):
	global state, drawedObject, selected_point
	# Clear All Selection First
	drawedObject = -1
	for obj in canvasDrawObject:
		obj.selected = False

	# Choose ONLY ONE object which in the point
	for obj in canvasDrawObject:
		if(obj.get_far_left() <= X and obj.get_far_right() >= X and obj.get_far_top() >= Y and obj.get_far_bottom() <= Y):
			state = "Selecting"
			drawedObject = obj
			obj.selected = True
			break
		else:
			selected_point = (0, 0, 0)
			obj.selected = False
			drawedObject = -1
			state = "None"
				
def doUnselectObject():
	global state

	# Tools changing
	if('drawedObject' in globals()):
		if(drawedObject != -1):
			drawedObject.selected = False
	state = "None"

def doMovement(dX, dY):
	if(drawedObject != -1):
		for i in range(len(drawedObject.vertex)):
			drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)

		network_modify_object(drawedObject)

def doResize(dX, dY, side):
	if(drawedObject != -1):
		for i in range(len(drawedObject.vertex)):

			if(side == "TopLeft"):
				if(drawedObject.vertex[i][0] != drawedObject.get_far_right() and drawedObject.vertex[i][1] != drawedObject.get_far_bottom()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][0] == drawedObject.get_far_right() and drawedObject.vertex[i][1] != drawedObject.get_far_bottom()) :
					drawedObject.vertex[i] = (drawedObject.vertex[i][0], drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][1] == drawedObject.get_far_bottom() and drawedObject.vertex[i][0] != drawedObject.get_far_right()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1], 0.0)
		
			elif(side == "TopRight"):
				if(drawedObject.vertex[i][0] != drawedObject.get_far_left() and drawedObject.vertex[i][1] != drawedObject.get_far_bottom()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][0] == drawedObject.get_far_left() and drawedObject.vertex[i][1] != drawedObject.get_far_bottom()) :
					drawedObject.vertex[i] = (drawedObject.vertex[i][0], drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][1] == drawedObject.get_far_bottom() and drawedObject.vertex[i][0] != drawedObject.get_far_left()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1], 0.0)
			elif(side == "BottomRight"):
				if(drawedObject.vertex[i][0] != drawedObject.get_far_left() and drawedObject.vertex[i][1] != drawedObject.get_far_top()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][0] == drawedObject.get_far_left() and drawedObject.vertex[i][1] != drawedObject.get_far_top()) :
					drawedObject.vertex[i] = (drawedObject.vertex[i][0], drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][1] == drawedObject.get_far_top() and drawedObject.vertex[i][0] != drawedObject.get_far_left()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1], 0.0)
			elif(side == "BottomLeft"):
				if(drawedObject.vertex[i][0] != drawedObject.get_far_right() and drawedObject.vertex[i][1] != drawedObject.get_far_top()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][0] == drawedObject.get_far_right() and drawedObject.vertex[i][1] != drawedObject.get_far_top()) :
					drawedObject.vertex[i] = (drawedObject.vertex[i][0], drawedObject.vertex[i][1] + dY, 0.0)
				elif(drawedObject.vertex[i][1] == drawedObject.get_far_top() and drawedObject.vertex[i][0] != drawedObject.get_far_right()):
					drawedObject.vertex[i] = (drawedObject.vertex[i][0] + dX, drawedObject.vertex[i][1], 0.0)
		network_modify_object(drawedObject)

def doMoveVertex(index, x, y):
	if(drawedObject != -1):
		drawedObject.vertex[index] = (x, y, 0.0)
		network_modify_object(drawedObject)

def drawBezierCurve(firstX, firstY, isPolygon):
	global drawedObject, state
	bc = BezierCurve(firstX, firstY, isPolygon, selected_color)
	canvasDrawObject.append(bc)
	drawedObject = bc
	bc.selected = True
	window.flip()
	state = "Drawing"

def drawPencil(firstX, firstY):
	global drawedObject, state
	p = Pencil(firstX, firstY, selected_color)
	canvasDrawObject.append(p)
	drawedObject = p
	p.selected = True
	
	window.flip
	state = "Drawing"

def drawLine(firstX, firstY, isPolygon):
	global drawedObject, state
	l = Line(firstX, firstY, isPolygon, selected_color)
	canvasDrawObject.append(l)
	drawedObject = l
	l.selected = True
	window.flip()
	state = "Drawing"
	
def drawText(firstX, firstY):
	global drawedObject, state
	t = Text((firstX, firstY), "")
	canvasDrawObject.append(t)
	drawedObject = t
	t.selected = True
	window.flip()
	state = "Drawing"

### UI DESIGN

def drawButton(x, y, text, selected):
	# Draw surrounding rectangle
	glColor3f(1.0, 1.0, 1.0)
	
	if(selected == True):
		glLineWidth(5.0)
	else:
		glLineWidth(1.0)

	glBegin(GL_LINE_LOOP)
	glVertex3f(x-95, y-10, 0.0)
	glVertex3f(x-95, y+10, 0.0)
	glVertex3f(x+95, y+10, 0.0)
	glVertex3f(x+95, y-10, 0.0)
	glEnd()

	toolLabel[text].draw()

button = ["Select", "Vertex", "Pencil", "Line", "Curve", "Line P", "Curve P", "Text"]

color = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 1, 0), (1, 0, 1), (1, 1, 1)]

def drawToolbox():
	global label
	# Toolbox Box (0,0) (200, 0), (200, 600), (0, 600)
        glColor3f(0.1, 0.1, 0.1)
        glBegin(GL_POLYGON)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(200.0, 0.0, 0.0)
        glVertex3f(200.0, 600.0, 0.0)
        glVertex3f(0.0, 600.0, 0.0)		
        glEnd()

	# Draw GLKolab Logo
	logoLabel.draw()

	# Draw Toolbox button (Y=500 until Y=340)
	y = 500
	for each in button:
		drawButton(100, y, each, each==selected_tool)
		y = y - 20
	
	# Draw Selected Color (Y = 320 until Y = 290)
	glColor3f(selected_color[0], selected_color[1], selected_color[2])
	glBegin(GL_POLYGON)
	glVertex2i(20, 320)
	glVertex2i(180, 320)
	glVertex2i(180, 290)
	glVertex2i(20, 290)
	glEnd()

	# Draw Color Selector (Y=280 until Y=240)
	# Each row with 4 color
	y = 280
	color_chunk = []
	for chunk_index in range(0, len(color), 4):
		color_chunk.append(color[chunk_index:chunk_index+4])
	
	for each in color_chunk:
		for i in range(0, 4):
			glColor3f(each[i][0], each[i][1], each[i][2])
			glBegin(GL_POLYGON)
			glVertex3f(50 * (i+1) - 50, y-10, 0.0)
			glVertex3f(50 * (i+1), y-10, 0.0)
			glVertex3f(50 * (i+1), y+10, 0.0)
			glVertex3f(50 * (i+1) - 50, y+10, 0.0) 
			glEnd()

		y = y - 20

def initToolLabel():
	global toolLabel
	y = 500
	for each in button:
		toolLabel[each] = pyglet.text.HTMLLabel('<font size=2 face="Helvetica" color="white"><strong>' + str(each) + '</font>', x=100, y=y, anchor_x='center', anchor_y='center')
		y = y - 20

### REDRAWING STUFF AND UTILITY
def redrawCanvas():
	map(drawAll, canvasDrawObject)

def redrawAll():
	window.clear()
	glColor3f(0.0, 0.0, 0.0)
	redrawCanvas()
	drawToolbox()
	cldis.draw()

def drawAll(drawObject):
	drawObject.draw()
	#print pickle.dumps(drawObject)	

### EVENT HANDLER	
@window.event
def on_mouse_motion(x, y, dx, dy):
	if(selected_tool.startswith("Curve")):
		if(state == "Drawing"):
			drawedObject.vertex.pop()
			drawedObject.vertex.append((x, y, 0.0))
			
			redrawCanvas()
	elif(selected_tool.startswith("Line")):
		if(state == "Drawing"):
			drawedObject.vertex.pop()
			drawedObject.vertex.append((x, y, 0.0))
			
			redrawCanvas()

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
	global state, resizing, selected_point
	if(x > 200):
		if(button == pyglet.window.mouse.LEFT and "drawedObject" in globals()):
			if(selected_tool == "Select"):
				if(state == "Selecting"):
					if(drawedObject != -1):
						if(x in range(drawedObject.get_far_left()-RANGE_VERTEX, drawedObject.get_far_left()+RANGE_VERTEX) and y in range(drawedObject.get_far_top()-RANGE_VERTEX, drawedObject.get_far_top()+RANGE_VERTEX)):
							doResize(dx, dy, "TopLeft")
							resizing = True	
						elif(x in range(drawedObject.get_far_right()-RANGE_VERTEX, drawedObject.get_far_right()+RANGE_VERTEX) and y in range(drawedObject.get_far_top()-RANGE_VERTEX, drawedObject.get_far_top()+RANGE_VERTEX)):
							doResize(dx, dy, "TopRight")
							resizing = True
						elif(x in range(drawedObject.get_far_right()-RANGE_VERTEX, drawedObject.get_far_right()+RANGE_VERTEX) and y in range(drawedObject.get_far_bottom()-RANGE_VERTEX, drawedObject.get_far_bottom()+RANGE_VERTEX)):
							doResize(dx, dy, "BottomRight")
							resizing = True
						elif(x in range(drawedObject.get_far_left()-RANGE_VERTEX, drawedObject.get_far_left()+RANGE_VERTEX) and y in range(drawedObject.get_far_bottom()-RANGE_VERTEX, drawedObject.get_far_bottom()+RANGE_VERTEX)):
							doResize(dx, dy, "BottomLeft")
							resizing = True
						elif(resizing == False):
							doMovement(dx, dy)		
			elif(selected_tool == "Vertex"):
				if(state == "Selecting"):
					if(drawedObject != -1):
						for v in drawedObject.vertex:
							if(x >= v[0] - RANGE_VERTEX and x <= v[0] + RANGE_VERTEX and y >= v[1] - RANGE_VERTEX and y <= v[1] + RANGE_VERTEX):
								doMoveVertex(drawedObject.vertex.index(v), x, y)
								selected_point = (x, y, 0.0)

			elif(selected_tool == "Pencil"):
				if(drawedObject != -1):
					drawedObject.vertex.append((x, y, 0.0))
					redrawCanvas()
			elif(selected_tool == "Curve"): 
				pass
	else:
		# Anggap sebagai klik
		on_mouse_release(x, y, button, modifiers)
@window.event
def on_mouse_release(x, y, button, modifiers):
	global resizing, drawedObject
	resizing = False
	if(selected_tool == "Select"):
		pass
	elif(selected_tool == "Pencil"):
		if "drawedObject" in globals():
			if isinstance(drawedObject, Pencil):
				network_add_object(drawedObject)
		state = "None"
		pass
	elif(selected_tool == "Curve"): 
		pass

@window.event
def on_mouse_press(x, y, button, modifiers):
	global state, selected_tool, selected_color
	print str(x)
	# Toolbox or Canvas?
	if(x > 200):
		if(button == pyglet.window.mouse.LEFT):  
			# If first poin clicked (ONLY FOR POLYGON)
			if(selected_tool.endswith("P") and state == "Drawing"):
				# If your mouse cursor near that, add last vertex with first point and done!
				first_point = drawedObject.vertex[0]
				if(x >= first_point[0] - RANGE_VERTEX and x <= first_point[0] + RANGE_VERTEX and y >= first_point[1] - RANGE_VERTEX and y <= first_point[1] + RANGE_VERTEX):
					drawedObject.vertex.append(first_point)
					state = "None"
					network_add_object(drawedObject)
					drawedObject.selected = False
					return
			if(selected_tool == "Select" or selected_tool == "Vertex"):
				getSelectedObject(x, y)
			elif(selected_tool == "Pencil"):
				# Just A DOT of drawing
				drawPencil(x, y)
				pass
			elif(selected_tool.startswith("Curve")): 
				if(state == "None"):
					drawBezierCurve(x, y, selected_tool.endswith("P"))
					
				if(state == "Drawing"):
					drawedObject.vertex.append((x, y, 0.0))
			elif(selected_tool.startswith("Line")):
				if(state == "None"):
					drawLine(x, y, selected_tool.endswith("P"))
							
				if(state == "Drawing"):
					drawedObject.vertex.append((x, y, 0.0))
			elif(selected_tool == "Text"):
				if(state == "None"):
					drawText(x, y)
			

		elif(button == pyglet.window.mouse.RIGHT):  # End Drawing
			if(state == "Drawing"):
				state = "None"
				network_add_object(drawedObject)
				drawedObject.selected = False
	else:
		# This is toolbox
		# Tool selection part
		if y <= 500 and y > 480 :
			if(selected_tool != "Vertex"):
				doUnselectObject()
			selected_tool = "Select"
		elif y <= 480 and y > 460:          
			if(selected_tool != "Select"):
				doUnselectObject()
			selected_tool = "Vertex"
		elif y <= 460 and y > 440:
			doUnselectObject()
			selected_tool = "Pencil"
		elif y <= 440 and y > 420:
			doUnselectObject()
			selected_tool = "Line"
		elif y <= 420 and y > 400:
			doUnselectObject()
			selected_tool = "Curve"
		elif y <= 400 and y > 380: 
			doUnselectObject()
			selected_tool = "Line P"
		elif y <= 380 and y > 360:
			doUnselectObject()
			selected_tool = "Curve P"
		elif y <= 360 and y > 340:
			doUnselectObject()
			selected_tool = "Text"
			
		# Color selection part (280 to 240)
		if x >= 0 and x < 50 and y >= 260 and y < 280:
			selected_color = color[0]
		elif x >= 50 and x < 100 and y >= 260 and y < 280:
			selected_color = color[1]
		elif x >= 100 and x < 150 and y >= 260 and y < 280:
			selected_color = color[2]
		elif x >= 150 and x < 200 and y >= 260 and y < 280:
			selected_color = color[3]
		if x >= 0 and x < 50 and y >= 240 and y < 260:
			selected_color = color[4]
		elif x >= 50 and x < 100 and y >= 240 and y < 260:
			selected_color = color[5]
		elif x >= 100 and x < 150 and y >= 240 and y < 260:
			selected_color = color[6]
		elif x >= 150 and x < 200 and y >= 240 and y < 260:
			selected_color = color[7]
		
@window.event
def on_key_press(symbol, modifiers):
	if symbol == pyglet.window.key.DELETE:
		# Delete Object
		if(selected_tool == "Select" and drawedObject != -1):
			canvasDrawObject.remove(drawedObject)
			network_remove_object(drawedObject)
		elif(selected_tool == "Vertex" and drawedObject != -1 and selected_point != (0,0,0)):
			drawedObject.vertex.remove(selected_point)
			network_modify_object(drawedObject)
	elif((selected_tool == "Text" and state == "Drawing") or isinstance(drawedObject, Text) and drawedObject.selected == True):
		if(drawedObject != -1):
			if(symbol != pyglet.window.key.ENTER):
				drawedObject.add_new_character(pyglet.window.key.symbol_string(symbol))
			else:
				#network_add_object(drawedObject)
				doUnselectObject()
@window.event
def on_draw():
	network_synchronize(s)
	redrawAll()

#patch_idle_loop()
glClearColor(1.0, 1.0, 1.0, 1.0)
initToolLabel()

pyglet.app.run()

