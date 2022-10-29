from tkinter import filedialog
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

def getimage(file_path,ratio_aspect):
    my_img = Image.open(file_path)
    new_size = (int(my_img.width*ratio_aspect),int(my_img.height*ratio_aspect))
    resized = my_img.resize(new_size, Image.ANTIALIAS)
    new_img = ImageTk.PhotoImage(resized)
    return new_img

class photoCanvas():
    def __init__(self,root,filepath,ratio):
        # Canvas.__init__(self,root)
        new_img = getimage(filepath,ratio)
        self.canvas = Canvas(root, width=600,height=600)
        self.bkgd = self.canvas.create_image(0,0,anchor=N,image=new_img)
        self.image = new_img
        self.canvas.grid(row=1,column=0)

    def opennewimage(self,root):
        filepath = filedialog.askopenfilename(initialdir='./imag/')
        ratio = 0.1
        self.canvaschangeimage(root,filepath,ratio)

    def canvaschangeimage(self,root,filepath,ratio):
        new_img = getimage(filepath,ratio)
        self.grid_forget()
        # self = Canvas(root, width=600,height=300)
        # self.create_image(0,0,anchor=N,image=new_img)
        # self.image = new_img
        # self.grid(row=1,column=0)

    def deletecanvas(self):
        self.canvas.delete(self.bkgd)

class MenuBar(Menu):
    def __init__(self,root):

        Menu.__init__(self,root)
        file = Menu(self, tearoff=False)
        file.add_command(label='New')
        file.add_command(label="Open",command=lambda:canvas.deletecanvas())  
        file.add_command(label="Save")  
        file.add_command(label="Save as")    
        file.add_separator()  
        file.add_command(label="Exit", command=root.quit)  
        MenuBar.add_cascade(self,label="File", menu=file)  

if __name__ == "__main__":
    
    root = Tk()
    root.title('Learn python')
    root.geometry('1000x750')
    root.iconbitmap("Image_Folder/icon.ico")

    menubar = MenuBar(root)
    canvas = photoCanvas(root,"imag/B1.jpg",0.1)
    canvas.deletecanvas()

    root.config(menu=menubar)
    root.mainloop()

    