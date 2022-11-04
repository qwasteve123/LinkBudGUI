from time import sleep
import PIL as pil
from tkinter import *

ZOOM_SCALE = 1.1


class WorldGrid():
    def __init__(self,screen_width,screen_height,canvas):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale_step = 0
        self.canvas = canvas
        self.shape_list = []
        self.bkgd = 0
        self.screen_center_world_x = 0
        self.screen_center_world_y = 0       


    def _set_scale_step(self,scale_step):
        self.scale_step = scale_step

    def add_background(self,filepath):
        try:
            self.background.delete()
            self.background.add_background(filepath)
        except:
            self._reset_screen_world_center()
            self.background = Background(self.canvas,self.screen_width,self.screen_height,self.scale_step,0,0)
            self.shape_list.append(self.background)
            self.background.add_background(filepath)


    def _set_screen_center_world(self,dev_x: float =0 ,dev_y: float=0):
        try:
            self.screen_center_world_x -= dev_x
            self.screen_center_world_y -= dev_y
        except:
            self.screen_center_world_x ,self.screen_center_world_y = 0,0


    def _reset_screen_world_center(self):
            self.screen_center_world_x = 0
            self.screen_center_world_y = 0

    def _get_world_center(self):
        try:
             x,y = self.screen_center_world_x ,self.screen_center_world_y
        except:
            self._set_screen_center_world()
        return self.screen_center_world_x,self.screen_center_world_y

    @staticmethod
    def screen_to_world(screen_x,screen_y,scale_step,screen_width,screen_height):
        world_x = (screen_x - screen_width/2)*(ZOOM_SCALE**scale_step)
        world_y = -(screen_y - screen_height/2)*(ZOOM_SCALE**scale_step)
        return world_x, world_y

    @staticmethod
    def world_to_screen(world_x,world_y,scale_step,screen_width,screen_height):
        screen_x = world_x*(ZOOM_SCALE**scale_step) + screen_width/2
        screen_y = -world_y*(ZOOM_SCALE**scale_step) + screen_height/2
        return screen_x, screen_y

    def pan_move(self,x_dev,y_dev):
        for shape in self.shape_list:
            self._set_screen_center_world(x_dev,y_dev)
            shape.move(self.screen_center_world_x,self.screen_center_world_y)

    def zoom(self,event_x,event_y,zoom_in):
        self.zoom_deviation(event_x,event_y,zoom_in)
        for shape in self.shape_list:
            shape.zoom(self.screen_center_world_x,self.screen_center_world_y,self.scale_step)

    def zoom_deviation(self,event_x,event_y,zoom_in):
        self.scale_step += zoom_in
        # print(self.scale_step)
        dev_x, dev_y = self.screen_to_world(event_x,event_y,0,self.screen_width,self.screen_height)
        # self.screen_center_world_x = dev_x*(ZOOM_SCALE-1)*ZOOM_SCALE**(zoom_in) + self.screen_center_world_x
        # self.screen_center_world_y = dev_y*(ZOOM_SCALE-1)*ZOOM_SCALE**(zoom_in) + self.screen_center_world_y
        # print(self.scale_step,self.screen_center_world_x,self.screen_center_world_y)

############################################################

class Grid_Shapes():
    def __init__(self,canvas,screen_width,screen_height,scale_step,anchor_x,anchor_y,screen_center_world_x=0,screen_center_world_y=0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.canvas = canvas
        self.scale_step = scale_step
        self.width, self.height = 0,0
        self.anchor_x, self.anchor_y = anchor_x,anchor_y
        self.screen_center_world_x, self.screen_center_world_y = screen_center_world_x,screen_center_world_y

    def delete(self):
        self.canvas.delete(self.bkgd)

    # Input screen_center_world return image center
    def _world_to_image(self,world_x,world_y):
        img_world_x = world_x + self.width/2
        img_world_y = -world_y + self.height/2
        # print(img_world_x, img_world_y)
        return img_world_x, img_world_y

    def world_to_screen(world_x,world_y,scale_step,screen_width,screen_height):
        screen_x = world_x*(ZOOM_SCALE**scale_step) + screen_width/2
        screen_y = -world_y*(ZOOM_SCALE**scale_step) + screen_height/2
        return screen_x, screen_y

    def _update_screen_center_world(self,screen_center_world_x,screen_center_world_y):
        self.screen_center_world_x,self.screen_center_world_y = screen_center_world_x,screen_center_world_y

    def _update_scale_step(self,scale_step):
        self.scale_step = scale_step

    def get_coor_from_image_center(self,screen_center_world_x,screen_center_world_y,scale_step):
        img_center_world_x, img_center_world_y = self._world_to_image(screen_center_world_x, screen_center_world_y)
        world_x1 = img_center_world_x - (self.screen_width/2)*(ZOOM_SCALE**(-scale_step))
        world_y1 = img_center_world_y - (self.screen_height/2)*(ZOOM_SCALE**(-scale_step))
        world_x2 = img_center_world_x + (self.screen_width/2)*(ZOOM_SCALE**(-scale_step))
        world_y2 = img_center_world_y + (self.screen_height/2)*(ZOOM_SCALE**(-scale_step))
        # print('step',self.scale_step,ZOOM_SCALE**(-scale_step))
        print("coor",(world_x1+world_x2)/2,(world_y1+world_y2)/2)
        return (world_x1,world_y1,world_x2,world_y2)

###########################################################

class Background(Grid_Shapes):
    def _resize_image(self,image,scale_step):
        # width, height = int(image.width*ZOOM_SCALE**(-scale_step)),int(image.height*ZOOM_SCALE**(-scale_step))
        size = (self.screen_width, self.screen_height)
        image = image.resize(size, pil.Image.BOX)
        # print(image.width, image.height)
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

    def add_background(self,filepath,type=""):
        self.filepath = filepath
        if type == 'pan':
            image = self.crop_and_resize_image(self.primitive_image)
        else:
            image = self._add_new_image(filepath)
            image = self.crop_and_resize_image(image)
        self._to_canvas(image,0,0)
        # print(self.screen_center_world_x,self.screen_center_world_y)

    def _add_new_image(self,filepath):
        image = self._create_image(filepath)
        self.width, self.height = image.width,image.height
        self.primitive_image = image
        self.ratio_aspect = self._get_ratio_aspect(image.width,image.height)
        return image

    def crop_and_resize_image(self,image):
        cropped_img = self._crop_image(image,self.get_coor_from_image_center(self.screen_center_world_x, self.screen_center_world_y,self.scale_step))
        resized_image = self._resize_image(cropped_img,self.scale_step)
        return resized_image

    def _to_canvas(self,image,x,y):
        tk_image = pil.ImageTk.PhotoImage(image)
        self.tk_temp_img = tk_image
        self.bkgd = self.canvas.create_image(WorldGrid.world_to_screen(x,y,0,self.screen_width,self.screen_height),anchor=CENTER,image=tk_image)

    def move(self,screen_center_world_x,screen_center_world_y):
        self.delete()
        self._update_screen_center_world(screen_center_world_x,screen_center_world_y)
        self.add_background(self.filepath,'pan')

    def zoom(self,screen_center_world_x,screen_center_world_y,scale_step):
        self.delete()
        self._update_screen_center_world(screen_center_world_x,screen_center_world_y)
        self._update_scale_step(scale_step)
        self.add_background(self.filepath,'pan')


if __name__ == "__main__":
    pass
