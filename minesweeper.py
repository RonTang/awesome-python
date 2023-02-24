import win32gui
import win32api
import pyautogui
import random
import time
import win32process
import win32con
import ctypes
import random
import os
from array import array

rPM = ctypes.windll.kernel32.ReadProcessMemory
#点赞关注唐老师编程~~~~谢谢支持
WINDOW_TITLE = "扫雷"
col_num = 30
line_num = 16
pyautogui.PAUSE = 0
def coordToScreen(game_window,place):
    pos = win32gui.GetWindowRect(game_window)
    x = pos[0]+place[1]*34 + 85
    y = pos[1]+place[0]*34 + 140
    return (x,y)

def coordToScreenFast(pos,place):
    x = pos[0]+place[1]*34 + 85
    y = pos[1]+place[0]*34 + 140
    return (x,y)

def getGameWindow(title):
    game_window = win32gui.FindWindow(None,title)
    while not game_window:
        print('定位游戏窗体失败，3秒后重试...')
        time.sleep(3)
        game_window = win32gui.FindWindow(None,title)
    win32gui.SetForegroundWindow(game_window) 
    return game_window

gamemap = [array('b',[0]*col_num) for i in range(line_num)]

def getGameProcessAndAddress(game_window):
    _,pid = win32process.GetWindowThreadProcessId(game_window)
    process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
    module_handles = win32process.EnumProcessModules(process_handle)
    module_handle = module_handles[0]  # 0 - the executable itself
    #module_file_name = win32process.GetModuleFileNameEx(process_handle, module_handle)
    return process_handle,module_handle

def getGameMap(process_handle,module_handle):
    global line_num,col_num
    src_address = ctypes.c_void_p(module_handle + 0xAAA38)
    dst_address = ctypes.create_string_buffer(8)

    rPM(process_handle.handle,src_address,dst_address,8,0)
    src_address = ctypes.c_void_p(int.from_bytes(dst_address.raw, byteorder='little')+0x18)
    rPM(process_handle.handle,src_address,dst_address,8,0)

    info_address = int.from_bytes(dst_address,byteorder='little')

    line_address = ctypes.c_void_p(info_address+0x0C)
    col_address = ctypes.c_void_p(info_address+0x10)
    rPM(process_handle.handle,line_address,dst_address,4,0)
    line_num = int.from_bytes(dst_address,byteorder='little')
    rPM(process_handle.handle,col_address,dst_address,4,0)
    col_num = int.from_bytes(dst_address,byteorder='little')

    #print("行列信息：",line_num,col_num)
    
    info_address = ctypes.c_void_p(info_address+0x58)
    rPM(process_handle.handle,info_address,dst_address,8,0)
    info_address = ctypes.c_void_p(int.from_bytes(dst_address,byteorder='little')+0x10)
    rPM(process_handle.handle,info_address,dst_address,8,0)

    sweeper_address = int.from_bytes(dst_address,byteorder='little')
    for i in range(col_num):
        v1 = ctypes.c_void_p(sweeper_address + i*8)
        rPM(process_handle.handle,v1,dst_address,8,0)
        v5 = int.from_bytes(dst_address,byteorder='little')+0x10
        rPM(process_handle.handle,ctypes.c_void_p(v5),dst_address,8,0)
        v5 = int.from_bytes(dst_address,byteorder='little')
        for j in range(line_num):
            rPM(process_handle.handle,ctypes.c_void_p(v5),dst_address,1,0)
            gamemap[j][i] = int.from_bytes(dst_address[:1],byteorder='little')
            v5+=1
    


def buildRandomClick():
    holes = []
    floodfillOne()
    for i in range(line_num):
        for j in range(col_num):
            if gamemap[i][j] == 0:
                holes.append((i,j))
                #print(i,j)
                zeros(i,j)
    #print(gamemap)
    for i in range(line_num):
       for j in range(col_num):
            if gamemap[i][j] == 2:
                holes.append((i,j))
                
    #random.shuffle(holes)
    #print(holes)
    return holes
dirs = [(-1,0),(0,1),(1,0),(0,-1),(-1,1),(-1,-1),(1,1),(1,-1)]
def floodfillOne():
    for i in range(line_num):
        for j in range(col_num):
            if gamemap[i][j] == 1:#遍历雷的8个方向
                for d in dirs:
                    nI = i+d[0]
                    nJ = j+d[1]
                    if nI >=0 and nI< line_num and nJ >=0 and nJ< col_num:
                        if gamemap[nI][nJ] == 0:
                            gamemap[nI][nJ] = 2
    
def zeros(x, y):
    gamemap[x][y] = 4   #填充所有0为4
    for d in dirs:
        nX = x+d[0]
        nY = y+d[1]
        if nX >=0 and nX< line_num and nY >=0 and nY< col_num:
            if gamemap[nX][nY]== 2:
                gamemap[nX][nY] = 4
            if gamemap[nX][nY]== 0:
                zeros(nX,nY)

    
game_window = getGameWindow(WINDOW_TITLE)
pos  =  win32gui.GetWindowRect(game_window)
process_handle,module_handle = getGameProcessAndAddress(game_window)

while win32gui.GetForegroundWindow() != game_window:
    win32gui.SetForegroundWindow(game_window)

pyautogui.moveTo(coordToScreenFast(pos,(0,0)))
pyautogui.click()

time.sleep(0.05)
getGameMap(process_handle,module_handle)

clicks = buildRandomClick()

click_count = 0
click_len = len(clicks)
d = 0
#模拟点击4000次
for i in range(4000):
    pyautogui.click(coordToScreenFast(pos,clicks[click_count]),duration=d)
    click_count +=1
    if click_count >= click_len:
        click_count = 0
    if win32gui.GetForegroundWindow() != game_window:
       break

#速度过快容易丢失按键信息
#while win32gui.GetForegroundWindow() == game_window:
##while click_count < click_len:       
##    #pyautogui.moveTo(*coordToScreen(game_window,clicks[click_count]))
##    #print(f"赞关注唐老师编程~~~~谢谢支持")
##    pyautogui.click(coordToScreen(game_window,clicks[click_count]))
##    #print(f"鼠标点击{clicks[click_count][0]}行，{clicks[click_count][1]}列")
##    click_count +=1
##    #if click_count == len(clicks):
##    #    time.sleep(1)
##    #click_count %= len(clicks)
    
    
            
time.sleep(3)        
pyautogui.press('p')       
process_handle.close()
    
