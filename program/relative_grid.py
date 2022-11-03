from time import sleep
import PIL as pil
from tkinter import *

ZOOMSCALE = 1.1


class WorldGrid():
    def __init__(self,screen_width,screen_height,ratio,canvas):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale_step = 0
        self.canvas = canvas
        self.shape_list = []
        self.bkgd = 0


    def _set_scale_step(self,scale_step):
        self.scale_step = scale_step

    def add_background(self,filepath):
        try:
            self.background.delete()
            self.background.add_background(filepath)
        except:
            self.background = Background(self.canvas,self.screen_width,self.screen_height,self.scale_step)
            self.shape_list.append(self.background)
            self.background.add_background(filepath)

    def pan_move(self,x_dev,y_dev):
        for shape in self.shape_list:
            shape.move(x_dev,y_dev)

    def zoom(self):
        for shape in self.shape_list:
            shape.zoom(x_dev,y_dev)

############################################################

class Grid_Shapes():
    def __init__(self,canvas,screen_width,screen_height,ratio):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.canvas = canvas
        self.ratio = ratio
        self.width, self.height = 0,0
        self.world_center_x, self.world_center_y = 0,0

    def delete(self):
        self.canvas.delete(self.bkgd)

    # Input world center return image center
    def _world_to_image(self,world_center_x,world_center_y):
            img_world_x = world_center_x + self.width/2
            img_world_y = -world_center_y + self.height/2
            return img_world_x, img_world_y


    def _set_world_center(self,dev_x: float =0 ,dev_y: float=0):
        try:
            self.world_center_x -= dev_x
            self.world_center_y -= dev_y
        except:
            self.world_center_x ,self.world_center_y = 0,0

    def _reset_world_center(self,dev_x: float =0 ,dev_y: float=0):
            self.world_center_x = 0
            self.world_center_y = 0

    def _get_world_center(self):
        try:
             x,y = self.world_center_x ,self.world_center_y
        except:
            self._set_world_center()
        return self.world_center_x,self.world_center_y

    def screen_to_world(self,screen_x,screen_y,scale_step):
        world_x = (screen_x - self.screen_width/2)*(ZOOMSCALE**scale_step)
        world_y = -(screen_y - self.screen_height/2)*(ZOOMSCALE**scale_step)
        return world_x, world_y
    def world_to_screen(self,world_x,world_y,scale_step):
        screen_x = world_x*(ZOOMSCALE**scale_step) + self.screen_width/2
        screen_y = -world_y*(ZOOMSCALE**scale_step) + self.screen_height/2
        return screen_x, screen_y
    def get_coor_from_image_center(self,world_center_x,world_center_y,scale_step):
        img_world_center_x, img_world_center_y = self._world_to_image(world_center_x, world_center_y)
        world_x1 = (img_world_center_x - self.screen_width/2)*(ZOOMSCALE**scale_step)
        world_y1 = (img_world_center_y - self.screen_height/2)*(ZOOMSCALE**scale_step)
        world_x2 = (img_world_center_x + self.screen_width/2)*(ZOOMSCALE**scale_step)
        world_y2 = (img_world_center_y + self.screen_height/2)*(ZOOMSCALE**scale_step)
        return (world_x1,world_y1,world_x2,world_y2)

###########################################################

class Background(Grid_Shapes):
    def _resize_image(self,image,scale_step):
        width, height = int(image.width*ZOOMSCALE**scale_step),int(image.height*ZOOMSCALE**scale_step)
        size = (width, height)
        image.resize(size, pil.Image.BOX)
        return image

    @ staticmethod
    def _get_ratio_aspect(width,height):
        return height/width

    def _crop_image(self,image,area_coordinate):
        cropped = image.crop(area_coordinate)
        return cropped

    def _create_image(self,filepath):
        image = pil.Image.open(filepath)
        return image

    def new_background(self,filepath):
        self.add_background(self,filepath)

    def add_background(self,filepath,type=""):
        self.filepath = filepath
        if type == 'pan':
            image = self.crop_and_resize_image(self.primitive_image)
        else:
            self._reset_world_center()
            image = self._add_new_image(filepath)
            image = self.crop_and_resize_image(image)
        self._to_canvas(image,0,0)
        # print(self.world_center_x,self.world_center_y)

    def _add_new_image(self,filepath):
        image = self._create_image(filepath)
        self.width, self.height = image.width,image.height
        self.primitive_image = image
        self.ratio_aspect = self._get_ratio_aspect(image.width,image.height)
        return image

    def crop_and_resize_image(self,image):
        world_center_x, world_center_y = self._get_world_center()
        cropped_img = self._crop_image(image,self.get_coor_from_image_center(world_center_x, world_center_y,0))
        resized_image = self._resize_image(cropped_img,0)
        return resized_image

    def _to_canvas(self,image,x,y):
        tk_image = pil.ImageTk.PhotoImage(image)
        self.tk_temp_img = tk_image
        self.bkgd = self.canvas.create_image(self.world_to_screen(x,y,0),anchor=CENTER,image=tk_image)

    def move(self,dev_x,dev_y):
        self.delete()
        self._set_world_center(dev_x,dev_y)
        self.add_background(self.filepath,'pan')



if __name__ == "__main__":
    pass
