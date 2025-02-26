import pygame
import time
import os
from random import random, randint, uniform

pygame.init()
pygame.mixer.init()
geigerSound = pygame.mixer.Sound("EMC\geiger.wav")
window = pygame.display.set_mode((0,0), pygame.RESIZABLE, pygame.FULLSCREEN)
pygame.display.set_caption("Simulation")
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (11,11,222)
RED = (255,11,11)
GREY = (127,127,135)
GREEN = (0,255,0)
window.fill(WHITE)
pygame.font.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont("Trebuchet MS",30)

class Grid:
    
    def __init__(self,sizex,sizey):
        self.sizex = sizex
        self.sizey = sizey
        self.eGrid = [["" for i in range(sizey)] for i in range(sizex)]  #elements
        self.wGrid = [["" for i in range(sizey)] for i in range(sizex)]  #water

    def draw(self):
        #do wGrid

        for i in self.eGrid:
            for j in i:
                j.draw()

class Element:
    types = ["N","U","X"]

    def __init__(self,gridx,gridy,posx,posy,type):
        self.posx = posx
        self.posy = posy
        self.gridx = gridx
        self.gridy = gridy
        self.type = type
        self.radius = 12
        self.timer = 0
        self.rect = pygame.Rect(self.posx - (self.radius*0.6), self.posy - (self.radius*0.6), self.radius*1.35, self.radius*1.35)

    def checkSecond(self,time):
        return time-self.timer > 1

    def draw(self, test = False):
        if self.type == "N":
            colour = GREY
        elif self.type == "U":
            colour = BLUE
        elif self.type == "X":
            colour = BLACK
        else:
            colour = GREEN
        pygame.draw.circle(window,colour,(self.posx,self.posy),self.radius)
    
    def releaseNeutron(self,uranium,neutronsF,fission = False):
        geigerSound.play()
        if fission:
            self.type = "N"
            self.timer = time.time()
        for i in range(1 + 2*fission):
            velx = uniform(-5,5)
            vely = (25 - velx ** 2)** 0.5
            if round(random()) % 2 == 0:
                vely *= -1
            neutronsF.append(Neutron(self.posx,self.posy,velx,vely))


class Neutron:
    
    def __init__(self,posx,posy,velx,vely):
        self.posx = posx
        self.posy = posy
        self.velx = velx
        self.vely = vely
        self.fast = True
        self.radius = 7
        self.rect = pygame.Rect(self.posx - (self.radius*0.6), self.posy - (self.radius*0.6), self.radius*1.35, self.radius*1.35)

    def draw(self):
        pygame.draw.circle(window,(180*self.fast,0,0),(self.posx,self.posy),self.radius)

    def move(self):
        self.posx = round(self.posx + self.velx)
        self.posy = round(self.posy + self.vely)
        self.rect.left = round(self.rect.left + self.velx)
        self.rect.top = round(self.rect.top + self.vely)

    def moderate(self):
        self.fast = False
        self.velx = self.velx/2 if abs(self.velx/2) > 0 else self.velx/abs(self.velx)
        self.vely = self.vely/2 if abs(self.vely/2) > 0 else self.vely/abs(self.velx)


class ControlRod:
    
    def __init__(self,posx,posy):
        self.posx = posx
        self.posy = posy
        self.rect = pygame.Rect(posx,posy,10,37*20)

    def draw(self):
        pygame.draw.rect(window,BLACK,self.rect)

    def collide(self, neutronsF, neutronsT, neutron):
        if self.rect.colliderect(neutron.rect):
            if neutron.fast:
                neutronsF.remove(neutron)
            else:
                neutronsT.remove(neutron)


class ModeratorRod:
    
    def __init__(self,posx,posy):
        self.posx = posx
        self.posy = posy
        self.rect = pygame.Rect(posx,posy,10,37*20)
    
    def draw(self):
        pygame.draw.rect(window,WHITE,self.rect)
        pygame.draw.rect(window,BLACK,self.rect,3)

    def collide(self, neutronsF, neutronsT, neutron):
        if neutron.fast:
            neutron.moderate()
            neutronsT.append(neutron)
            neutronsF.remove(neutron)



class Water:
    
    def __init__(self,posx,posy,gridx,gridy):
        self.posx = posx
        self.posy = posy
        self.gridx = gridx
        self.gridy = gridy
        self.rect = pygame.Rect(posx,posy,10,10)
        self.temperature = 0

    def collide(self):
        self.temperature += 1
        if self.temp > 100:
            pass




def checkCollision(uranium, xenon, neutronsT, neutronsF):
    for i in uranium:
        for j in neutronsT:
            if i.rect.colliderect(j.rect):# and random() > 0.5:
                i.releaseNeutron(uranium,neutronsF, True)
                i.timer = time.time()
                xenon.append(i)
                uranium.remove(i)
                neutronsT.remove(j)  # Remove the neutron after collision
                break

def checkCollisionXenon(xenon, neutronsT):
    for i in xenon:
        for j in neutronsT:
            if i.rect.colliderect(j.rect):
                i.timer = 0
                i.type = "N"
                xenon.remove(i)
                neutronsT.remove(j)
                break


def replenish(uranium, element):
    if element.type == "N":
        element.type = "U"
        uranium.append(element)
        return True
    return False

def autoControl(neutronsT, neutronsF, power, rods):
    if (len(neutronsT) + len(neutronsF)) < power:
        if rods[0].posy > 70 - 750:
            for i in range(len(rods)):
                if i % 2 == 0:  # First group (0)
                    rods[i].posy -= 1
                    rods[i].rect.top -= 1
        elif rods[1].posy > 70 - 750:
            for i in range(len(rods)):
                if i % 2 == 1:  # Second group (1)
                    rods[i].posy -= 1
                    rods[i].rect.top -= 1
        else:
            for i in rods:
                i.posy = 70 - 750
                i.rect.top = 70 - 750
    elif (len(neutronsT) + len(neutronsF)) > power:
        if rods[1].posy < 55:
            for i in range(len(rods)):
                if i % 2 == 1:  # First group (0)
                    rods[i].posy += 1
                    rods[i].rect.top += 1
        elif rods[0].posy < 55:
            for i in range(len(rods)):
                if i % 2 == 0:  # Second group (1)
                    rods[i].posy += 1
                    rods[i].rect.top += 1
        else:
            for i in rods:
                i.posy = 55
                i.rect.top = 55




def main():
    grid = Grid(40,20)
    for i in range(grid.sizex):
        for j in range(grid.sizey):
            grid.eGrid[i][j] = Element(i,j, 50 + 37*i, 75 + 37*j, "N")
            #grid.wGrid[i][j] = Water()

    simulating = True
    neutronsF = []
    neutronsT = []
    uranium = []
    xenon = []
    controlRods = [ControlRod(100+i*37*4,55) for i in range(10)]
    moderatorRods = [ModeratorRod(100+i*37*4-37*2,55) for i in range(11)]
    timeCheckN = 0
    timeCheckU = 0
    startCount = 120
    timeBetweenRelease = 1
    neutronAim = 40
    for i in range(startCount):
        valid = False
        attempts = 0
        while not valid and attempts < 100:
            valid = replenish(uranium, grid.eGrid[randint(0,grid.sizex-1)][randint(0,grid.sizey-1)])
            attempts += 1


    while simulating:  #main loop -------------------------------------------------------------------------------------
        pygame.display.update()
        window.fill(WHITE)
        grid.draw()
        neutronCount = font.render(str(len(neutronsF)+len(neutronsT)),True,BLACK)
        window.blit(neutronCount,(750,0))
        autoControl(neutronsT,neutronsF,neutronAim,controlRods)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                simulating = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    simulating = False
                if event.key == pygame.K_UP:
                    neutronAim = 99999
                if event.key == pygame.K_DOWN:
                    neutronAim = 0
                if event.key == pygame.K_SPACE:
                    neutronAim = 40
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

        neutronsF = [i for i in neutronsF if not (i.posx < -10 or i.posx > 1930 or i.posy < -10 or i.posy > 1090)]
        for i in neutronsF:
            i.move()
            i.draw()
        
        neutronsT = [i for i in neutronsT if not (i.posx < -10 or i.posx > 1930 or i.posy < -10 or i.posy > 1090)]
        for i in neutronsT:
            i.move()
            i.draw()
        
        for i in xenon:
            if i.type != "X":
                if i.checkSecond(time.time()):
                    if random() < 0.3:
                        i.type = "X"
                    else:
                        xenon.remove(i)

        for i in moderatorRods:
            i.draw()
            for j in neutronsF:
                if i.rect.colliderect(j.rect):
                    i.collide(neutronsF,neutronsT,j)

        for i in controlRods:
            i.draw()
            for j in neutronsF:
                if i.rect.colliderect(j.rect):
                    i.collide(neutronsF,neutronsT,j)
            for j in neutronsT:
                if i.rect.colliderect(j.rect):
                    i.collide(neutronsF,neutronsT,j)


        if len(neutronsT) > 0:
            if len(uranium) > 0:
                checkCollision(uranium, xenon, neutronsT, neutronsF)
            if len(xenon) > 0:
                checkCollisionXenon(xenon, neutronsT)


        timeBetweenRelease = 0.6 - random()/2
        if timeCheckN == 0:
            timeCheckN = time.time()
        else:
            if time.time() - timeCheckN > timeBetweenRelease:
                timeCheckN = 0
                valid = False
                attempts = 0
                while not valid and attempts < 20:
                    x = randint(0,grid.sizex-1)
                    y = randint(0,grid.sizey-1)
                    if grid.eGrid[x][y].type != "X":
                        valid = True
                        grid.eGrid[x][y].releaseNeutron(uranium, neutronsF)
                    attempts += 1

        if len(neutronsF) + len(neutronsT) > 40:
            if 120 + (len(neutronsF)+len(neutronsT)/10) < 300:
                num = 120 + (len(neutronsF)+len(neutronsT)/10)
            elif 120 + (len(neutronsF)+len(neutronsT)/10) < 500:
                num = 250
            else:
                num = 400
        else:
            num = 120
        while len(uranium) < num:
            valid = False
            while not valid:
                valid = replenish(uranium, grid.eGrid[randint(0,grid.sizex-1)][randint(0,grid.sizey-1)])

        clock.tick(70)

main()