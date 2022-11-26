from time import sleep
import PIL as pil
from tkinter import *
import numpy as np

# Zoom scale for all items in the canvas
ZOOM_SCALE = 1.2

# Helps keeping shapes and manage the screen - world transform, telling GridShapes component the coordinates
# to move.
class WorldGrid():
    def __init__(self,app,screen_size,canvas:Canvas):
        self.screen_size = screen_size
        self.scale_step = 0
        self.canvas = canvas
        self.shape_list = []
        self.screen_center_world_pt = np.array([0.0,0.0])
        self.background = None
        self.app = app
        self.gridline = GridLines(self)

    @property
    def scale(self):
        return ZOOM_SCALE**self.scale_step

    # Scale = scale_step * ZOOM_SCALE
    def _set_scale_step(self,scale_step):
        self.scale_step = scale_step

    def draw_coupler(self,anchor_pt1):
        shape = Coupler(self,anchor_pt1)
        return shape

    # Add lines to world
    def draw_s_line(self,anchor_pt1,anchor_pt2):
        shape = StraightLine(self,anchor_pt1,anchor_pt2)
        return shape

    def draw_rectangle(self,anchor_pt1,anchor_pt2):
        shape = Rectangle(self,anchor_pt1,anchor_pt2)
        return shape

    def draw_oval(self,anchor_pt1,anchor_pt2):
        shape = Oval(self,anchor_pt1,anchor_pt2)
        return shape

    def draw_seg_line(self,anchor_pt1,anchor_pt2):
        shape = SegmentedLine(self,anchor_pt1,anchor_pt2)
        return shape     

    # Add CAD image file as background
    def add_background(self,filepath):
        self._reset_screen_world_center()
        self._reset_scale_step()
        if self.background == None:    
            self.background = Background(self)
        else:
            self.background.remove_from_canvas()
        self.background.add_background(filepath,'new')

    # set the world coordinate that the screen center showing
    def _set_screen_center_world(self,dev):
        self.screen_center_world_pt += dev/self.scale
        self.dev,self.total_dev = dev, dev/self.scale

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
        self.gridline.move(dev)
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
        dev = self.screen_dir_world(mouse_pt)
        # zoom in and out need different scale_step
        if zoom_in == 1: # if zoom in
            self.scale_step += zoom_in
            self.screen_center_world_pt += zoom_in*dev*(ZOOM_SCALE-1)/self.scale
        else:   
            self.screen_center_world_pt += zoom_in*dev*(ZOOM_SCALE-1)/self.scale
            self.scale_step += zoom_in        


############################################################
# Common GridShapes inherited by other shapes. 
# Get screen center from World_Grid and help shapes showcase.
class Grid_Shapes():
    def __init__(self,wg : WorldGrid,anchor =np.array([0,0]),tag=None):
        self.wg = wg
        self.tag = tag
        wg.shape_list.append(self)

    @property
    def screen_size(self):
        return self.wg.screen_size

    @property
    def canvas(self):
        return self.wg.canvas

    @property
    def screen_center_world_pt(self):
        return self.wg.screen_center_world_pt

    @property
    def scale(self):
        return ZOOM_SCALE**(self.wg.scale_step)

    @property
    def scale_step(self):
        return self.wg.scale_step

    def remove_from_canvas(self):
        self.canvas.delete(self.id)

    def hide_from_canvas(self): #hide object
        self.canvas.itemconfig(self.id, state='hidden')

    def show_on_canvas(self): #hide object
        self.canvas.itemconfigure(self.id, state='normal')

class GridLines(Grid_Shapes):
    def __init__(self, wg: WorldGrid, anchor=np.array([0, 0]), tag=None):
        super().__init__(wg, anchor, tag)
        self.x_lines,self.y_lines = [],[]
        self.dist = 50
        self.set_up_gridlines()
        self.wg.shape_list.remove(self)
        self.prev_center = np.array([0.0,0.0])
        

    def set_up_gridlines(self):
        width, height = self.screen_size.astype(int)
        for x in range(0,width,self.dist):
            line = self.canvas.create_line((x,0),(x,height),fill='#303645',width=0.5)
            self.x_lines.append(line)
        for y in range(0,height,self.dist):
            print(y)
            line = self.canvas.create_line((0,y),(width,y),fill='#303645',width=0.5)
            self.y_lines.append(line)

    def move(self,dev):
        x,y = 0,1
        for index,line in enumerate(self.x_lines):
            prev = self.canvas.coords(line)
            if dev[x] < 0:
                if prev[x]-dev[x] > self.screen_size[x]:
                    next_index = (index + 1) % len(self.x_lines)
                    next_line = self.canvas.coords(self.x_lines[next_index])
                    new_x = next_line[x]-50
                else:
                    new_x = prev[x]-dev[x]
            else:
                if prev[x]-dev[x] < 0:
                    prev_index = index - 1
                    prev_line = self.canvas.coords(self.x_lines[prev_index])
                    new_x = prev_line[x]+50
                else:
                    new_x = prev[x]-dev[x]
            new_x = int(new_x)               
            new = [new_x,0,new_x,self.screen_size[y]]
            self.canvas.coords(line,new)
            new_x = None

        for index,line in enumerate(self.y_lines):
            prev = self.canvas.coords(line)
            
            if dev[y] > 0:
                if prev[y]+dev[y] > self.screen_size[y]:
                    next_index = (index + 1) % len(self.y_lines)
                    next_line = self.canvas.coords(self.y_lines[next_index])
                    new_y = next_line[y]-50
                else:
                    new_y = prev[y]+dev[y]
            else:
                if prev[y]+dev[y] < 0:
                    prev_index = index - 1
                    prev_line = self.canvas.coords(self.y_lines[prev_index])
                    new_y = prev_line[y]+50
                else:
                    new_y = prev[y]+dev[y]
            new_y = int(new_y)               
            new = [0,new_y,self.screen_size[x],new_y]
            self.canvas.coords(line,new)
            new_y = None       



   
###########################################################
# Inherit GridShapes, responsible for image cropping, resizing and showing on canvas
# Background of the drawing, CAD image
class Background(Grid_Shapes):
    def __init__(self, wg: WorldGrid, anchor=np.array([0, 0]), tag=None):
        super().__init__(wg, anchor, tag)
        self.image_list = []
        self.image_staus = None

        # width/ height ratio for resizing
    @ property
    def ratio_aspect(self):
        if self.size == None:
            return None
        return self.size[1]/self.size[0]

    # Get coordinate of image of area that should be cropped
    def _get_coor_from_image_center(self,size,scale,curr_img_scale):
        img_center_world_pt = self._world_to_image(self.screen_center_world_pt,size,curr_img_scale)
        img_pt1 = img_center_world_pt - (self.screen_size/2)/scale
        img_pt2 = img_center_world_pt + (self.screen_size/2)/scale

        self._get_screen_anchor(img_pt1,img_pt2,size,scale)
        img_pt1,img_pt2 = self._get_boundaries(img_pt1,img_pt2,size)
        return (img_pt1[0],img_pt1[1],img_pt2[0],img_pt2[1])

    def _world_to_image(self,world,size,curr_img_scale):
        img_x = world[0]*curr_img_scale + size[0]/2
        img_y = -world[1]*curr_img_scale + size[1]/2
        return np.array([img_x,img_y])

    def _get_screen_anchor(self,img_pt1,img_pt2,size,scale):
        x,y,dev = 0,1,np.array([0,0])
        if img_pt1[x] < 0 and img_pt2[x] > size[0]:
            dev[x] = (size[0] - (img_pt2[x] + img_pt1[x]))
        elif img_pt2[x] > size[0]:
            dev[x] = (size[0] - img_pt2[x])
        elif img_pt1[x] < 0:
            dev[x] = (-img_pt1[x])

        if img_pt1[y] < 0 and img_pt2[y] > size[1]:
            dev[y] = (size[1] - (img_pt2[y] + img_pt1[y]))
        elif img_pt2[y] > size[1]:
            dev[y] = (size[1] - img_pt2[y])
        elif img_pt1[y] < 0:
            dev[y] = (-img_pt1[y])

        self._screen_anchor = dev/2*scale
        self._screen_anchor[1] *= -1

    def _get_boundaries(self,img_pt1,img_pt2,size):
        if img_pt1[0] < 0:
            img_pt1[0] = 0
        if img_pt1[1] < 0:
            img_pt1[1] = 0            
        if img_pt2[0] > size[0]:
            img_pt2[0] = size[0]  
        if img_pt2[1] > size[1]:
            img_pt2[1] = size[1]
        return img_pt1,img_pt2

    # resize image 
    def _resize_image(self,image,scale):
        size = (int(image.size[0]*scale), int(image.size[1]*scale))
        image = image.resize(size, pil.Image.ANTIALIAS)
        return image

    # Crop image with given coordinates
    def _crop_image(self,image,area_coordinate):
        cropped = image.crop(area_coordinate)
        return cropped

    # Open image from a given folder directory
    def _create_image(self,filepath):
        image = pil.Image.open(filepath)
        return image

    def create_img_list(self,filepath):
        image_list = {}
        for i in range(0,-50,-5):
            scale = ZOOM_SCALE**i
            image = self._add_new_image(filepath)
            size = (int(image.size[0]*scale), int(image.size[1]*scale))
            image = image.resize(size, pil.Image.ANTIALIAS)
            image_list[i] = image
        return image_list

    def _select_image(self):
        for key, image in self.image_list.items():
            if self.scale_step <= 0:
                if key-self.scale_step in range(0,5):
                    self.scale_step_diff = self.scale_step-key
                    return image, ZOOM_SCALE**(self.scale_step-key), ZOOM_SCALE**key                
            else:
                self.scale_step_diff = self.scale_step
                return self.image_list[0], ZOOM_SCALE**(self.scale_step), ZOOM_SCALE**key
                    
    # update background when panning, zooming or adding new background
    def add_background(self,filepath,type=""):
        self.filepath = filepath
        if type == 'new': 
            self.image_list = self.create_img_list(filepath)
        image,scale,curr_img_scale = self._select_image()
        image = self._crop_and_resize_image(image,scale,curr_img_scale)
        self._to_canvas(image,type)
        return self

    # Add background image
    def _add_new_image(self,filepath):
        image = self._create_image(filepath)
        self.size = np.array([image.width,image.height])
        self._primitive_image = image
        return image

    # grouped crop and resize as it is used in panning
    def _crop_and_resize_image(self,image,scale,curr_img_scale):
        try:
            cropped_img = self._crop_image(image,self._get_coor_from_image_center(image.size,scale,curr_img_scale))
            resized_image = self._resize_image(cropped_img,scale)
            return resized_image
        except:
            return None

    # Turn the image to TkImage object and place it on canvas
    def _to_canvas(self,image,type):
        if image == None: # No image given, may caused by error
            self.hide_from_canvas()
            self.image_staus = 'hide'
        else: # Have image, put image on canvas
            tk_image = pil.ImageTk.PhotoImage(image,master=self.wg.app)
            self._tk_temp_img = tk_image
            coor = self.wg.world_dir_screen(self._screen_anchor).tolist()
            if type == "pan":
                self.canvas.coords(self.id,coor)
                self.canvas.itemconfig(self.id,image=tk_image)
                if self.image_staus == 'hide' and image != None:
                    self.show_on_canvas() #if image hide, show on canvas
                    self.image_staus == 'show'

            else:
                self.id = self.canvas.create_image(coor,anchor=CENTER,image=tk_image,tag=self.tag)

    # pan move of 
    def move(self):
        self.add_background(self.filepath,'pan')

    def zoom(self):
        self.add_background(self.filepath,'pan')

class TwoPointObject(Grid_Shapes):
    def __init__(self, world_grid: WorldGrid,screen_pt1,screen_pt2,fill='black',width=3):
        super().__init__(world_grid)
        self._create(screen_pt1,screen_pt2,fill,width)
        self._set_attribute(screen_pt1,screen_pt2)

    def _set_attribute(self,pt_1,pt_2):
        self.world_anchor_1 = self.wg.screen_to_world(pt_1)
        self.world_anchor_2 = self.wg.screen_to_world(pt_2)
        self.pt_1,self.pt_2= pt_1,pt_2
         
    def move(self):
        self._update_screen_anchors()
        self.change_coor(self.pt_1,self.pt_2)

    def change_coor(self,pt_1,pt_2):
        self.canvas.coords(self.id,pt_1[0],pt_1[1],pt_2[0],pt_2[1])
        # self._set_attribute(pt_1,pt_2)

    def zoom(self):
        self.move()
 
    def _update_screen_anchors(self):
        self.pt_1 = self.wg.world_to_screen(self.world_anchor_1)
        self.pt_2 = self.wg.world_to_screen(self.world_anchor_2)

class StraightLine(TwoPointObject):
    def __init__(self, world_grid: WorldGrid, pt_1, pt_2, fill='black',width=2):
        super().__init__(world_grid, pt_1, pt_2, fill, width)

    def _create(self,screen_pt1,screen_pt2,fill,width):
        self.id = self.canvas.create_line(screen_pt1.tolist(),screen_pt2.tolist(), fill= fill, width=width,tag=self.tag)

class Rectangle(TwoPointObject):
    def __init__(self, world_grid: WorldGrid, pt_1, pt_2, fill=None, width=2):
        super().__init__(world_grid, pt_1, pt_2, fill, width)
        
    def _create(self,pt_1, pt_2,fill,width):
        self.id = self.canvas.create_rectangle(pt_1.tolist(),pt_2.tolist(), fill= fill, width=width,tag= self.tag)

class Oval(TwoPointObject):
    def __init__(self, world_grid: WorldGrid, pt_1, pt_2, fill=None, width=2):
        super().__init__(world_grid, pt_1, pt_2, fill, width)
        
    def _create(self,pt_1, pt_2,fill,width):
        pt_1, pt_2 =self._convert_coor(pt_1,pt_2)
        self.id = self.canvas.create_oval(pt_1.tolist(),pt_2.tolist(), fill= fill, width=width,tag= self.tag)

    # convert from two corner points to center and circumference point.
    def _convert_coor(self,pt_1,pt_2):
        s = (pt_1-pt_2)**2
        r = np.sqrt(s[0]+s[1])
        new_pt_1 = pt_1 - r
        new_pt_2 = pt_1 + r
        return new_pt_1, new_pt_2

    def change_coor(self,pt_1,pt_2):
        pt_1, pt_2=self._convert_coor(pt_1,pt_2)
        return super().change_coor(pt_1,pt_2)

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
    def __init__(self, world_grid: WorldGrid, anchor_1=np.array([0,0]),anchor_2=np.array([0,0])):
        super().__init__(world_grid, anchor_1)
        self.wg.shape_list.remove(self)
        self.line_list = []
        self.prev_world_pt = None
        self.add_line(anchor_1,anchor_2)

    @property
    def prev_screen_pt(self):
        if np.any(self.prev_world_pt) != None:
            pt = self.wg.world_to_screen(self.prev_world_pt)
            return pt
        else:
            return None

    def add_line(self,*args):
        if np.any(self.prev_screen_pt) != None:
            pt_1,pt_2 = self.prev_screen_pt,args[1]
        else:
            pt_1,pt_2 = args[0],args[1]
        line = self._create(pt_1,pt_2)
        self.prev_world_pt = self.wg.screen_to_world(args[1])
        self.line_list.append(line)
        return line

    def change_coor(self,pt1,pt2):
        self.line_list[-1].change_coor(pt1,pt2)
        self.line_list[-1]._set_attribute(pt1,pt2)
            
    def _create(self,prev_pt,next_pt):
        line = StraightLine(self.wg,prev_pt,next_pt)
        return line

    def remove_end_line(self):
        if len(self.line_list) > 2:
            self.wg.delete_shape(self.line_list[-1])
    
    @property
    def world_anchor_1(self):
        if len(self.line_list) >= 2:
            return self.line_list[-2].world_anchor_2
        else:
            return self.line_list[0].world_anchor_1

if __name__ == "__main__":
    pass
