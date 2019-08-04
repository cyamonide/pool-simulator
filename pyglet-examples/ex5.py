import pyglet

window = pyglet.window.Window()

pyglet.app.run()

print(window.push_handlers(pyglet.window.event.WindowEventLogger()))