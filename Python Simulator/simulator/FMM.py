import numpy as np
import pygame

from sklearn.mixture import GMM
from math import sqrt, atan, pi

def emFit(results, numComponents):
    if len(results) == 0:
        return None
    m =np.matrix(results)

    gmm = GMM(numComponents,covariance_type='full', n_iter= 100, n_init = 4)

    gmm.fit(results)

    components = []
    for componentID in xrange(numComponents):
        mu = gmm.means_[componentID] 
        cov = gmm.covars_[componentID]
        proba = gmm.weights_[componentID]

        components.append((mu,cov,proba))
    components = sorted(components,key=lambda x: x[0][0])
    return components
    
def drawComponents(surface, windowSize, scaleFactor, components):
    if components is None:
        return
    colors = [(255, 150, 150),(150, 150, 255),(150, 255, 150)]
    for color,(mu,cov, proba) in zip(colors[:len(components)],components):
    
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        major = 2.0 * sqrt(5.991 * eigenvalues.max())
        minor = 2.0 * sqrt(5.991 * eigenvalues.min())
        angle1 = atan(eigenvectors[1][0]/eigenvectors[0][0])
        angle2 = atan(eigenvectors[1][1]/eigenvectors[0][1])
        if eigenvalues[0] > eigenvalues[1]:
            angle = angle1
        else:
            angle = angle2
        
        
        mu_x,mu_y = mu
        if major < 1.0 or minor < 1.0:
            continue

        s = pygame.Surface((major*scaleFactor[0], minor*scaleFactor[1]),pygame.SRCALPHA, 32)

        ellipse = pygame.draw.ellipse(s, color, (0, 0, major*scaleFactor[0], minor*scaleFactor[0]))

        s2 = pygame.transform.rotate(s, angle*360.0/(2.0*pi))
        height, width = s2.get_rect().height,s2.get_rect().width
        surface.blit(s2,(mu_x*scaleFactor[0]-width/2.0,mu_y*scaleFactor[1]-height/2.0))#(mu_x*scaleFactor[0]-height/2.0,mu_y*scaleFactor[1]-width/2.0))
        
        
        #s = pygame.Surface((major*scaleFactor[0], minor*scaleFactor[1]))
        #s.fill((255,255,255))
        #s.set_alpha(128)
        
        #ellipse = pygame.draw.ellipse(s, blue, (0, 0, major*scaleFactor[0], minor*scaleFactor[0]))
        
        #s3 = pygame.transform.rotate(s, angle1*360.0/(2.0*pi))
        #height, width = s3.get_rect().height,s3.get_rect().width
        #surface.blit(s3,(mu_x*scaleFactor[0]-width/2.0,mu_y*scaleFactor[1]-height/2.0))#(mu_x*scaleFactor[0]-height/2.0,mu_y*scaleFactor[1]-width/2.0))
        
        
       #surface.blit(s,(0,0))
        #print angle*360.0/(2.0*pi)

