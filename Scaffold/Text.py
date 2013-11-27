import pyglet
from pyglet.gl import *

window = pyglet.window.Window()
label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

@window.event
def on_draw():
    window.clear()
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POLYGON)
    glVertex2f(100.0, 100.0)
    glVertex2f(100.0, 200.0)
    glVertex2f(200.0, 300.0)
    glEnd() 
    label.draw()
    print "La"
pyglet.app.run()
