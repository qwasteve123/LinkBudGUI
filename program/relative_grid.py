from PIL import ImageTk,Image
from tkinter import *

# save coordinate of objects and output on screen objects
# get new


class WorldGrid():
    def __init__(self,screen_width,screen_height,ratio,canvas):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ratio = ratio
        self.canvas = canvas

    def add_background():
        pass

    def show_on_screen():
        pass

    ############################################################

    def background(self,filepath):
        image = Image.open(filepath)
        tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_line(300, 35, 300, 200, dash=(10), width=5)



    def canvas_add_image(self,root,filepath):
        self.image, self.primitive_image = self.getimage(filepath,self.height,self.width)
        try:
            self.canvas.delete(self.bkgd)
        except:
            pass
        self.bkgd = self.canvas.create_image(self.width/2,self.height/2,anchor=CENTER,image=self.image)
        self.count = 1
        self.image_centerx, self.image_centery = self.width/2, self.height/2


    class shapes():
        pass




if __name__ == "__main__":
    pass
