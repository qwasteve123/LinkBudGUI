from time import sleep
import PIL as pil
from tkinter import *
import numpy as np

# Zoom scale for all items in the canvas
ZOOM_SCALE = 1.1

# Helps keeping shapes and manage the screen - world transform, telling GridShapes component the coordinates
# to move.
class WorldGrid():
    def __init__(self,screen_width,screen_height,canvas):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale_step = 0
        self.canvas = canvas
        self.shape_list = []
        self.screen_center_world_x = 0
        self.screen_center_world_y = 0       

    # Scale = scale_step * ZOOM_SCALE
    def _set_scale_step(self,scale_step):
        self.scale_step = scale_step

    # Add CAD image file as background
    def add_background(self,filepath):
        self._reset_screen_world_center()
        self._reset_scale_step()    
        try:
            self.background.delete()
            self.background.add_background(filepath)
        except:
            self.background = Background(self.canvas,self.screen_width,self.screen_height,0,0,0)
            self.shape_list.append(self.background)
            self.background.add_background(filepath)

    def add_straight_line():
        pass

    # set the world coordinate that the screen center showing
    def _set_screen_center_world(self,dev_x: float =0 ,dev_y: float=0):
        try:
            self.screen_center_world_x -= dev_x*(ZOOM_SCALE**(-self.scale_step))
            self.screen_center_world_y -= dev_y*(ZOOM_SCALE**(-self.scale_step))
        except:
            self.screen_center_world_x ,self.screen_center_world_y = 0,0

    # reset the screen center to world center
    def _reset_screen_world_center(self):
            self.screen_center_world_x = 0
            self.screen_center_world_y = 0

    # reset scale_step to its initial stage
    def _reset_scale_step(self):
            self.scale_step = 0

    def _get_world_center(self):
        try:
             x,y = self.screen_center_world_x ,self.screen_center_world_y
        except:
            self._set_screen_center_world()
        return self.screen_center_world_x,self.screen_center_world_y

    # The world coordinate that the screen is showing
    @staticmethod
    def screen_to_world(screen_x,screen_y,scale_step,screen_width,screen_height):
        world_x = (screen_x - screen_width/2)*(ZOOM_SCALE**scale_step)
        world_y = -(screen_y - screen_height/2)*(ZOOM_SCALE**scale_step)
        return world_x, world_y

    # The screen coordinate in the world 
    @staticmethod
    def world_to_screen(world_x,world_y,scale_step,screen_width,screen_height):
        screen_x = world_x*(ZOOM_SCALE**scale_step) + screen_width/2
        screen_y = -world_y*(ZOOM_SCALE**scale_step) + screen_height/2
        return screen_x, screen_y

    # pan move all shapes i.e. background, lines and others
    def pan_move(self,x_dev,y_dev):
        for shape in self.shape_list:
            self._set_screen_center_world(x_dev,y_dev)
            shape.move(self.screen_center_world_x,self.screen_center_world_y)

    # zoom all shapes
    def zoom(self,event_x,event_y,zoom_in):
        self._zoom_deviation(event_x,event_y,zoom_in)
        for shape in self.shape_list:
            shape.zoom(self.screen_center_world_x,self.screen_center_world_y,self.scale_step)

    # Zooming will expand the image from a point.
    # zoom deviation corrects the deviation from focus point.
    def _zoom_deviation(self,event_x,event_y,zoom_in):
        self.scale_step += zoom_in
        dev_x, dev_y = self.screen_to_world(event_x,event_y,0,self.screen_width,self.screen_height)
        self.screen_center_world_x = zoom_in*dev_x*(ZOOM_SCALE-1)*ZOOM_SCALE**(-self.scale_step) + self.screen_center_world_x
        self.screen_center_world_y = zoom_in*dev_y*(ZOOM_SCALE-1)*ZOOM_SCALE**(-self.scale_step) + self.screen_center_world_y

############################################################
# Common GridShapes inherited by other shapes. 
# Get screen center from World_Grid and help shapes showcase.
class Grid_Shapes():
    def __init__(self,canvas,screen_width,screen_height,scale_step,anchor_x,anchor_y,screen_center_world_x=0,screen_center_world_y=0):
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._canvas = canvas
        self._scale_step = scale_step
        self.width, self.height = 0,0
        self._screen_anchor_x, self._screen_anchor_y = 0,0
        self.world_anchor_x, self.world_anchor_y = anchor_x,anchor_y
        self._screen_center_world_x, self._screen_center_world_y = screen_center_world_x,screen_center_world_y

    def delete(self):
        self._canvas.delete(self.bkgd)

    # Input screen_center_world return image center
    def _world_to_image(self,world_x,world_y):
        img_world_x = world_x + self.width/2
        img_world_y = -world_y + self.height/2
        return img_world_x, img_world_y

    def _update_screen_center_world(self,screen_center_world_x,screen_center_world_y):
        self._screen_center_world_x,self._screen_center_world_y = screen_center_world_x,screen_center_world_y

    def _update_scale_step(self,scale_step):
        self._scale_step = scale_step

    # Get coordinate of image of area that should be cropped
    def _get_coor_from_image_center(self,screen_center_world_x,screen_center_world_y,scale_step):
        img_center_world_x, img_center_world_y = self._world_to_image(screen_center_world_x, screen_center_world_y)
        world_x1 = img_center_world_x - (self._screen_width/2)*(ZOOM_SCALE**(-scale_step))
        world_y1 = img_center_world_y - (self._screen_height/2)*(ZOOM_SCALE**(-scale_step))
        world_x2 = img_center_world_x + (self._screen_width/2)*(ZOOM_SCALE**(-scale_step))
        world_y2 = img_center_world_y + (self._screen_height/2)*(ZOOM_SCALE**(-scale_step))
        self._get_screen_anchor(world_x1, world_y1, world_x2, world_y2,self._scale_step)
        world_x1, world_y1, world_x2, world_y2 = self._get_boundaries(world_x1, world_y1, world_x2, world_y2,scale_step)
        return world_x1, world_y1, world_x2, world_y2

    # Handle the screen boundaries when showing on canvas
    def _get_screen_anchor(self,world_x1, world_y1, world_x2, world_y2,scale_step):
        dev_x, dev_y = 0,0
        if world_x1 < 0 and world_x2 > self.width:
            dev_x = (self.width - (world_x2 + world_x1))*(ZOOM_SCALE**(scale_step))
        elif world_x2 > self.width:
            dev_x = (self.width - world_x2)*(ZOOM_SCALE**(scale_step))
        elif world_x1 < 0:
            dev_x = (-world_x1)*(ZOOM_SCALE**(scale_step))

        if world_y1 < 0 and world_y2 > self.height:
            dev_y = (self.height - (world_y2 + world_y1))*(ZOOM_SCALE**(scale_step))
        elif world_y2 > self.height:
            dev_y = (self.height - world_y2)*(ZOOM_SCALE**(scale_step))
        elif world_y1 < 0:
            dev_y = (-world_y1)*(ZOOM_SCALE**(scale_step))
            # dev_y = (world_x2 - self.width)*(ZOOM_SCALE**(scale_step))


        self._screen_anchor_x = dev_x/2
        self._screen_anchor_y = -dev_y/2
        self._update_screen_center_world

    def _get_boundaries(self,world_x1, world_y1, world_x2, world_y2,scale_step):
        if world_x1 < 0:
            world_x1 = 0
        if world_y1 < 0:
            world_y1 = 0            
        if world_x2 > self.width:
            world_x2 = self.width  
        if world_y2 > self.height:
            world_y2 = self.height
        return (world_x1, world_y1, world_x2, world_y2)



###########################################################
# Inherit GridShapes, responsible for image cropping, resizing and showing on canvas
# Background of the drawing, CAD image
class Background(Grid_Shapes):

    # resize image 
    def _resize_image(self,image,scale_step,dev_width =0,dev_height=0):
        size = (self._screen_width-dev_width, self._screen_height-dev_height)
        size = (int(image.width*(ZOOM_SCALE**(scale_step))), int(image.height*(ZOOM_SCALE**(scale_step))))
        image = image.resize(size, pil.Image.BOX)
        return image

    # width/ height ratio for resizing
    @ staticmethod
    def _get_ratio_aspect(width,height):
        return height/width

    # Crop image with given coordinates
    def _crop_image(self,image,area_coordinate):
        cropped = image.crop(area_coordinate)
        return cropped

    # Open image from a given folder directory
    def _create_image(self,filepath):
        image = pil.Image.open(filepath)
        return image

    # update background when panning, zooming or adding new background
    def add_background(self,filepath,type=""):
        self.filepath = filepath
        if type == 'pan':
            image = self._crop_and_resize_image(self._primitive_image)
        else:  
            image = self._add_new_image(filepath)
            image = self._crop_and_resize_image(image)
        self._to_canvas(image,0,0)

    # Add background image
    def _add_new_image(self,filepath):
        image = self._create_image(filepath)
        self.width, self.height = image.width,image.height
        self._primitive_image = image
        self.ratio_aspect = self._get_ratio_aspect(image.width,image.height)
        return image

    # grouped crop and resize as it is used in panning
    def _crop_and_resize_image(self,image):
        cropped_img = self._crop_image(image,self._get_coor_from_image_center(self._screen_center_world_x, self._screen_center_world_y,self._scale_step))
        resized_image = self._resize_image(cropped_img,self._scale_step)
        return resized_image

    # Turn the image to TkImage object and place it on canvas
    def _to_canvas(self,image,x=0,y=0):
        tk_image = pil.ImageTk.PhotoImage(image)
        self._tk_temp_img = tk_image
        self.bkgd = self._canvas.create_image(WorldGrid.world_to_screen(self._screen_anchor_x,self._screen_anchor_y,
                                                                        0,self._screen_width,self._screen_height),anchor=CENTER,image=tk_image)

    # pan move of 
    def move(self,screen_center_world_x,screen_center_world_y):
        self.delete()
        self._update_screen_center_world(screen_center_world_x,screen_center_world_y)
        self.add_background(self.filepath,'pan')

    def zoom(self,screen_center_world_x,screen_center_world_y,scale_step):
        self.delete()
        self._update_screen_center_world(screen_center_world_x,screen_center_world_y)
        self._update_scale_step(scale_step)
        self.add_background(self.filepath,'pan')

class Straight_Lines(Grid_Shapes):
    pass
    


if __name__ == "__main__":
    pass
