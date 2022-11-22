from time import sleep
import PIL as pil
from tkinter import *
import numpy as np

# Zoom scale for all items in the canvas
ZOOM_SCALE = 1.1

# Helps keeping shapes and manage the screen - world transform, telling GridShapes component the coordinates
# to move.
class WorldGrid():
    def __init__(self,screen_size,canvas):
        self.screen_size = screen_size
        self.scale_step = 0
        self.canvas = canvas
        self.shape_list = []
        self.screen_center_world_pt = np.array([0,0])

    @property
    def scale(self):
        return ZOOM_SCALE**self.scale_step

    # Scale = scale_step * ZOOM_SCALE
    def _set_scale_step(self,scale_step):
        self.scale_step = scale_step

    def draw_coupler(self,anchor_pt1):
        coupler = Coupler(self,anchor_pt1)
        return coupler

    # Add lines to world
    def draw_s_line(self,anchor_pt1,anchor_pt2):
        line = Straight_Lines(self,anchor_pt1,anchor_pt2)
        return line

    def draw_rectangle(self,anchor_pt1,anchor_pt2):
        rectangle = Rectangle(self,anchor_pt1,anchor_pt2)
        return rectangle

    # Add CAD image file as background
    def add_background(self,filepath):
        self._reset_screen_world_center()
        self._reset_scale_step()    
        try:
            self.background.remove_from_canvas()
            self.background.add_background(filepath)
        except:
            self.background = Background(self)
            self.background.add_background(filepath)

    # set the world coordinate that the screen center showing
    def _set_screen_center_world(self,dev):
        try:
            self.screen_center_world_pt -= dev*self.scale
        except:
            self.screen_center_world_pt = np.array([0,0])

    # reset the screen center to world center
    def _reset_screen_world_center(self):
            self.screen_center_world_pt = np.array([0,0])

    # reset scale_step to its initial stage
    def _reset_scale_step(self):
            self.scale_step = 0

    # The screen coordinates origin shift to center of screen
    def screen_dir_world(self,screen):
        world = screen - self.screen_size/2
        world[1] *= -1
        return world

    # The screen coordinates shift back to origin
    def world_dir_screen(self,world):
        screen = world + self.screen_size/2
        screen[1] *= -1
        return screen

    # The world coordinate that the screen is showing
    def screen_to_world(self,screen):
        screen = self.screen_dir_world(screen)
        world = screen/self.scale + self.screen_center_world_pt
        return world

    # The screen coordinate in the world 
    def world_to_screen(self,world):
        world = (world - self.screen_center_world_pt)* self.scale
        return self.world_dir_screen(world)

    def delete_shape(self,shape):
        shape.remove_from_canvas()
        self.shape_list.remove(shape)

    # pan move all shapes i.e. background, lines and others
    def pan_move(self,dev):
        self._set_screen_center_world(dev)
        # print('move')
        for shape in self.shape_list:
            # print(type(shape), shape.id)
            shape.move(self.screen_center_world_pt)

    # zoom all shapes
    def zoom(self,mouse_pt,zoom_in):
        self._zoom_deviation(mouse_pt,zoom_in)
        for shape in self.shape_list:
            shape.zoom(self.screen_center_world_pt,self.scale_step)

    # Zooming will expand the image from a point.
    # zoom deviation corrects the deviation from focus point.
    # zoom_in = -1,0 or 1
    def _zoom_deviation(self,mouse_pt,zoom_in):
        self.scale_step += zoom_in
        dev = self.screen_dir_world(mouse_pt)
        self.screen_center_world_pt += zoom_in*dev*(ZOOM_SCALE-1)/self.scale

############################################################
# Common GridShapes inherited by other shapes. 
# Get screen center from World_Grid and help shapes showcase.
class Grid_Shapes():
    def __init__(self,wg : WorldGrid,anchor =np.array([0,0]),tag=None):
        self._screen_size = wg.screen_size
        self._canvas = wg.canvas
        self.wg = wg
        self._scale_step = wg.scale_step
        self._screen_center_world_pt = wg.screen_center_world_pt
        self.tag = tag

        self.size = np.array([0,0])
        self._screen_anchor_x, self._screen_anchor_y = np.array([0,0])
        self.world_anchor = anchor

        wg.shape_list.append(self)

    @property
    def scale(self):
        return ZOOM_SCALE**(self.scale_step)

    def remove_from_canvas(self):
        self._canvas.delete(self.id)

    # Input screen_center_world return image center
    def _world_to_image(self,world):
        img_world = world + self.size/2
        img_world[1] *= -1
        return img_world

    def _update_screen_center_world(self):
        self._screen_center_world_pt = self.wg.screen_center_world_pt

    def _update_scale_step(self):
        self._scale_step = self.wg.screen_center_world_pt

    # Get coordinate of image of area that should be cropped
    def _get_coor_from_image_center(self,screen_center_world_pt):
        img_center_world_pt = self._world_to_image(screen_center_world_pt)
        img_pt1 = img_center_world_pt - (self.size/2)/self.scale
        img_pt2 = img_center_world_pt + (self.size/2)/self.scale
        self._get_screen_anchor(img_pt1,img_pt2)
        img_pt1,img_pt2 = self._get_boundaries(img_pt1,img_pt2)
        return img_pt1,img_pt2

    # Handle the screen boundaries when showing on canvas
    def _get_screen_anchor(self,img_pt1,img_pt2):
        dev_x, dev_y = 0,0
        width,height = self.size
        img_pt1_x, img_pt1_y = img_pt1
        img_pt2_x, img_pt2_y = img_pt2 
        if img_pt1_x < 0 and img_pt2_x > width:
            dev_x = (width - (img_pt2_x + img_pt1_x))*self.scale
        elif img_pt2_x > width:
            dev_x = (width - img_pt2_x)*self.scale
        elif img_pt1_x < 0:
            dev_x = (-img_pt1_x)*self.scale

        if img_pt1_y < 0 and img_pt2_y > height:
            dev_y = (height - (img_pt2_y + img_pt1_y))*self.scale
        elif img_pt2_y > height:
            dev_y = (height - img_pt2_y)*self.scale
        elif img_pt1_y < 0:
            dev_y = (-img_pt1_y)*self.scale

        self._screen_anchor = np.array([dev_x/2,-dev_y/2])

    def _get_boundaries(self,img_pt1,img_pt2):
        img_pt1_x, img_pt1_y = img_pt1
        img_pt2_x, img_pt2_y = img_pt2 
        if img_pt1_x < 0:
            img_pt1_x = 0
        if img_pt1_y < 0:
            img_pt1_y = 0            
        if img_pt2_x > self.size[0]:
            img_pt2_x = self.size[0]  
        if img_pt2_y > self.size[1]:
            img_pt2_y = self.size[1]
        return (img_pt1_x, img_pt1_y,img_pt2_x, img_pt2_y)

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
        self.id = self._canvas.create_image(self.world_grid.world_dir_screen(self._screen_anchor_x,self._screen_anchor_y),
                                                                        anchor=CENTER,image=tk_image,
                                                                        tag=self.tag)

    # pan move of 
    def move(self,screen_center_world_x,screen_center_world_y):
        self.remove_from_canvas()
        self._update_screen_center_world(screen_center_world_x,screen_center_world_y)
        self.add_background(self.filepath,'pan')

    def zoom(self,screen_center_world_x,screen_center_world_y,scale_step):
        self.remove_from_canvas()
        self._update_screen_center_world(screen_center_world_x,screen_center_world_y)
        self._update_scale_step(scale_step)
        self.add_background(self.filepath,'pan')

class Straight_Lines(Grid_Shapes):
    def __init__(self, world_grid: WorldGrid,x1,y1,x2,y2,fill='black',width=2, anchor_x=0, anchor_y=0):
        super().__init__(world_grid, anchor_x, anchor_y)
        self.draw(x1,y1,x2,y2,fill,width)

    def draw(self,x1,y1,x2,y2,fill='black',width=2): 
        self._create(x1,y1,x2,y2,fill,width)
        self._set_attribute(x1,y1,x2,y2,fill,width)

    def _create(self,x1,y1,x2,y2,fill,width):
        point_1, point_2 = (x1,y1), (x2,y2)
        self.id = self._canvas.create_line(point_1,point_2, fill= fill, width=width,tag=self.tag)

    def _set_attribute(self,x1,y1,x2,y2,fill,width):
        self.fill, self.width = fill, width
        self.world_anchor_x1, self.world_anchor_y1 = self.world_grid.screen_to_world(x1,y1)
        self.world_anchor_x2, self.world_anchor_y2 = self.world_grid.screen_to_world(x2,y2)
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2

    def move(self,screen_center_world_x,screen_center_world_y):
        self.remove_from_canvas()
        self._update_screen_center_world(screen_center_world_x,screen_center_world_y)
        self._update_screen_anchors()
        self._create(self.x1,self.y1,self.x2,self.y2,fill=self.fill,width=self.width)

    def zoom(self,screen_center_world_x,screen_center_world_y,scale_step):
        self._update_scale_step(scale_step)
        self.move(screen_center_world_x,screen_center_world_y)

    def _update_screen_anchors(self):
        self.x1, self.y1 = self.world_grid.world_to_screen(self.world_anchor_x1,self.world_anchor_y1)
        self.x2, self.y2 = self.world_grid.world_to_screen(self.world_anchor_x2,self.world_anchor_y2)

class Rectangle(Straight_Lines):
    def __init__(self, world_grid: WorldGrid, x1, y1, x2, y2, fill=None, width=2, anchor_x=0, anchor_y=0):
        super().__init__(world_grid, x1, y1, x2, y2, fill, width, anchor_x, anchor_y)
        
    def _create(self,x1,y1,x2,y2,fill,width):
        self.id = self._canvas.create_rectangle(x1,y1,x2,y2, fill= fill, width=width,tag= self.tag)

class Coupler():
    def __init__(self, world_grid: WorldGrid, anchor_x=0, anchor_y=0):
        self.draw(world_grid,anchor_x,anchor_y,world_grid.scale_step)

    def draw(self,world_grid: WorldGrid,anchor_x,anchor_y,scale_step):
        s = self.fix_scale(scale_step)
        world_grid.draw_rectangle(anchor_x-50*s, anchor_y-25*s,anchor_x+50*s, anchor_y+25*s)
        world_grid.draw_s_line(anchor_x,anchor_y,anchor_x,anchor_y-50*s)
        world_grid.draw_s_line(anchor_x,anchor_y,anchor_x+35*s,anchor_y)
    
    def fix_scale(self,scale_step):
        return ZOOM_SCALE**scale_step

if __name__ == "__main__":
    pass
