import PIL as pil
from tkinter import *

# save coordinate of objects and output on screen objects
# get new


class WorldGrid():
    def __init__(self,screen_width,screen_height,ratio,canvas):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ratio = ratio
        self.canvas = canvas
        self.shape_list = []
        self.bkgd = 0

    def add_background(self,filepath,x,y):
        try:
            self.background.delete(self.canvas)
        except:
            pass
        self.background = self.Background(filepath,self.canvas,x,y,self.screen_width,self.screen_height,self.bkgd)
        self.shape_list.append(self.background)

    def pan_move(self,x_displacement,y_displacement):
        x_displacement, y_displacement

    def to_screen(self):
        pass
    

    def screen_to_world(self,screen_x,screen_y):
        world_x = screen_x + self.screen_width/2
        world_y = -screen_y + self.screen_height/2
        return world_x, world_y
    def world_to_screen(self,world_x,world_y):
        screen_x = world_x - self.screen_width/2
        screen_y = -world_y - self.screen_height/2
        return screen_x, screen_y

    ############################################################

    class Background():
        def __init__(self,canvas,screen_width,screen_height,bkgd):
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.canvas = canvas

        def delete(self,canvas):
            canvas.delete(self.bkgd)

        def create_image(filepath):
            image = pil.Image.open(filepath)
            return image

        def to_canvas(self,image,x,y):
            tk_image = pil.ImageTk.PhotoImage(image)
            self.bkgd = self.canvas.create_image(self.world_to_screen(0,0),anchor=CENTER,image=tk_image)
            self.tk_temp_img = tk_image




        def screen_to_world(self,screen_x,screen_y):
            world_x = screen_x + self.screen_width/2
            world_y = -screen_y + self.screen_height/2
            return world_x, world_y
        def world_to_screen(self,world_x,world_y):
            screen_x = world_x - self.screen_width/2
            screen_y = -world_y - self.screen_height/2
            return screen_x, screen_y



    class Shapes():
        pass

if __name__ == "__main__":
    pass
