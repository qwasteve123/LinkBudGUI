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
        self.width, self.height = width, height
        self.bkgd_color = HexColor.CANVAS_BACKGROUD.value
        self.row, self.column = row, column
        self.app = app

        self.canvas = Canvas(app,width=self.width,height=self.height,background=self.bkgd_color,
                        cursor='tcross',borderwidth=0,highlightthickness=0,relief=FLAT)
        self.canvas.grid(row=row,column=column,columnspan=2,sticky=sticky)  

        self.create_labels(self.app,self.row,self.column)
        self.key_binding()

    # create coordinate labels and status label
    def create_labels(self,app,row,column):
        self.label_coor = ttk.Label(app,text='Coordinates  x: ---  y: ---')
        self.label_coor.grid(row=row,column=column+1,sticky=SE)
        self.label_status = ttk.Label(app,text='Status: pan')
        self.label_status.grid(row=row,column=column,sticky=SW)
        self.world_grid = WorldGrid(self.width,self.height,self.canvas)

    # set key binding for canvas
    def key_binding(self):
        self.hover_coor = HoverCoor(self)
        self.canvas.bind("<Motion>", self.hover_coor.hover_motion)
        self.canvas.bind("<Leave>", self.hover_coor.hover_leave)

        self.zoom_and_pan = PanAndZoom(self)
        self.canvas.bind("<MouseWheel>", self.zoom_and_pan.mouse_wheel)
        self.canvas.bind("<B1-Motion>", self.zoom_and_pan.pan_move)
        self.canvas.bind("<B1-ButtonRelease>", self.zoom_and_pan.pan_release)
        self.canvas.bind("<B2-Motion>", self.zoom_and_pan.pan_move)
        self.canvas.bind("<B2-ButtonRelease>", self.zoom_and_pan.pan_release)

        self.draw_shape = DrawShape(self)
        self.canvas.bind("<Button-3>", self.draw_shape.drawline)
        self.canvas.bind("a",self.draw_shape.draw_rectangle)

        # set canvas as focus when mouse pointer enter canvas
        self.canvas.bind("<Enter>",self.set_focus)

    # set focus on canvas for drawing    
    def set_focus(self,event):
        event.widget.focus_set()

    @property
    def scale_step(self):
        step = self.zoom_and_pan.scale_step
        return step

class HoverCoor():
    def __init__(self,WindowCanvas : WindowCanvas):
        self.win_can = WindowCanvas
        self.world_grid = WindowCanvas.world_grid
        self.label_coor = WindowCanvas.label_coor
        self.width = WindowCanvas.width
        self.height = WindowCanvas.height
        self.row = WindowCanvas.row
        self.column = WindowCanvas.column

    def hover_motion(self,event):
        scale_step = self.win_can.scale_step
        x,y = self.world_grid.screen_to_world(event.x,event.y,scale_step,self.width,self.height)
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

class PanAndZoom():
    def __init__(self,WindowCanvas : WindowCanvas):
        self.world_grid = WindowCanvas.world_grid
        self.canvas = WindowCanvas.canvas
        self.MAX_ZOOM = 30
        self.MIN_ZOOM = -25
        self.scale_step = 0

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

class DrawShape():
    def __init__(self,WindowCanvas : WindowCanvas):
        self.draw_x1, self.draw_y1 = None,None
        self.world_grid = WindowCanvas.world_grid
        self.label_status = WindowCanvas.label_status
        
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

    def draw_coupler(self,event):
        if self.draw_x1 == None:
            self.draw_x1, self.draw_y1 = event.x, event.y
        else:
            x2, y2 = event.x, event.y
            self.world_grid.draw_rectangle(self.draw_x1,self.draw_y1,x2,y2)
            self.draw_x1, self.draw_y1 = None,None

    def change_draw_label(self):
        self.label_status.config(text='Status: s_line Specify first point')

if __name__ == "__main__":
    pass 