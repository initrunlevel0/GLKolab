#!/usr/bin/python

# BezierDraw
# Part of GLKolab Project Scaffolding

# Putu Wiramaswara Widya <initrunlevel0@gmail.com
# http://github.com/initrunlevel0/GLKolab

import ctypes
import pyglet
from pyglet.gl import *

canvasDrawObject = []
state = "None"

window = pyglet.window.Window(800,600) 
# Class of Bezier
class DrawObject:
	
	def draw(self):
		raise NotImplementedError()
	def draw(self):
		raise NotImplementedError()

class BezierCurve(DrawObject):
	
	def draw(self):
		# Draw only its line curve
		c_vertex = ((ctypes.c_float * 3) * len(self.vertex)) (*self.vertex)
		glMap1f(GL_MAP1_VERTEX_3, 0.0, 100.0, 3, len(self.vertex), c_vertex[0])
		glEnable(GL_MAP1_VERTEX_3)
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
		self.curvePrecision = 101
		self.vertex = []
		self.selected = False
		
		# Define first curve
		self.vertex.append((firstX, firstY, 0.0))

def drawBezierCurve(firstX, firstY):
	global drawedObject
	bc = BezierCurve(firstX, firstY)
	canvasDrawObject.append(bc)
	drawedObject = bc
	bc.selected = True
	window.flip()
	
	

def redrawCanvas():
	glClear(GL_COLOR_BUFFER_BIT)
	map(drawAll, canvasDrawObject)
	
def drawAll(drawObject):
	drawObject.draw()
	
	
@window.event
def on_draw():
	glLoadIdentity()
	glColor3f(1.0, 1.0, 1.0)

@window.event
def on_mouse_motion(x, y, dx, dy):
	if(state == "Drawing"):
		drawedObject.vertex.pop()
		drawedObject.vertex.append((x, y, 0.0))
		
		redrawCanvas()
	
@window.event
def on_mouse_press(x, y, button, modifiers):
	global state
	if(button == pyglet.window.mouse.LEFT):  # Start Drawing
		if(state == "None"):
			drawBezierCurve(x, y)
			
			redrawCanvas()
			state = "Drawing"
			
		if(state == "Drawing"):
			drawedObject.vertex.append((x, y, 0.0))
			for x in canvasDrawObject:
				print x.vertex
				print "-------"
			
	elif(button == pyglet.window.mouse.RIGHT):  # End Drawing
		if(state == "Drawing"):
			state = "None"
			
			redrawCanvas()
			drawedObject.selected = False


pyglet.app.run()



		
		
