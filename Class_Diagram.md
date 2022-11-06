:::mermaid
classDiagram
  direction LR

   WorldGrid <|-- Grid_Shapes
   Grid_Shapes <|-- Background

  class WorldGrid{
      +screen_width
      +screen_height
      +scale_step
      +canvas
      +shape_list
      +screen_center_world_x
      +screen_center_world_y

      +add_background()
      +screen_to_world()
      +world_to_screen()
      +pan_move()
      +zoom()
      +zoom_deviation()

      -_set_scale_step()
      -_set_screen_center_world()
      -_reset_screen_world_center()
      -_reset_scale_step()
      -_get_world_center()
  }

   class Grid_Shapes{
      +width
      +height
      +world_anchor_x
      +world_anchor_y

      -_screen_width
      -_screen_height
      -_canvas
      -_scale_step
      -_screen_center_world_x
      -_screen_center_world_y
      -_screen_anchor_x
      -_screen_anchor_y



      +delete()

      -_world_to_image()
      -_update_screen_center_world()
      -_update_scale_step()
      -_get_coor_from_image_center()
      -_get_screen_anchor()
      -_get_boundaries()
    }
    class Background{
      -_tk_temp_img
      -_primitive_image

      +add_background()
      +move()
      +zoom()

      -_get_ratio_aspect()
      -_resize_image()
      -_crop_image()
      -_create_image()
      -_add_new_image()
      -_crop_and_resize_image()
      -_to_canvas()
    }

:::
