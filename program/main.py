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
from canvas import *

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

class PageTab():
    def __init__(self,root,width,height,row,column,sticky,rowspan=1,columnspan =1):
        self.my_notebook = ttk.Notebook(root)
        self.my_notebook.grid(padx=5,sticky=sticky,rowspan=rowspan,columnspan=columnspan)

        self.page_frame = ttk.Frame(self.my_notebook, width=width, height=height,relief='raise')
        self.add_frame = ttk.Frame(self.my_notebook, width=width, height=height,relief='raise')

        self.page_frame.grid(row=row,column=column,sticky=sticky)
        self.add_frame.grid(row=row,column=column,sticky=sticky)

        self.my_notebook.add(self.page_frame,text='Home')
        self.my_notebook.add(self.add_frame,text='+')

class ToolBoxTab():
    def __init__(self,app,width,height,row,column,sticky,rowspan=1,columnspan =1):
        my_notebook = ttk.Notebook(app)
        my_notebook.grid(padx=5,pady=4,rowspan=rowspan,columnspan=columnspan)

        my_frame1 = ttk.Frame(my_notebook, width=width, height=height)
        my_frame2 = ttk.Frame(my_notebook, width=width, height=height)
        my_frame3 = ttk.Frame(my_notebook, width=width, height=height)

        my_frame1.grid(row=row,column=column,sticky=sticky)
        my_frame2.grid(row=row,column=column,sticky=sticky)
        my_frame3.grid(row=row,column=column,sticky=sticky)

        my_notebook.add(my_frame1,text='Home')
        my_notebook.add(my_frame2,text='Insert')
        my_notebook.add(my_frame3,text='Annotate')

        line_button = ttk.Button(my_frame1,text= 'line',command=lambda:canvas.draw_shape.change_draw('s_line'))
        line_button.grid(row=0,column=0,sticky=W)
        rectangle_button = ttk.Button(my_frame1,text= 'rectangle',command=lambda:canvas.draw_shape.change_draw('rectangle'))
        rectangle_button.grid(row=0,column=1,sticky=W)
        coupler_button = ttk.Button(my_frame1,text= 'coupler',command=lambda:canvas.draw_shape.change_draw('coupler'))
        coupler_button.grid(row=0,column=2,sticky=W)

if __name__ == "__main__":
    
    root = Tk()
    style = ThemedStyle(root)
    style.set_theme('equilux')
    root.title('Learn python')

    # set window as screen width and height
    width , height = int(root.winfo_screenwidth()), int(root.winfo_screenheight())
    root.geometry(f'{width}x{height}')
    root.state('zoomed')

    root.config(background=HexColor.BACKGROUND.value)
    root.iconbitmap("Image_Folder/icon.ico")
    width,height=root.winfo_width(),root.winfo_height()

    toolbox = ToolBoxTab(root,width-10,100,1,0,N,1,2)
    pagetab = PageTab(root,1,1,1,0,SW)
    canvas = WindowCanvas(pagetab.page_frame,width * 0.7,height-190,2,0,SW)

    canvas.world_grid.add_background('imag/B1.jpg')

    root.mainloop()