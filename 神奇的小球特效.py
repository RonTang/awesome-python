import pygame
from math import sin,cos
from noise import pnoise1,pnoise2  
width = 800
height = 800
pygame.init()
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Pygame特效")
keep_going = True
clock = pygame.time.Clock()
count = 500
delta = 50/count
def map(v,v_min,v_max,n_min,n_max):
    return n_min +(n_max-n_min)/(v_max-v_min) * (v - v_min)

while keep_going:
    for event in pygame.event.get():  # 遍历事件
        if event.type == pygame.QUIT:  # 退出事件
            keep_going = False

    screen.fill((0,0,0))
    clock.tick(60)
    step = 0
    mouse_x,mouse_y = pygame.mouse.get_pos()
    cr = map(pnoise1(pygame.time.get_ticks()*0.001),-1,1,100,255)
    cg = map(pnoise1((1000+pygame.time.get_ticks())*0.001),-1,1,100,255)
    cb = map(pnoise1((2000+pygame.time.get_ticks())*0.001),-1,1,100,255)
    #step等距间隔数组 m
    for i in range(count):
        R = 200 + 120*sin(pygame.time.get_ticks()*step*0.00005)
        if R < 200:
            r = map(R,0,200,3,1)
        else:
            r = map(R,200,320,1,5)

        pygame.draw.circle(screen,(cr,cg,cb),(R * sin(i) + width/2,R * cos(i) +height/2),r)
        step+=delta

    pygame.display.flip()
pygame.quit()

        
    
