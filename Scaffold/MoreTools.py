#!/usr/bin/python

# BezierDraw
# Part of GLKolab Project Scaffolding

# Putu Wiramaswara Widya <initrunlevel0@gmail.com
# http://github.com/initrunlevel0/GLKolab

import ctypes
import pyglet
from pyglet.gl import *

### GLOBAL VARIABLE
canvasDrawObject = []
state = "None"
tool = "Select"

window = pyglet.window.Window(800,600) 

### DRAWING CLASS DEFINITION
class DrawObject:
	selected = False
	def draw(self):
		raise NotImplementedError()
	
	def get_far_left(self):
		raise NotImplementedError()
	
	def get_far_right(self):
		raise NotImplementedError()
	
	def get_far_top(self):
		raise NotImplementedError()
	
	def get_far_bottom(self):
		
	def __init__(self):
		raise NotImplementedError()

class BezierCurve(DrawObject):
	vertex = []
	curvePrecision = 101
	
	def draw(self):
		# Draw only its line curve
		c_vertex = ((ctypes.c_float * 3) * len(self.vertex)) (*self.vertex)
		glMap1f(GL_MAP1_VERTEX_3, 0.0, 100.0, 3, len(self.vertex), c_vertex[0])
		glEnable(GL_MAP1_VERTEX_3)
		glLineWidth(2.0)
		glBegin(GL_LINE_STRIP)
		for i in range(0, self.curvePrecision):
			glEvalCoord1f(i)
		glEnd()
		
		if state == "None":
			pass
			
		elif (state == "Drawing") and (self.selected == True):
			
			# Draw dot for every vertex
			for v in self.vertex:
				glPointSize(10.0)
				glBegin(GL_POINTS)
				glVertex3f(v[0], v[1], 0.0)
				glEnd()
			pass
		
		glFlush()
	def __init__(self, firstX, firstY):
		global state
		
		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))

class Pencil(DrawObject):
	vertex = []
	
	def draw(self):
		glLineWidth(2.0)
		glBegin(GL_LINE_STRIP)
		for v in self.vertex:
			glVertex3f(v[0], v[1], 0.0)
		glEnd();
		glFlush()
	def __init__(self, firstX, firstY):
		global state
		self.vertex = []
		self.selected = False
		
		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))

### DO DRAWING PRIMITIVE
def drawBezierCurve(firstX, firstY):
	global drawedObject, state
	bc = BezierCurve(firstX, firstY)
	canvasDrawObject.append(bc)
	drawedObject = bc
	bc.selected = True
	redrawCanvas()
	window.flip()
	state = "Drawing"
	
def drawPencil(firstX, firstY):
	global drawedObject, state
	p = Pencil(firstX, firstY)
	canvasDrawObject.append(p)
	drawedObject = p
	p.selected = True
	redrawCanvas()
	
	window.flip
	state = "Drawing"
	
	
### REDRAWING STUFF AND UTILITY
def redrawCanvas():
	glClear(GL_COLOR_BUFFER_BIT)
	map(drawAll, canvasDrawObject)

def whichSelected():
	pass

def drawAll(drawObject):
	drawObject.draw()
	

### EVENT HANDLER	
@window.event
def on_draw():
	pass

@window.event
def on_mouse_motion(x, y, dx, dy):
	if(tool == "Curve"):
		if(state == "Drawing"):
			drawedObject.vertex.pop()
			drawedObject.vertex.append((x, y, 0.0))
			
			redrawCanvas()

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
	
	if(button == pyglet.window.mouse.LEFT):
		if(tool == "Select"):
			pass
		elif(tool == "Pencil"):
			drawedObject.vertex.append((x, y, 0.0))
			redrawCanvas()
			pass
		elif(tool == "Curve"): 
			pass

@window.event
def on_mouse_release(x, y, button, modifiers):
	if(tool == "Select"):
		pass
	elif(tool == "Pencil"):
		state = "None"
		pass
	elif(tool == "Curve"): 
		pass

@window.event
def on_mouse_press(x, y, button, modifiers):
	global state, tool
	if(button == pyglet.window.mouse.LEFT):  # Start Drawing
		# From what tools
		if(tool == "Select"):
			selectedObject = whichSelected()
			if(selectedObject != None):
				selectedObject.selected = True
				redrawCanvas()
			pass
		elif(tool == "Pencil"):
			# Just A DOT of drawing
			drawPencil(x, y)
			pass
		elif(tool == "Curve"): 
			if(state == "None"):
				drawBezierCurve(x, y)
				
			if(state == "Drawing"):
				drawedObject.vertex.append((x, y, 0.0))
			
	elif(button == pyglet.window.mouse.RIGHT):  # End Drawing
		if(state == "Drawing"):
			state = "None"
			drawedObject.selected = False
			redrawCanvas()

@window.event
def on_key_press(symbol, modifiers):
	global tool, state, drawedObject
	
	# Tools changing
	if('drawedObject' in globals()):
		drawedObject.selected = False
	state = "None"
	redrawCanvas()
	
	if symbol == pyglet.window.key._1:
		tool = "Select"
	elif symbol == pyglet.window.key._2:
		tool = "Pencil"
	elif symbol == pyglet.window.key._3:
		tool = "Curve"
	
	print "Selected " + tool

### MAIN FUNCTION
glLoadIdentity
glClearColor(1.0, 1.0, 1.0, 0.0)
glClear(GL_COLOR_BUFFER_BIT)
glColor3f(0.0, 0.0, 0.0)
pyglet.app.run()
	




		
		
