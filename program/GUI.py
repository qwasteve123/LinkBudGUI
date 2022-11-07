from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedStyle
from pdf2image import convert_from_path
from enum import Enum
import os
import time
from PIL import ImageTk,Image
from relative_grid import *



def convert(file, outputDir):
    outputDir = outputDir + str(round(time.time())) + '/'
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    pages = convert_from_path(file, 500)
    counter = 1
    for page in pages:
        myfile = outputDir +'output' + str(counter) +'.jpg'
        counter = counter + 1
        page.save(myfile, "JPEG")
        print(myfile)
    return myfile

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

        self.canvas = Canvas(app, 
                        width=self.width,height=self.height, 
                        background=self.bkgd_color,
                        cursor='tcross',borderwidth=2,highlightthickness=0,relief=FLAT)
        self.canvas.grid(row=row,column=column,sticky=sticky)  
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)
        self.canvas.bind("<B2-Motion>", self.pan_move)
        self.canvas.bind("<B2-ButtonRelease>", self.pan_release)
        self.canvas.bind("<Motion>", self.hover_motion)
        self.canvas.bind("<Leave>", self.hover_leave)
        self.label = ttk.Label(app)
        self.label.grid(row=row+1,column=column,sticky=SE)
        self.world_grid = WorldGrid(self.width,self.height,self.canvas)

    def hover_motion(self,event):
            x,y = self.world_grid.screen_to_world(event.x,event.y,self.scale_step,self.width,self.height)
            x += self.world_grid.screen_center_world_x
            y += self.world_grid.screen_center_world_y
            self.change_label(x,y)

    def hover_leave(self,event):
        self.change_label("","")

    def change_label(self,center_x,center_y):
        if center_x == "":
            self.label.grid_forget()
        else:
            center_x,center_y = int(center_x), int(center_y)
            self.label.grid(row=self.row+1,column=self.column,sticky=SE)
            self.label.config(text=f'Coordinates  x:{center_x}  y:{center_y}' )

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
        self.x1, self.y1 = None, None
        self.canvas.config(cursor='tcross')

    def pan_move(self,event):
        try:
            x2, y2 = event.x, event.y
            self.world_grid.pan_move(x2-self.x1, self.y1-y2)
            self.x1, self.y1 = event.x, event.y
        except:
            self.x1, self.y1 = event.x, event.y
        sleep(0.05)
        self.canvas.config(cursor='circle')

    def add_background(self):
        filepath = filedialog.askopenfilename(initialdir=self.initialdir)
        self.world_grid.add_background(filepath)

class ToolBoxTab():
    def __init__(self,root,width,height,row,column,sticky):
        my_notebook = ttk.Notebook(root)
        my_notebook.grid(padx=5,pady=4)

        my_frame1 = ttk.Frame(my_notebook, width=width, height=height)
        my_frame2 = ttk.Frame(my_notebook, width=width, height=height)
        my_frame3 = ttk.Frame(my_notebook, width=width, height=height)

        my_frame1.grid(row=row,column=column,sticky=sticky)
        my_frame2.grid(row=row,column=column,sticky=sticky)
        my_frame3.grid(row=row,column=column,sticky=sticky)

        my_notebook.add(my_frame1,text='Home')
        my_notebook.add(my_frame2,text='Insert')
        my_notebook.add(my_frame3,text='Annotate')

class PageTab():
    def __init__(self,root,width,height,row,column,sticky):
        self.my_notebook = ttk.Notebook(root)
        self.my_notebook.grid(padx=5)

        self.page_frame = ttk.Frame(self.my_notebook, width=width, height=height,relief='raise')
        self.add_frame = ttk.Frame(self.my_notebook, width=width, height=height,relief='raise')

        self.page_frame.grid(row=row,column=column,sticky=sticky)
        self.add_frame.grid(row=row,column=column,sticky=sticky)

        self.my_notebook.add(self.page_frame,text='Home')
        self.my_notebook.add(self.add_frame,text='+')

if __name__ == "__main__":
    
    root = Tk()
    style = ThemedStyle(root)
    style.set_theme('equilux')
    root.title('Learn python')
    root.geometry('1500x1200')
    root.config(background=HexColor.BACKGROUND.value)
    # root.config(background='white')
    root.iconbitmap("Image_Folder/icon.ico")

    toolbox = ToolBoxTab(root,1490,100,1,0,N)
    pagetab = PageTab(root,1490,1,1,0,N)
    canvas = WindowCanvas(pagetab.page_frame,1490,600,2,0,S)

    #For testing
    canvas.world_grid.add_background('imag/B1.jpg')

    root.mainloop()

    