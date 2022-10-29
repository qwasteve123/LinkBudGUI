from tkinter import filedialog
from matplotlib.backend_tools import ZoomPanBase
from pdf2image import convert_from_path
import os
import time
from tkinter import *
from PIL import ImageTk,Image

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



class photoCanvas():

    def __init__(self,root,filepath):
        self.width = 900
        self.height = 600
        self.bkgd_color = 'grey'
        self.ratio_aspect = 1

        self.canvas = Canvas(root, 
                            width=self.width,height=self.height, 
                            background=self.bkgd_color,
                            relief=SUNKEN )

        new_img = self.getimage(filepath,self.height,self.width)
        self.bkgd = self.canvas.create_image(self.width/2,self.height/2,anchor=CENTER,image=new_img)
        self.image = new_img
        self.canvas.grid(row=1,column=0)

    def openimage(self,root):
        filepath = filedialog.askopenfilename(initialdir='./imag/')
        self.canvaschangeimage(root,filepath)

    def canvaschangeimage(self,root,filepath):
        new_img = self.getimage(filepath,self.height,self.width)
        self.canvas.delete(self.bkgd)
        self.bkgd = self.canvas.create_image(self.width/2,self.height/2,anchor=CENTER,image=new_img)
        self.image = new_img

    def deletecanvas(self):
        self.canvas.delete(self.bkgd)

    def zoom_in(self):
        self.ratio_aspect = self.ratio_aspect+ 0.01
        resized_img = self.resizeimage(self.image,self.ratio_aspect+0.01)
        self.bkgd = self.canvas.create_image(self.width/2,self.height/2,anchor=CENTER,image=self.image)
        self.image = resized_img

    def zoom_out(self):
        self.ratio_aspect = self.ratio_aspect+ 0.01
        resized_img = self.resizeimage(self.image,self.ratio_aspect+0.01)
        self.bkgd = self.canvas.create_image(self.width/2,self.height/2,anchor=CENTER,image=self.image)
        self.image = resized_img

    def getimage(self,file_path,height,width):
        my_img = Image.open(file_path)
        if my_img.height/my_img.width > height/width:
            ratio_aspect = height/my_img.height
        else:
            ratio_aspect = width/my_img.width
        new_img = self.resizeimage(my_img,ratio_aspect)
        return new_img

    def resizeimage(self,my_img,ratio_aspect):
        new_size = (int(my_img.width*ratio_aspect),int(my_img.height*ratio_aspect))
        resized = my_img.resize(new_size, Image.ANTIALIAS)
        new_img = ImageTk.PhotoImage(resized)
        return new_img

class MenuBar(Menu):
    def __init__(self,root):

        Menu.__init__(self,root)
        file = Menu(self, tearoff=False)
        file.add_command(label='New')
        file.add_command(label="Open",command=lambda:canvas.openimage(root))  
        file.add_command(label="Save")  
        file.add_command(label="Save as")
        file.add_command(label="Delete",command=lambda:canvas.deletecanvas())     
        file.add_separator()  
        file.add_command(label="Exit", command=root.quit)  
        MenuBar.add_cascade(self,label="File", menu=file)  

if __name__ == "__main__":
    
    root = Tk()
    root.title('Learn python')
    root.geometry('1000x750')
    root.iconbitmap("Image_Folder/icon.ico")

    menubar = MenuBar(root)
    canvas = photoCanvas(root,"imag/B1.jpg")

    zoom_in_btn = Button(root,text='zoom in',command=lambda:canvas.zoom_in()).grid(row=1,column=1)

    root.config(menu=menubar)
    root.mainloop()

    