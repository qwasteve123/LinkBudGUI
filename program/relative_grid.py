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
        self.background = None

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
        if self.background == None:    
            self.background = Background(self)
        else:
            self.background.remove_from_canvas()
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
        self._screen_anchor = np.array([0,0])
        self.world_anchor = anchor

        wg.shape_list.append(self)

    @property
    def scale(self):
        return ZOOM_SCALE**(self.wg.scale_step)

    def remove_from_canvas(self):
        self._canvas.delete(self.id)

    # Input screen_center_world return image center
    def _world_to_image(self,world):
        img_world = world + self.size/2
        return img_world

    def _update_screen_center_world(self):
        self._screen_center_world_pt = self.wg.screen_center_world_pt

    def _update_scale_step(self):
        self._scale_step = self.wg.screen_center_world_pt

    # Get coordinate of image of area that should be cropped
    def _get_coor_from_image_center(self):
        img_center_world_pt = self._world_to_image(self._screen_center_world_pt)
        img_pt1 = img_center_world_pt - (self._screen_size/2)/self.scale
        img_pt2 = img_center_world_pt + (self._screen_size/2)/self.scale
        self._get_screen_anchor(img_pt1,img_pt2)
        img_pt1,img_pt2 = self._get_boundaries(img_pt1,img_pt2)
        return (img_pt1[0],img_pt1[1],img_pt2[0],img_pt2[1])

    # Handle the screen boundaries when showing on canvas
    def _get_screen_anchor(self,img_pt1,img_pt2):
        x,y, origin = 0,1,[0,0]
        center_x = (min(img_pt2[x],self.size[x])+max(img_pt1[x],origin[x]))/2
        center_y = (min(img_pt2[y],self.size[y])+max(img_pt1[y],origin[y]))/2

        self._screen_anchor[0] =center_x*self.scale
        self._screen_anchor[1] =center_y*self.scale

    def _get_boundaries(self,img_pt1,img_pt2):
        x,y  = 0,1,
        origin=np.zeros(2)
        img_pt1 = np.array([max(img_pt1[x],origin[x]),max(img_pt1[y],origin[y])])
        img_pt2 = np.array([min(img_pt2[x],self.size[x]),min(img_pt2[y],self.size[y])])

        return img_pt1,img_pt2

###########################################################
# Inherit GridShapes, responsible for image cropping, resizing and showing on canvas
# Background of the drawing, CAD image
class Background(Grid_Shapes):

    # resize image 
    def _resize_image(self,image):
        size = (int(image.size[0]*self.scale), int(image.size[1]*self.scale))
        image = image.resize(size, pil.Image.BOX)
        return image

    # width/ height ratio for resizing
    @ property
    def ratio_aspect(self):
        if self.size == None:
            return None
        return self.size[1]/self.size[0]

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
        self._to_canvas(image)
        return self

    # Add background image
    def _add_new_image(self,filepath):
        image = self._create_image(filepath)
        self.size = np.array([image.width,image.height])
        self._primitive_image = image
        return image

    # grouped crop and resize as it is used in panning
    def _crop_and_resize_image(self,image):
        cropped_img = self._crop_image(image,self._get_coor_from_image_center())
        resized_image = self._resize_image(cropped_img)
        return resized_image

    # Turn the image to TkImage object and place it on canvas
    def _to_canvas(self,image):
        tk_image = pil.ImageTk.PhotoImage(image)
        self._tk_temp_img = tk_image
        self.id = self._canvas.create_image(self.wg.world_dir_screen(np.array([0,0])).tolist(),anchor=CENTER,image=tk_image,tag=self.tag)

    # pan move of 
    def move(self,screen_center_world):
        self.remove_from_canvas()
        self._update_screen_center_world(screen_center_world)
        self.add_background(self.filepath,'pan')

    def zoom(self,screen_center_world,scale_step):
        self.remove_from_canvas()
        self._update_screen_center_world(screen_center_world)
        self._update_scale_step(scale_step)
        self.add_background(self.filepath,'pan')

class Straight_Lines(Grid_Shapes):
    def __init__(self, world_grid: WorldGrid,screen_pt1,screen_pt2,fill='black',width=2, anchor_x=0, anchor_y=0):
        super().__init__(world_grid, anchor_x, anchor_y)
        self.draw(screen_pt1,screen_pt2,fill,width)
        self._create(screen_pt1,screen_pt2,fill,width)
        self._set_attribute(screen_pt1,screen_pt2,fill,width)

    def _create(self,screen_pt1,screen_pt2,fill,width):

        self.id = self._canvas.create_line(screen_pt1.tolist(),screen_pt2.tolist(), fill= fill, width=width,tag=self.tag)

    def _set_attribute(self,pt_1,pt_2,fill,width):
        self.fill, self.width = fill, width
        self.world_anchor_1 = self.wg.screen_to_world(pt_1)
        self.world_anchor_2 = self.wg.screen_to_world(pt_2)
        self.pt_1,self.pt_2= pt_1,pt_2
         
    def move(self,screen_center_world_pt):
        self.remove_from_canvas()
        self._update_screen_center_world(screen_center_world_pt)
        self._update_screen_anchors()
        self._create(self.pt_1,self.pt_2,fill=self.fill,width=self.width)

    def zoom(self,screen_center_world_pt,scale_step):
        self._update_scale_step(scale_step)
        self.move(screen_center_world_pt)

    def _update_screen_anchors(self):
        self.pt_1 = self.wg.world_to_screen(self.world_anchor_1)
        self.pt_2 = self.wg.world_to_screen(self.world_anchor_2)

class Rectangle(Straight_Lines):
    def __init__(self, world_grid: WorldGrid, pt_1, pt_2, fill=None, width=2, anchor_x=0, anchor_y=0):
        super().__init__(world_grid, pt_1, pt_2, fill, width, anchor_x, anchor_y)
        
    def _create(self,pt_1, pt_2,fill,width):
        self.id = self._canvas.create_rectangle(pt_1.tolist(),pt_2.tolist(), fill= fill, width=width,tag= self.tag)

class Coupler():
    def __init__(self, world_grid: WorldGrid, anchor_1=np.array([0,0])):
        self.draw(world_grid,anchor_1,world_grid.scale_step)

    def draw(self,world_grid: WorldGrid,anchor_x,anchor_y,scale_step):
        s = self.fix_scale(scale_step)
        world_grid.draw_rectangle(anchor_x-50*s, anchor_y-25*s,anchor_x+50*s, anchor_y+25*s)
        world_grid.draw_s_line(anchor_x,anchor_y,anchor_x,anchor_y-50*s)
        world_grid.draw_s_line(anchor_x,anchor_y,anchor_x+35*s,anchor_y)
    
    def fix_scale(self,scale_step):
        return ZOOM_SCALE**scale_step

if __name__ == "__main__":
    pass
