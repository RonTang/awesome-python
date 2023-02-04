import numpy as np
import cupy as cp
from noise import pnoise3
import pygame
import time
import datetime
#数值区间映射
def map(v,v_min,v_max,n_min,n_max):
    return n_min +(n_max-n_min)/(v_max-v_min) * (v - v_min)


# 初始设置
width = 1600
height = 900
pygame.init()
screen = pygame.display.set_mode((width,height)) 
pygame.display.set_caption("Pygame绘制图形，点赞关注唐老师，谢谢！！")
keep_going = True
radius = 2.5                 #粒子半径
COUNT = 3000                 #粒子数量
surf =screen.convert_alpha() #粒子绘制Suface

colors = np.random.randint(100,255,size=(COUNT,3)) #粒子的随机颜色


gpu_positions = cp.random.randint(0,width,size=(COUNT,2))#粒子在GPU上的位置
cpu_positions = cp.asnumpy(gpu_positions)                #粒子在CPU上的位置
speeds = cp.random.uniform(80,160,size=(COUNT,1))
speeds = cp.hstack([speeds,speeds])
frameCount = 0 #游戏帧数

v = cp.vectorize(map)


def update(frameCount,delta):
    global gpu_positions
    
    #GPU处理粒子的位置
    noises = cp.asarray([pnoise3(position[0]*0.001,2+position[1]*0.001,frameCount*0.0006) \
     for position in cpu_positions])
    noises = v(noises,-1,1,-2*np.pi,2*np.pi).reshape(COUNT,1)
    noises = cp.hstack((cp.cos(noises),cp.sin(noises)))
    rand1 = cp.random.randint(0,width,(COUNT,1))
    rand2 = cp.random.randint(0,height,(COUNT,1))
    gpu_positions = cp.add(gpu_positions,cp.multiply(cp.multiply(speeds,delta),noises))
    f1 = (gpu_positions[:,0]<0)|(gpu_positions[:,0]>width)
    f2 = (gpu_positions[:,1]<0)|(gpu_positions[:,1]>height)
    f = (f1 | f2).reshape((COUNT,1))
    f = cp.hstack((f,f))
    cp.copyto(gpu_positions,cp.hstack((rand1,rand2)),where=f)
    
    
##    如果我们不用GPU加速，可以使用如下CPU代码完成任务
##    for particle in particles:
##        #noiseValue = perlin(particle[0]*0.001,2+particle[1]*0.001)
##        noiseValue = pnoise3(particle[0]*0.001,2+particle[1]*0.001,frameCount*0.0005)
##        noiseValue = map(noiseValue,-1,1,-2*np.pi,2*np.pi)
##        vx = particle[2] * np.cos(noiseValue)  
##        vy = particle[2] * np.sin(noiseValue)
##        particle[0]+=vx
##        particle[1]+=vy
##        if particle[0]<0 or particle[0]>width or particle[1]<0 or particle[1]>height:
##            particle[0] = np.random.randint(0,width)
##            particle[1] = np.random.randint(0,height)
clock = pygame.time.Clock()
font_size = 30
font = pygame.font.SysFont("Microsoft YaHei", font_size)

ms = 0
while keep_going:
    
    #s = time.perf_counter()
    update(frameCount,ms)
    cpu_positions = cp.asnumpy(gpu_positions)
    #e = time.perf_counter()
    #print(e-s)
    for event in pygame.event.get():  # 遍历事件
        if event.type == pygame.QUIT:  # 退出事件
            keep_going = False
    
    surf.fill((0,0,0,7))
    #ugly solution just add fade speed...
    surf.fill((0,0,0,20),(width-400, 8,380,28))
    
    ##使用special_flags进行fill操作无Bug但性能低
    #screen.fill((0,0,0))
    #surf.fill((255, 255, 255, 220),special_flags=pygame.BLEND_RGBA_MULT)#变透明
    #surf.fill((0,0,0,15),special_flags=pygame.BLEND_RGBA_SUB) #变透明
    ##
   
    t = datetime.datetime.now()
    t = t.strftime("%Y/%m/%d %H:%M:%S")
    #if frameCount % 100 == 0:
    fps_num = int(clock.get_fps())
   
    for pid in range(COUNT):
        pygame.draw.circle(surf,colors[pid],cpu_positions[pid],radius)
    
    fps = font.render(f"分辨率:{width}*{height},粒子数:{COUNT},时间:{t}，帧率:{str(fps_num)},记得点赞哦~", True, (255,255,255))
    screen.blit(surf,(0,0))
    screen.blit(fps, (width-1080, 0))
    
    
    
    pygame.display.flip()  # 刷新屏幕
    ms = clock.tick(1000)/1000
    frameCount += 1

# 退出程序
pygame.quit()







