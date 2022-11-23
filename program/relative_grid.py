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
        self.screen_center_world_pt = np.array([0.0,0.0])
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
        self.screen_center_world_pt += dev/self.scale

    # reset the screen center to world center
    def _reset_screen_world_center(self):
            self.screen_center_world_pt = np.array([0.0,0.0])

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
        world[1] *= -1
        screen = world + self.screen_size/2
        return screen

    # The world coordinate that the screen is showing
    def screen_to_world(self,screen):
        screen = self.screen_dir_world(screen)
        return screen/self.scale + self.screen_center_world_pt

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
        for shape in self.shape_list:
            shape.move()

    # zoom all shapes
    def zoom(self,mouse_pt,zoom_in):
        self._zoom_deviation(mouse_pt,zoom_in)
        for shape in self.shape_list:
            shape.zoom()

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
        img_x = world[0] + self.size[0]/2
        img_y = -world[1] + self.size[1]/2
        return np.array([img_x,img_y])

    def _update_screen_center_world(self):
        self._screen_center_world_pt = self.wg.screen_center_world_pt

    # Get coordinate of image of area that should be cropped
    def _get_coor_from_image_center(self):
        img_center_world_pt = self._world_to_image(self._screen_center_world_pt)
        img_pt1 = img_center_world_pt - (self._screen_size/2)/self.scale
        img_pt2 = img_center_world_pt + (self._screen_size/2)/self.scale

        self._get_screen_anchor(img_pt1,img_pt2)
        img_pt1,img_pt2 = self._get_boundaries(img_pt1,img_pt2)
        return (img_pt1[0],img_pt1[1],img_pt2[0],img_pt2[1])

    def _get_screen_anchor(self,world_pt1, world_pt2):
        x,y,dev = 0,1,np.array([0,0])
        if world_pt1[x] < 0 and world_pt2[x] > self.size[0]:
            dev[x] = (self.size[0] - (world_pt2[x] + world_pt1[x]))
        elif world_pt2[x] > self.size[0]:
            dev[x] = (self.size[0] - world_pt2[x])
        elif world_pt1[x] < 0:
            dev[x] = (-world_pt1[x])

        if world_pt1[y] < 0 and world_pt2[y] > self.size[1]:
            dev[y] = (self.size[1] - (world_pt2[y] + world_pt1[y]))
        elif world_pt2[y] > self.size[1]:
            dev[y] = (self.size[1] - world_pt2[y])
        elif world_pt1[y] < 0:
            dev[y] = (-world_pt1[y])

        self._screen_anchor = dev/2*self.scale
        self._screen_anchor[1] *= -1

    def _get_boundaries(self,img_pt1,img_pt2):
        if img_pt1[0] < 0:
            img_pt1[0] = 0
        if img_pt1[1] < 0:
            img_pt1[1] = 0            
        if img_pt2[0] > self.size[0]:
            img_pt2[0] = self.size[0]  
        if img_pt2[1] > self.size[1]:
            img_pt2[1] = self.size[1]
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

        try:
            if type == 'pan':
                image = self._crop_and_resize_image(self._primitive_image)
            else:  
                image = self._add_new_image(filepath)
                image = self._crop_and_resize_image(image)
            self._to_canvas(image,type)
            return self
        except:
            pass

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
    def _to_canvas(self,image,type):
        tk_image = pil.ImageTk.PhotoImage(image)
        self._tk_temp_img = tk_image
        coor = self.wg.world_dir_screen(self._screen_anchor).tolist()
        if type == "pan":
            self._canvas.coords(self.id,coor)
            self._canvas.itemconfig(self.id,image=tk_image)
        else:
            self.id = self._canvas.create_image(coor,anchor=CENTER,image=tk_image,tag=self.tag)

    # pan move of 
    def move(self):
        self._update_screen_center_world()
        self.add_background(self.filepath,'pan')

    def zoom(self):
        self.move()

class Straight_Lines(Grid_Shapes):
    def __init__(self, world_grid: WorldGrid,screen_pt1,screen_pt2,fill='black',width=3):
        super().__init__(world_grid)
        self._create(screen_pt1,screen_pt2,fill,width)
        self._set_attribute(screen_pt1,screen_pt2,fill,width)

    def _create(self,screen_pt1,screen_pt2,fill,width):
        self.id = self._canvas.create_line(screen_pt1.tolist(),screen_pt2.tolist(), fill= fill, width=width,tag=self.tag)

    def _set_attribute(self,pt_1,pt_2,fill,width):
        self.fill, self.width = fill, width
        self.world_anchor_1 = self.wg.screen_to_world(pt_1)
        self.world_anchor_2 = self.wg.screen_to_world(pt_2)
        self.pt_1,self.pt_2= pt_1,pt_2
         
    def move(self):
        self._update_screen_center_world()
        self._update_screen_anchors()
        self.change_coor(self.pt_1[0],self.pt_1[1],self.pt_2[0],self.pt_2[1])

    def change_coor(self,x1,y1,x2,y2):
        self._canvas.coords(self.id,x1,y1,x2,y2)

    def zoom(self):
        self.move()
 
    def _update_screen_anchors(self):
        self.pt_1 = self.wg.world_to_screen(self.world_anchor_1)
        self.pt_2 = self.wg.world_to_screen(self.world_anchor_2)

class Rectangle(Straight_Lines):
    def __init__(self, world_grid: WorldGrid, pt_1, pt_2, fill=None, width=2):
        super().__init__(world_grid, pt_1, pt_2, fill, width)
        
    def _create(self,pt_1, pt_2,fill,width):
        self.id = self._canvas.create_rectangle(pt_1.tolist(),pt_2.tolist(), fill= fill, width=width,tag= self.tag)

class Coupler(Grid_Shapes):
    def __init__(self, world_grid: WorldGrid, anchor_1=np.array([0,0])):
        super().__init__(world_grid, anchor_1)
        self.wg.shape_list.remove(self)
        self.draw(anchor_1)
        
    def draw(self,anchor_1):
        s = self.scale
        x,y = anchor_1
        shape_1 = self.wg.draw_rectangle(np.array([x-50*s, y-25*s]),np.array([x+50*s, y+25*s]))
        shape_2 = self.wg.draw_s_line(np.array([x,y]),np.array([x,y-50*s]))
        shape_3 = self.wg.draw_s_line(np.array([x,y]),np.array([x+35*s,y]))
        self.shape_list = [shape_1,shape_2,shape_3]

class SegmentedLine(Grid_Shapes):
    def __init__(self, world_grid: WorldGrid, anchor_1=np.array([0,0])):
        super().__init__(world_grid, anchor_1)
        self.wg.shape_list.remove(self)
        self.draw(anchor_1)    

if __name__ == "__main__":
    pass
