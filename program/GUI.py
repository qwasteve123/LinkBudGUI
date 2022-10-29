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
        self.MAX_ZOOM = 30
        self.MIN_ZOOM = 0
        self.ZOOM_SCALE = 1.1


        self.canvas = Canvas(root, 
                            width=self.width,height=self.height, 
                            background=self.bkgd_color,
                            relief=SUNKEN )

        self.canvas.grid(row=1,column=0)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)
        self.canvas.bind("<B2-Motion>", self.pan_move)
        self.canvas.bind("<B2-ButtonRelease>", self.test)

    def mouse_wheel(self,event):
        if event.num == 5 or event.delta == -120:
            if self.count > self.MIN_ZOOM:
                self.count -= 1
        if event.num == 4 or event.delta == 120:
            if self.count < self.MAX_ZOOM - 1:
                self.count += 1
        self.zoom_in_or_out(self.count)

    def test(self,event):
        self.x1, self.y1 = None, None

    def pan_move(self,event):
        try:
            x2, y2 = event.x, event.y
            self.canvas.move(self.bkgd, x2-self.x1, y2-self.y1)
            self.image_center(x2-self.x1, y2-self.y1)
            self.x1, self.y1 = event.x, event.y
            self.crop_move(self.count)
            
        except:
            self.x1, self.y1 = event.x, event.y

    def image_center(self,x_displacement, y_displacement):
        self.image_centerx += x_displacement
        self.image_centery += y_displacement
        print(self.image_centerx,self.image_centery,x_displacement,y_displacement)

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
        self.count
        self.background_list = self.save_background()
        self.image_centerx, self.image_centery = self.width/2, self.height/2

    def save_background(self):
        dict = {}
        for index in range(self.MIN_ZOOM,self.MAX_ZOOM,1):
            dict[index] = self.resizeimage(self.primitive_image,self.ratio_aspect*(self.ZOOM_SCALE**index))
        return dict

    def deletecanvas(self):
        self.canvas.delete(self.bkgd)

    def zoom_in_or_out(self,count):
        # self.zoom_image = self.resizeimage(self.primitive_image,self.ratio_aspect*(1.1**count))
        cropped_image = self.cropimage2(self.background_list[self.count])
        self.image = self.to_tkimage(cropped_image)
        self.bkgd = self.canvas.create_image(self.image_centerx,self.image_centery,anchor=CENTER,image=self.image)
        print(self.count)

    def crop_move(self,count):
        cropped_image = self.cropimage(self.background_list[self.count])
        self.image = self.to_tkimage(cropped_image)
        self.bkgd = self.canvas.create_image(self.width/2,self.height/2,anchor=CENTER,image=self.image)
        print(self.count)

    def getimage(self,file_path,height,width):
        image = Image.open(file_path)
        if image.height/image.width > height/width:
            ratio_aspect = height/image.height
        else:
            ratio_aspect = width/image.width
        resized = self.resizeimage(image,ratio_aspect)
        tk_image = self.to_tkimage(resized)
        self.ratio_aspect = ratio_aspect
        return tk_image, image

    def resizeimage(self,image,ratio_aspect):
        new_size = (int(image.width*ratio_aspect),int(image.height*ratio_aspect))
        resized = image.resize(new_size, Image.BOX)
        return resized

    def to_tkimage(self,image):
        tk_image = ImageTk.PhotoImage(image)
        return tk_image

    def cropimage2(self,image):
        # crop from center of image with canvas frame
        if self.count > 3:
            x1, y1 = image.width/2, image.height/2
            x2, y2 = self.width/2, self.height/2
            coordinate = 0.95*x1-x2, 0.95*y1-y2, 1.05*x1+x2, 1.05*y1+y2
            print(coordinate)
            cropped = image.crop((coordinate))
        else:
            cropped = image
        return cropped

    def cropimage(self,image):
        # crop from center of image with canvas frame
        if self.count > 3:
            x1, y1 = image.width/2, image.height/2
            x2, y2 = self.image_centerx-self.width/2, self.image_centery-self.height/2
            x3, y3 = self.width/2, self.height/2
            print(x1,x2,x3,y1,y2,y3)
            coordinate = (x1-x2-x3), (y1-y2-y3), (x1-x2+x3), (y1-y2+y3)
            print(coordinate)
            cropped = image.crop((coordinate))
        else:
            cropped = image
        return cropped

    def update_image(self):
        pass

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

    