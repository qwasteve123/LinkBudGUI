from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedStyle
# from pdf2image import convert_fr om_path
from enum import Enum
import os
import time
from PIL import ImageTk,Image
from relative_grid import *

class HexColor(Enum):
    BACKGROUND = '#2d2d2d'
    TITLE = '#222933'
    TOOLTAB = '#3B4453'
    CANVAS_BACKGROUD = '#222831'

class WindowCanvas():
    def __init__(self,app,width,height,row,column,sticky):
        self.width = width
        self.height = height
        self.bkgd_color = HexColor.CANVAS_BACKGROUD.value
        self.MAX_ZOOM = 30
        self.MIN_ZOOM = -25
        self.scale_step = 0
        self.ZOOM_SCALE = 1.1
        self.initialdir= './imag/'
        self.is_hover = False
        self.row = row
        self.column = column
        self.app = app
        self.left_click_mode = 'pan'
        self.draw_x1, self.draw_y1 = None,None

        self.canvas = Canvas(app, 
                        width=self.width,height=self.height, 
                        background=self.bkgd_color,
                        cursor='tcross',borderwidth=0,highlightthickness=0,
                        relief=FLAT)
        self.canvas.grid(row=row,column=column,columnspan=2,sticky=sticky)  
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)
        self.canvas.bind("<B1-Motion>", self.pan_move)
        self.canvas.bind("<B1-ButtonRelease>", self.pan_release)
        self.canvas.bind("<B2-Motion>", self.pan_move)
        self.canvas.bind("<B2-ButtonRelease>", self.pan_release)
        self.canvas.bind("<Button-3>", self.drawline)
        self.canvas.bind("a",self.draw_rectangle)
        self.canvas.bind("<Button-1>",self.focus_set)
        self.canvas.bind("<Motion>", self.hover_motion)
        self.canvas.bind("<Leave>", self.hover_leave)
        self.canvas.focus_set()
        self.label_coor = ttk.Label(app,text='Coordinates  x: ---  y: ---')
        self.label_coor.grid(row=row,column=column+1,sticky=SE)
        self.label_status = ttk.Label(app,text='Status: pan')
        self.label_status.grid(row=row,column=column,sticky=SW)
        self.world_grid = WorldGrid(self.width,self.height,self.canvas)

        # set focus back to canvas for keyboard button binding.
    def focus_set(self,event):
        event.widget.focus_set()

    def hover_motion(self,event):
        x,y = self.world_grid.screen_to_world(event.x,event.y,self.scale_step,self.width,self.height)
        x += self.world_grid.screen_center_world_x
        y += self.world_grid.screen_center_world_y
        self.change_label(x,y)
            
    def hover_leave(self,event):
        self.change_label("","")

    def change_label(self,center_x,center_y):
        if center_x == "":
            self.label_coor.config(text='Coordinates  x: ---  y: ---' )
        else:
            center_x,center_y = int(center_x), int(center_y)
            self.label_coor.grid(row=self.row,column=self.column+1,sticky=SE)
            self.label_coor.config(text=f'Coordinates  x:{center_x}  y:{center_y}' )

    def mouse_wheel(self,event):
        zoom_in = 0
        if event.delta == -120:
            if self.scale_step <= self.MAX_ZOOM:
                zoom_in = -1
                self.scale_step +=1
        if event.delta == 120:
            if self.scale_step >= self.MIN_ZOOM:
                zoom_in = 1
                self.scale_step -=1
        self.world_grid.zoom(event.x,event.y,zoom_in)

    def pan_release(self,event):
        self.pan_x1, self.pan_y1 = None, None
        self.canvas.config(cursor='tcross')

    def pan_move(self,event):
        try:
            x2, y2 = event.x, event.y
            self.world_grid.pan_move(x2-self.pan_x1, self.pan_y1-y2)
            self.pan_x1, self.pan_y1 = event.x, event.y
        except:
            self.pan_x1, self.pan_y1 = event.x, event.y
        sleep(0.05)
        self.canvas.config(cursor='circle')

    def add_background(self):
        filepath = filedialog.askopenfilename(initialdir=self.initialdir)
        self.world_grid.add_background(filepath)

    def drawline(self,event):
        if self.draw_x1 == None:
            self.draw_x1, self.draw_y1 = event.x, event.y
        else:
            x2, y2 = event.x, event.y
            self.world_grid.draw_s_line(self.draw_x1,self.draw_y1,x2,y2)
            self.draw_x1, self.draw_y1 = None,None

    def draw_rectangle(self,event):
        if self.draw_x1 == None:
            self.draw_x1, self.draw_y1 = event.x, event.y
        else:
            x2, y2 = event.x, event.y
            self.world_grid.draw_rectangle(self.draw_x1,self.draw_y1,x2,y2)
            self.draw_x1, self.draw_y1 = None,None

    def drawline_end(self,event):
        self.draw_x1, self.draw_y1 = None, None

    def change_draw_label(self):
        self.label_status.config(text='Status: s_line Specify first point')    

if __name__ == "__main__":
    pass