from PIL import Image, ImageDraw

DEFAULT_SIZE = 10

class DrawingHelper:

    def drawLinePattern(fillStyle, color, dstPath):
        img = Image.new('RGBA', (DEFAULT_SIZE, DEFAULT_SIZE), (255, 0, 0, 0))
        drawImg = ImageDraw.Draw(img)
        draw = getattr(DrawingHelper, '_get' + fillStyle, DrawingHelper._getHorizontal)
        xy = draw()
        drawImg.line(xy, fill=color ,width=1)
        # img.show()
        img.save(dstPath, 'PNG')

    def _getHorizontal():
        return [(0, DEFAULT_SIZE/2), (DEFAULT_SIZE, DEFAULT_SIZE/2)]

    def _getVertical():
        return [(DEFAULT_SIZE/2, 0), (DEFAULT_SIZE/2, DEFAULT_SIZE)]

    def _getBDiagonal():
        return [(DEFAULT_SIZE, 0), (0, DEFAULT_SIZE)]

    def _getFDiagonal():
        return [(0,0), (DEFAULT_SIZE, DEFAULT_SIZE)]

    def _getCross():
        return [(0, DEFAULT_SIZE/2), (DEFAULT_SIZE, DEFAULT_SIZE/2), 
                (DEFAULT_SIZE/2, DEFAULT_SIZE/2), 
                (DEFAULT_SIZE/2, 0), (DEFAULT_SIZE/2, DEFAULT_SIZE)]

    def _getDiagonalX():
        return [(DEFAULT_SIZE, 0), (0, DEFAULT_SIZE), 
                (DEFAULT_SIZE/2, DEFAULT_SIZE/2), 
                (0, 0), (DEFAULT_SIZE, DEFAULT_SIZE)]