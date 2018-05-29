from os import path
import numpy as np
import vispy
from vispy import gloo, app

vispy.use('Glfw')  # avoid bug on Qt

GLSL_PATH = path.join(path.dirname(path.abspath(__file__)), 'glsl')

class MatrixVisualizer(object):
    """docstring for MatrixVisualizer."""
    def __init__(self, width=600, height=600, value_range_min=0, value_range_max=1):
        self.value_range = (value_range_min, value_range_max)
        self._canvas = app.Canvas(size=(width, height), position=(0,0), title="ALife book "+self.__class__.__name__)
        self._canvas.events.draw.connect(self.on_draw)
        vertex_shader = open(path.join(GLSL_PATH, 'matrix_visualizer_vertex.glsl'), 'r').read()
        fragment_shader = open(path.join(GLSL_PATH, 'matrix_visualizer_fragment.glsl'), 'r').read()
        self._render_program = gloo.Program(vertex_shader, fragment_shader)
        self._render_program['a_position'] = [(-1,-1), (-1,+1), (+1,-1), (+1,+1)]
        self._render_program['a_texcoord'] = [( 0, 1), ( 0, 0), ( 1, 1), ( 1, 0)]
        self._render_program['u_texture'] = np.zeros((1,1)).astype(np.uint8)
        self._canvas.show()

    def on_draw(self, event):
        gloo.clear()
        self._render_program.draw(gloo.gl.GL_TRIANGLE_STRIP)

    def update(self, matrix):
        matrix[matrix < self.value_range[0]] = self.value_range[0]
        matrix[matrix > self.value_range[1]] = self.value_range[1]
        img = ((matrix.astype(np.float64) - self.value_range[0]) / (self.value_range[1] - self.value_range[0]) * 255).astype(np.uint8)
        self._render_program['u_texture'] = img
        self._canvas.update()
        app.process_events()

    def __bool__(self):
        return not self._canvas._closed

if __name__ == '__main__':
    v = MatrixVisualizer(600, 600)
    data = np.repeat(np.arange(0, 256, dtype=np.uint8)[np.newaxis,:], 3, axis=0)
    while v:
        data = np.roll(data, 1, axis=1)
        v.update(data)
