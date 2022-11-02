import PIL as pil
from tkinter import *

class WorldGrid():
    def __init__(self,screen_width,screen_height,ratio,canvas):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale = 0
        self.canvas = canvas
        self.shape_list = []
        self.bkgd = 0

    def _set_scale(self,scale):
        self.scale = scale

    def add_background(self,filepath):
        try:
            self.background.remove_background()
            self.background.add_background(filepath)
        except:
            self.background = Background(self.canvas,self.screen_width,self.screen_height,self.scale)
            self.shape_list.append(self.background)
            self.background.add_background(filepath)


    def pan_move(self,x_displacement,y_displacement):
        pass

    def to_screen(self):
        pass

    ############################################################

class Grid_Shapes():
    def __init__(self,canvas,screen_width,screen_height,ratio):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.canvas = canvas
        self.ratio = ratio
        self.width, self.height = 0,0

    def delete(self):
        self.canvas.delete(self.bkgd)

    def screen_to_world(self,screen_x,screen_y,scale):
        world_x = (screen_x - self.screen_width/2)*(1.1**scale)
        world_y = -(screen_y - self.screen_height/2)*(1.1**scale)
        return world_x, world_y
    def world_to_screen(self,world_x,world_y,scale):
        screen_x = world_x*(1.1**scale) + self.screen_width/2
        screen_y = -world_y*(1.1**scale) + self.screen_height/2
        return screen_x, screen_y
    def screen_to_world_area(self,center_screen_x,center_screen_y,scale):
        world_x1 = (center_screen_x - self.screen_width/2)*(1.1**scale)
        world_y1 = (center_screen_y - self.screen_height/2)*(1.1**scale)
        world_x2 = (center_screen_x + self.screen_width/2)*(1.1**scale)
        world_y2 = (center_screen_y + self.screen_height/2)*(1.1**scale)
        return (world_x1,world_y1,world_x2,world_y2)

    def screen_to_Image_area(self,image_center_x,image_center_y,scale):
        world_x1 = int((image_center_x - self.screen_width/2)*(1.1**scale))
        world_y1 = int((image_center_y - self.screen_height/2)*(1.1**scale))
        world_x2 = int((image_center_x + self.screen_width/2)*(1.1**scale))
        world_y2 = int((image_center_y + self.screen_height/2)*(1.1**scale))
        return int(world_x1,world_y1,world_x2,world_y2)

class Background(Grid_Shapes):
    def _resize_image(self,image,scale):
        width, height = int(image.width*1.1**scale),int(image.height*1.1**scale)
        size = (width, height)
        image.resize(size, pil.Image.BOX)
        return image

    @staticmethod
    def _get_ratio_aspect(width,height):
        return height/width

    def _crop_image(self,image,area_coordinate):
        cropped = image.crop(area_coordinate)
        return cropped

    def _create_image(self,filepath):
        image = pil.Image.open(filepath)
        return image

    def image_transform(self,image,step,scale,deviation):
        pass

    def remove_background(self):
        self.canvas.delete(self.bkgd)

    def add_background(self,filepath):
        image = self._add_image(filepath)
        self._to_canvas(image,0,0)

    def _add_image(self,filepath):
        print(filepath)
        image = self._create_image(filepath)
        self.width, self.height = image.width,image.height
        self.ratio_aspect = self._get_ratio_aspect(image.width,image.height)
        x,y = self._get_image_center()
        cropped_img = self._crop_image(image,self.screen_to_world_area(x,y,0))
        resized_image = self._resize_image(cropped_img,0)

        return resized_image

    def _to_canvas(self,image,x,y):
        tk_image = pil.ImageTk.PhotoImage(image)
        self.tk_temp_img = tk_image
        print(self.world_to_screen(0,0,0))
        self.bkgd = self.canvas.create_image(self.world_to_screen(0,0,0),anchor=CENTER,image=tk_image)
        

    def _get_image_center(self):
        x,y = self.width/2,self.height/2
        return x,y


if __name__ == "__main__":
    pass
