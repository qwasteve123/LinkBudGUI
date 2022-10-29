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
        self.count = 1

        self.canvas = Canvas(root, 
                            width=self.width,height=self.height, 
                            background=self.bkgd_color,
                            relief=SUNKEN )

        self.canvas.grid(row=1,column=0)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)

    def mouse_wheel(self,event):
        if event.num == 5 or event.delta == -120:
            self.count -= 1
        if event.num == 4 or event.delta == 120:
            self.count += 1
        self.zoom_in_or_out(self.count)
    

    def openimage(self,root):
        filepath = filedialog.askopenfilename(initialdir='./imag/')
        self.canvas_add_image(root,filepath)

    def canvas_add_image(self,root,filepath):
        self.image, self.primitive_image = self.getimage(filepath,self.height,self.width)
        try:
            self.canvas.delete(self.bkgd)
        except:
            pass
        self.bkgd = self.canvas.create_image(self.width/2,self.height/2,anchor=CENTER,image=self.image)    

    def deletecanvas(self):
        self.canvas.delete(self.bkgd)

    def zoom_in_or_out(self,count):
        # self.ratio_aspect = self.ratio_aspect+ 0.01
        self.image = self.resizeimage(self.primitive_image,self.ratio_aspect*(1+0.05*count))
        print(self.ratio_aspect*(1+0.05*count))
        self.bkgd = self.canvas.create_image(self.width/2,self.height/2,anchor=CENTER,image=self.image)

    def getimage(self,file_path,height,width):
        my_img = Image.open(file_path)
        if my_img.height/my_img.width > height/width:
            ratio_aspect = height/my_img.height
        else:
            ratio_aspect = width/my_img.width
        new_img = self.resizeimage(my_img,ratio_aspect)
        self.ratio_aspect = ratio_aspect
        return new_img, my_img

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
    zoom_out_btn = Button(root,text='zoom out',command=lambda:canvas.zoom_out()).grid(row=2,column=1)
    root.config(menu=menubar)
    root.mainloop()

    