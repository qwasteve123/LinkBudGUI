from tkinter import filedialog
from pdf2image import convert_from_path
import os
import time
from tkinter import *
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

class WindowCanvas():
    def __init__(self,root):
        self.width = root.winfo_width()
        self.height = 600
        self.bkgd_color = 'grey'
        self.MAX_ZOOM = 30
        self.MIN_ZOOM = -25
        self.scale_step = 0
        self.ZOOM_SCALE = 1.1
        self.initialdir= './imag/'
        self.is_hover = False

        self.canvas = Canvas(root, 
                        width=self.width,height=self.height, 
                        background=self.bkgd_color,
                        relief=SUNKEN )
        self.canvas.grid(row=0,column=0)   
        self.world_grid = WorldGrid(self.width,self.height,self.canvas)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)
        self.canvas.bind("<B2-Motion>", self.pan_move)
        self.canvas.bind("<B2-ButtonRelease>", self.pan_release)
        self.canvas.bind("<Motion>", self.hover_motion)
        self.canvas.bind("<Leave>", self.hover_leave)
        self.label = Label(root)
        self.label.grid(row=1,column=0,sticky=E)

    def hover_motion(self,event):
            x,y = self.world_grid.screen_to_world(event.x,event.y,self.scale_step,self.width,self.height)
            x += self.world_grid.screen_center_world_x
            y += self.world_grid.screen_center_world_y
            self.change_label(x,y)

    def hover_leave(self,event):
        self.change_label("","")

    def change_label(self,center_x,center_y):
        if center_x == "":
            self.label.config(text="")
        else:
            center_x,center_y = int(center_x), int(center_y)
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

    def pan_move(self,event):
        try:
            x2, y2 = event.x, event.y
            self.world_grid.pan_move(x2-self.x1, self.y1-y2)
            self.x1, self.y1 = event.x, event.y
        except:
            self.x1, self.y1 = event.x, event.y

    def add_background(self):
        filepath = filedialog.askopenfilename(initialdir=self.initialdir)
        self.world_grid.add_background(filepath)

class MenuBar(Menu):
    def __init__(self,root):

        Menu.__init__(self,root)
        file = Menu(self, tearoff=False)
        file.add_command(label='New')
        file.add_command(label="Open",command=lambda:canvas.add_background())  
        file.add_command(label="Save")  
        file.add_command(label="Save as")
        file.add_command(label="Delete",command=lambda:canvas.deletecanvas())     
        file.add_separator()  
        file.add_command(label="Exit", command=root.quit)  
        MenuBar.add_cascade(self,label="File", menu=file)  

if __name__ == "__main__":
    
    root = Tk()
    root.title('Learn python')
    root.geometry('1500x1200')
    root.iconbitmap("Image_Folder/icon.ico")

    menubar = MenuBar(root)
    # canvas = PhotoCanvas(root,"imag/B1.jpg")
    canvas = WindowCanvas(root)

    #For testing
    canvas.world_grid.add_background('imag/B1.jpg')


    root.config(menu=menubar)
    root.mainloop()

    