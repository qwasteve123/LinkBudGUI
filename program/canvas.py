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
        self.size = np.array([width, height])
        self.bkgd_color = HexColor.CANVAS_BACKGROUD.value
        self.row, self.column = row, column
        self.app = app

        self.canvas = Canvas(app,width=self.size[0],height=self.size[1],background=self.bkgd_color,
                        cursor='tcross',borderwidth=0,highlightthickness=0,relief=FLAT)
        self.canvas.grid(row=row,column=column,columnspan=2,sticky=sticky)  
        self.world_grid = WorldGrid(self.size,self.canvas)

        self.create_labels(self.app,self.row,self.column)
        self.key_binding()

    # create coordinate labels and status label
    def create_labels(self,app,row,column):
        self.label_coor = ttk.Label(app,text='Coordinates  x: ---  y: ---')
        self.label_coor.grid(row=row,column=column+1,sticky=SE)
        self.label_status = ttk.Label(app,text='Status: pan')
        self.label_status.grid(row=row,column=column,sticky=SW)
        

    # set key binding for canvas
    def key_binding(self):
        self.hover_coor = HoverCoor(self)
        self.canvas.bind("<Motion>", lambda Event: [self.hover_coor.hover_motion(Event), self.draw_shape.hover_draw(Event)])
        self.canvas.bind("<Leave>", self.hover_coor.hover_leave)

        self.zoom_and_pan = PanAndZoom(self)
        self.canvas.bind("<MouseWheel>", self.zoom_and_pan.mouse_wheel)
        self.canvas.bind("<B1-Motion>", self.zoom_and_pan.pan_move)
        self.canvas.bind("<B1-ButtonRelease>", self.zoom_and_pan.pan_release)
        self.canvas.bind("<B2-Motion>", lambda Event: [self.zoom_and_pan.pan_move(Event), self.draw_shape.pan_draw(Event)])

        self.canvas.bind("<B2-ButtonRelease>", self.zoom_and_pan.pan_release)

        self.draw_shape = DrawShape(self)
        self.canvas.bind("<Button-3>", self.draw_shape.start_draw)
        # self.canvas.bind("<B2-Motion>", self.draw_shape.pan_draw)

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
        self.size = WindowCanvas.size
        self.row = WindowCanvas.row
        self.column = WindowCanvas.column


    def hover_motion(self,event):
        pt = self.world_grid.screen_to_world(np.array([event.x,event.y]))
        self.change_label(pt)
            
    def hover_leave(self,event):
        self.change_label(None)

    def change_label(self,center=None):
        if np.any(center) == None:
            self.label_coor.config(text='Coordinates  x: ---  y: ---' )
        else:
            # self.label_coor.grid(row=self.row,column=self.column+1,sticky=SE)
            self.label_coor.config(text=f'Coordinates  x:{int(center[0])}  y:{int(center[1])}' )

class PanAndZoom():
    def __init__(self,WindowCanvas : WindowCanvas):
        self.world_grid = WindowCanvas.world_grid
        self.canvas = WindowCanvas.canvas
        self.MAX_ZOOM = 30
        self.MIN_ZOOM = -25
        self.scale_step = 0
        self.pan_pt1 = None

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
        self.pan_pt1 = None
        self.canvas.config(cursor='tcross')

    def pan_move(self,event):
        if np.any(self.pan_pt1) != None:
            dev_pt = np.array([event.x-self.pan_pt1[0], self.pan_pt1[1]-event.y])
            self.world_grid.pan_move(dev_pt)
        self.pan_pt1 = np.array([event.x, event.y])
        print(self.pan_pt1)
        sleep(0.05)
        self.canvas.config(cursor='circle')

class DrawShape():
    def __init__(self,WindowCanvas : WindowCanvas):
        self.draw_pt1 = None
        self.world_grid = WindowCanvas.world_grid
        self.label_status = WindowCanvas.label_status
        self.draw_status = None
        self.temp_shape = None

    def start_draw(self,event):
        match self.draw_status:
            case 's_line':
                self.drawline(event)
            case 'rectangle':
                self.draw_rectangle(event)
            case 'coupler':
                self.draw_coupler(event)
            case None:
                pass

    def hover_draw(self,event):
        if self.draw_pt1 != None:
            if self.temp_shape != None:
                self.world_grid.delete_shape(self.temp_shape)
                self.draw_pt1 = self.world_grid.world_to_screen(self.temp_shape.world_anchor_1)
            self.temp_shape = self.world_grid.draw_s_line(self.draw_pt1,np.array([event.x,event.y]))
            
    def pan_draw(self,event):
        if self.draw_pt1 != None:
            if self.temp_shape != None:
                try:
                    self.draw_pt1[0] += event.x-self.pan_x1
                    self.draw_pt1[1] += self.pan_y1-event.y
                except:
                    self.pan_pt1 = np.array([event.x, event.y])
    
    def add_background(self):
        filepath = filedialog.askopenfilename(initialdir=self.initialdir)
        self.world_grid.add_background(filepath)

    def drawline(self,event):
        if self.draw_pt1 == None:
            self.draw_pt1 = np.array([event.x, event.y])
        else:
            pt_2 = np.array([event.x, event.y])
            self.world_grid.draw_s_line(self.draw_pt1,pt_2)
            self.draw_pt1 = None

    def draw_rectangle(self,event):
        if self.draw_pt1 == None:
            self.draw_pt1 = np.array([event.x, event.y])
        else:
            pt_2 = np.array([event.x, event.y])
            self.world_grid.draw_rectangle(self.draw_pt1,pt_2)
            self.draw_pt1 = None

    def draw_coupler(self,event):
        self.world_grid.draw_coupler(np.array([event.x, event.y]))

    def change_draw(self,status):
        self.label_status.config(text=f'Status: {status}')
        self.draw_status = status

    def change_draw_label(self):
        self.label_status.config(text='Status: s_line Specify first point')

if __name__ == "__main__":
    pass 