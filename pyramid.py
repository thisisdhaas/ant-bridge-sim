from param import G
from error import SimulationError

class Pyramid(object):
    def __init__(self, id):
        self.id = id
        self.settled = False
        self.pos = self.getPos();
        self.x = self.pos[0]
        self.y = self.pos[1]
        if G.verbose:
            print >> G.outfile, "deterministic ant %d is moving" % (self.id)

    def getPos(self):
        y = -1
        blocks = -1
        while blocks < self.id:
            y += 1
            numBlocksOnLine = self.lineWidth(y)
            if numBlocksOnLine <= 0:
                raise SimulationError("PyramidHeightError", "Pyramid cannot grow higher at current width")
            blocks += numBlocksOnLine

        xStart = (G.numBlocksX - numBlocksOnLine) / 2
        xEnd = G.numBlocksX - xStart
        x = xEnd - (blocks - self.id) -1
        assert x >= xStart and x < xEnd
        return (x,y)

    def lineWidth(self, y):
        scale = (1 / (G.pyramidScaleFactor * float(y)*float(y) + 1))
        ret = float(G.numBlocksX) * scale
        return int(ret)

    def move(self):
        G.state[self.pos] = G.NORMAL
        self.settled = True

