import pygame


def drawEllipseCentered(surface, color, center, size):
    pygame.draw.ellipse(surface, map(lambda x: int(x),color), (map(lambda x: int(x),(center[0]-size[0]/2,center[1]-size[1]/2)), map(lambda x: int(x),size)))
def drawGradientEllipseCentered(surface, color, center, size, layers = 3):
    for x in xrange(layers-1,-1, -1):
        drawEllipseCentered(surface, map(lambda i: int(i*(1+x)/layers),color), center, map(lambda i:  int(i*(1+x)/layers), size))
		
def drawGradientCircle(surface, color, center, size, layers = 3, inverted=False):
    if inverted:
        for x in xrange(layers-1,-1, -1):
            pygame.draw.circle(surface, map(lambda i: int(i*(layers-x)/layers),color), center,  int(size*(1+x)/layers))
    else:
        for x in xrange(layers-1,-1, -1):
            pygame.draw.circle(surface, map(lambda i: int(i*(1+x)/layers),color), center,  int(size*(1+x)/layers))


def drawInfolabel(window, position, space, label, value):
    font = pygame.font.Font(None,24)
    text = font.render(label, 1, (10, 10, 10))
    window.blit(text, position)   
    text = font.render(str(value), 1, (10, 10, 10))
    window.blit(text, (position[0]+ space,position[1] ))   

