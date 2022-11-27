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
        self.world_grid = WorldGrid(app,self.size,self.canvas)

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
        self.canvas.bind("<Motion>", lambda Event: [self.hover_coor.hover_motion(Event), self.draw_shape.update_temp_draw(Event)])
        self.canvas.bind("<Leave>", self.hover_coor.hover_leave)

        self.zoom_and_pan = PanAndZoom(self)
        self.canvas.bind("<MouseWheel>", lambda Event: [self.zoom_and_pan.mouse_wheel(Event), self.draw_shape.update_temp_draw(Event)])
        self.canvas.bind("<B1-Motion>", lambda Event: [self.zoom_and_pan.pan_move(Event), self.draw_shape.update_temp_draw(Event)])
        self.canvas.bind("<B1-ButtonRelease>", self.zoom_and_pan.pan_release)
        self.canvas.bind("<B2-Motion>", lambda Event: [self.zoom_and_pan.pan_move(Event), self.draw_shape.update_temp_draw(Event)])
        self.canvas.bind("<Button-3>", lambda Event: [self.draw_shape.remove_draw_status(Event)])

        self.canvas.bind("<B2-ButtonRelease>", self.zoom_and_pan.pan_release)
        self.canvas.bind("<Escape>", lambda Event: [self.draw_shape.remove_draw_status(Event)])

        self.draw_shape = DrawShape(self)
        self.canvas.bind("<Button-1>", self.draw_shape.start_draw)

        # set canvas as focus when mouse pointer enter canvas
        self.canvas.bind("<Enter>",self.set_focus)

    # set focus on canvas for drawing    
    def set_focus(self,event):
        event.widget.focus_set()

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
        if event.delta == -120 and self.scale_step <= self.MAX_ZOOM:
                zoom_in = -1
                self.scale_step +=1
        if event.delta == 120 and self.scale_step >= self.MIN_ZOOM:
                zoom_in = 1
                self.scale_step -=1
        self.world_grid.zoom(np.array([event.x,event.y]),zoom_in)

    def pan_release(self,event):
        self.pan_pt1 = None
        self.canvas.config(cursor='tcross')

    def pan_move(self,event):
        if np.any(self.pan_pt1) != None:
            dev_pt = np.array([self.pan_pt1[0]-event.x, event.y-self.pan_pt1[1]])
            self.world_grid.pan_move(dev_pt)
        self.pan_pt1 = np.array([event.x, event.y])
        self.canvas.config(cursor='circle')

class DrawShape():
    def __init__(self,WindowCanvas : WindowCanvas):
        self.draw_pt1 = None
        self.wg = WindowCanvas.world_grid
        self.label_status = WindowCanvas.label_status
        self.draw_status = None
        self.temp_shape = None
        self.is_drawing_seg = False
        self.seg_line = None

    def start_draw(self,event):
        if self.draw_status == None:
            return
        elif np.any(self.draw_pt1) == None:
            self.draw_pt1 = np.array([event.x, event.y])
            self.draw(1,self.draw_pt1)
        else:
            pt2 = np.array([event.x, event.y])
            print(pt2)
            self.draw(2,self.draw_pt1,pt2)

        if self.temp_shape != None:
            if self.draw_status[1] == 'segmented_line':
                pass
            else:
                self.wg.delete_shape(self.temp_shape)
                self.temp_shape = None
                self.draw_pt1 = None
            
            

    def draw(self,draw_status,pt1,pt2=None):
        if draw_status == 1:
            match self.draw_status[1]:
                case 'coupler':
                    shape = self.wg.draw_coupler(pt1)
                    self.draw_pt1 = None
                    return shape
                case None:
                    return
        elif draw_status == 2:
            match self.draw_status[1]:    
                case 's_line':
                    return self.wg.draw_s_line(pt1,pt2)
                case 'rectangle':
                    return self.wg.draw_rectangle(pt1,pt2)
                case 'oval':
                    return self.wg.draw_oval(pt1,pt2)  
                case 'segmented_line':
                    if self.is_drawing_seg:
                        self.seg_line.add_line(pt1,pt2)
                        return self.seg_line
                    else:
                        self.seg_line = self.wg.draw_seg_line(pt1,pt2)
                        self.is_drawing_seg = True
                    return self.seg_line
        else:
            return

    def update_temp_draw(self,event):
        pt2 = np.array([event.x, event.y])
        
        if self.temp_shape != None:
            self.draw_pt1 = self.wg.world_to_screen(self.temp_shape.world_anchor_1)
            self.temp_shape.change_coor(self.draw_pt1,pt2)
            print(pt2)
        elif np.any(self.draw_pt1) != None:
            self.temp_shape = self.draw(self.draw_status[0],self.draw_pt1,pt2)   
    
    def add_background(self):
        filepath = filedialog.askopenfilename(initialdir=self.initialdir)
        self.wg.add_background(filepath)

    def change_draw(self,status):
        self.label_status.config(text=f'Status: {status[1]}')
        self.draw_status = status
        self.draw_pt1 = None
        
    def change_draw_label(self):
        self.label_status.config(text='Status: s_line Specify first point')

    def remove_draw_status(self,event):
        if self.temp_shape != None:
            if self.draw_status[1] == 'segmented_line':
                self.temp_shape = None
                self.seg_line.remove_end_line()
                self.seg_line = None
                self.is_drawing_seg = False
            else:
                self.wg.delete_shape(self.temp_shape)
                self.temp_shape = None
            self.draw_pt1 = None
        self.draw_status = None



if __name__ == "__main__":
    pass 