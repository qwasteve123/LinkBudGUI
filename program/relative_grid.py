import PIL as pil
from tkinter import *
import numpy as np
import math
from canvas import HexColor

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
        self.selection_list = []
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
        return self.world_dir_screen(world).astype(int)

    def delete_shape(self,shape):
        shape.remove_from_canvas()
        self.shape_list.remove(shape)

    # pan move all shapes i.e. background, lines and others
    def pan_move(self,dev):
        self._set_screen_center_world(dev)
        self.gridline.move()
        for shape in self.shape_list:
            shape.move()

    # zoom all shapes
    def zoom(self,mouse_pt,zoom_in):
        self._zoom_deviation(mouse_pt,zoom_in)
        self.gridline.zoom()
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

    def remove_selection(self,*shape_ids):
        if shape_ids == None:
            return
        else:
            for shape_id in shape_ids:
                self.selection_list.remove(shape_id)



    def add_selection(self,*shape_ids):
        for shape_id in shape_ids:
            if shape_id not in self.selection_list:
                color = self.find_colour(shape_id)
                selection_color = self.get_selection_color(color)
                self.change_colour(shape_id,selection_color)
                self.selection_list.append(shape_id)
            else:
                self.remove_selection(shape_id)

    def get_selection_color(self,color1): 
        r1,g1,b1 = self.hex_to_rgb(color1)
        r2,g2,b2 = self.hex_to_rgb(HexColor.SELECTION)
        nr = int(r1+ float(r2-r1) * 0.8)
        ng = int(g1+ float(g2-g1) * 0.8)
        nb = int(b1+ float(b2-b1) * 0.8)
        new_color = "#%x%x%x" % (nr,ng,nb)
        return new_color


    def hex_to_rgb(self,hex):
        hex = hex.lstrip('#')
        lv = len(hex)
        return tuple(int(hex[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))      

    def find_colour(self,shape_id):
        type = self.canvas.type(shape_id)
        if type in ['line','arc']:
            color = self.canvas.itemcget(shape_id,'fill')
        elif type in ['rectangle','oval']:
            color = self.canvas.itemcget(shape_id,'outline')  
        else:
            return None          
        return color

    def change_colour(self,shape_id,color):
        type = self.canvas.type(shape_id)
        if type in ['line','arc']:
            self.canvas.itemconfig(shape_id,fill=color)
        elif type in ['rectangle','oval']:
            self.canvas.itemconfig(shape_id,outline=color)  


############################################################
# Common GridShapes inherited by other shapes. 
# Get screen center from World_Grid and help shapes showcase.
class Grid_Shape():
    def __init__(self,wg : WorldGrid,anchor =np.array([0,0]),tag=None):
        self.wg = wg
        self.tag = tag
        wg.shape_list.append(self)

    @property
    def coor(self):
        return self.canvas.coords(self.id)

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

    def itemconfig(self,**kwargs):
        self.canvas.itemconfig(self.id,kwargs)

    # def select_items(self,*args):
    #     for shape_id in args:
    #         self.canvas.itemconfig(shape_id,fill='white')

class GridLines(Grid_Shape):
    def __init__(self, wg: WorldGrid, anchor=np.array([0, 0]), tag=None):
        super().__init__(wg, anchor, tag)
        self.x_lines,self.y_lines = [],[]
        self.dist, self.prev_dist = 20,20
        self.dist_list = [1,2,4]
        self.grid_scale_step = 4
        self.set_up_gridlines()
        self.wg.shape_list.remove(self)
        self.prev_center = np.array([0.0,0.0])
        
    def set_up_gridlines(self):
        x,y = 0,1
        screen_pt1 = self.wg.screen_to_world(np.array([0,0])).astype(float)
        screen_pt2 = self.wg.screen_to_world(self.screen_size).astype(float)
        x_rng1, x_rng2 = int(screen_pt1[x]//self.dist-1),int((screen_pt2[x]//self.dist)+100)
        for x_step in range(x_rng1, x_rng2):
            x_coor = x_step*self.dist
            pt1,pt2 = np.array([x_coor,screen_pt1[y]]),np.array([x_coor,screen_pt2[y]])
            line = self._draw_grid_lines(x_coor,pt1,pt2)
            line.wg.shape_list.remove(line)
            self.x_lines.append(line)

        y_rng1, y_rng2 = int((screen_pt2[y]//self.dist)-1),int((screen_pt1[y]//self.dist)+100)
        for y_step in range(y_rng1, y_rng2):
            y_coor = y_step*self.dist
            pt1,pt2 = np.array([screen_pt1[x],y_coor]),np.array([screen_pt2[x],y_coor])
            line = self._draw_grid_lines(y_coor,pt1,pt2)
            line.wg.shape_list.remove(line)
            self.y_lines.append(line)

    def _draw_grid_lines(self,coor,pt1,pt2):
        pt1,pt2 = self.wg.world_to_screen(pt1), self.wg.world_to_screen(pt2)
        line_width = self.is_thick_line(coor,self.dist)
        line = StraightLine(self.wg,pt1,pt2,fill='#303645',width=line_width,tag=('gridlines'))
        return line

    def move(self):
        x,y = 0,1
        screen_pt1 = self.wg.screen_to_world(np.array([0,0])).astype(float)
        screen_pt2 = self.wg.screen_to_world(self.screen_size).astype(float)
        x_count = int(screen_pt1[x]//self.dist-1)
        y_count = int(screen_pt2[y]//self.dist-1)        
        for index, line in enumerate(self.x_lines):
            x_step = x_count+index
            x_coor = round(x_step*self.dist,2)
            pt1,pt2 = np.array([x_coor,screen_pt1[y]]),np.array([x_coor,screen_pt2[y]])
            self._change_grid_lines(line,x_coor,pt1,pt2)
            
        for index, line in enumerate(self.y_lines):
            y_step = y_count+index
            y_coor = round(y_step*self.dist,2)
            pt1,pt2 = np.array([screen_pt1[x],y_coor]),np.array([screen_pt2[x],y_coor])
            self._change_grid_lines(line,y_coor,pt1,pt2)

    def _change_grid_lines(self,line,coor,pt1,pt2):
        pt1,pt2 = self.wg.world_to_screen(pt1), self.wg.world_to_screen(pt2)
        line_width = self.is_thick_line(coor,self.dist)
        line.change_coor(pt1,pt2)
        line.itemconfig(width=line_width)

    def zoom(self):
        
        if self.dist*self.scale > 1.8*self.prev_dist:
            self.grid_scale_step -=1
            self.dist = self.dist_list[self.grid_scale_step%3]*10**(self.grid_scale_step//3)
            self.prev_dist = self.dist*self.scale
        elif 1.8*self.dist*self.scale < self.prev_dist:
            self.grid_scale_step +=1
            self.dist = self.dist_list[self.grid_scale_step%3]*10**(self.grid_scale_step//3)
            self.prev_dist = self.dist*self.scale
        print(self.dist)
        self.move()

    def is_thick_line(self,coor,dist):
        log_num = math.log10(dist)
        if log_num < 0:
            power = -(log_num//10)
            coor *= 10**power
            dist *= 10**power
        if coor % (5*dist) == 0:
            return 3
        else:
            return 0.5
###########################################################
# Inherit GridShapes, responsible for image cropping, resizing and showing on canvas
# Background of the drawing, CAD image
class Background(Grid_Shape):
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

class TwoPointObject(Grid_Shape):
    def __init__(self, world_grid: WorldGrid,screen_pt1,screen_pt2,**kwarg):
        super().__init__(world_grid)
        self._create(screen_pt1,screen_pt2,**kwarg)
        self._set_attribute(screen_pt1,screen_pt2)

    @property
    def coor(self):
        coor = self.canvas.coords(self.id)
        return np.array([coor[0],coor[1]]),np.array([coor[2],coor[3]])

    def _set_attribute(self,pt_1,pt_2):
        self.world_anchor_1 = self.wg.screen_to_world(pt_1)
        self.world_anchor_2 = self.wg.screen_to_world(pt_2)
        self.pt_1,self.pt_2= pt_1,pt_2
         
    def move(self):
        self._update_screen_anchors()
        self.change_coor(self.pt_1,self.pt_2)

    def change_coor(self,pt_1,pt_2):
        self.canvas.coords(self.id,pt_1[0],pt_1[1],pt_2[0],pt_2[1])

    def zoom(self):
        self.move()
 
    def _update_screen_anchors(self):
        self.pt_1 = self.wg.world_to_screen(self.world_anchor_1)
        self.pt_2 = self.wg.world_to_screen(self.world_anchor_2)

class StraightLine(TwoPointObject):
    def __init__(self, world_grid: WorldGrid, pt_1, pt_2,fill='#FF0000', width=2,**kwargs):
        super().__init__(world_grid, pt_1, pt_2,fill=fill, width=width,**kwargs)

    def _create(self,screen_pt1,screen_pt2,**kwargs):
        self.id = self.canvas.create_line(screen_pt1.tolist(),screen_pt2.tolist(), kwargs)

class Rectangle(TwoPointObject):
    def __init__(self, world_grid: WorldGrid, pt_1, pt_2, fill=None, width=2,outline='#FFFFFF',**kwargs):
        super().__init__(world_grid, pt_1, pt_2,fill=fill, width=width,outline=outline,**kwargs)
        
    def _create(self,pt_1, pt_2,**kwargs):
        self.id = self.canvas.create_rectangle(pt_1.tolist(),pt_2.tolist(), kwargs)

class Oval(TwoPointObject):
    def __init__(self, world_grid: WorldGrid, pt_1, pt_2, fill=None, width=2,outline='#000000',**kwargs):
        super().__init__(world_grid, pt_1, pt_2,fill=fill, width=width,outline=outline,**kwargs)
        
    def _create(self,pt_1, pt_2,**kwargs):
        pt_1, pt_2 =self._convert_coor(pt_1,pt_2)
        self.id = self.canvas.create_oval(pt_1.tolist(),pt_2.tolist(),kwargs)

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

class Coupler(Grid_Shape):
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

class SegmentedLine(Grid_Shape):
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
