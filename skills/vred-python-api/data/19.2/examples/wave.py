# Sinus wave with cubes
# source: wave.html

import math

# a sinus wave
class vrWave:
    speed = math.pi / 10.0
    pieces = 200
    def __init__(self, id = 0, shift = 0.0):
        self.shift = shift
        self.nodes = self._queryNodes(id)
        self.step()

    def step(self):
        piece = math.pi / len(self.nodes)
        for i in range(len(self.nodes)):
            node = self.nodes[i]
            pos = self.shift + i * piece
            z = math.fabs(math.sin(pos))
            setTransformNodeScale(node, 1.0, 1.0, z)
        self.shift += vrWave.speed
        if self.shift > math.pi:
            self.shift = 0.0

    def _queryNodes(self, id):
        nodes = []
        for i in range(vrWave.pieces):
            name = "wave {}/{}".format(id, i + 1)
            node = findNode(name, False)
            nodes.append(node)
        return nodes;

# creation and animation of all waves
class vrWaveAnimation(vrTimer):
    waveCount = 20
    def __init__(self):
        super(vrWaveAnimation, self).__init__()
        self.waves = []
        for i in range(vrWaveAnimation.waveCount):
            shift = math.pi * i / vrWaveAnimation.waveCount
            wave = vrWave(i + 1, shift)
            self.waves.append(wave)
        super(vrWaveAnimation, self).connect(self._step)

    def run(self):
        super(vrWaveAnimation, self).setActive(True)

    def stop(self):
        super(vrWaveAnimation, self).setActive(False)

    def __del__(self):
        self.stop()

    def _step(self):
        for wave in self.waves:
            wave.step()

animation = vrWaveAnimation()
animation.run()
