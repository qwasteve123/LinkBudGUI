```mermaid
classDiagram
  direction LR

   MainWindowTk -- WindowCanvas
   MainWindowTk -- MenuBar
   WindowCanvas <|-- WorldGrid

  class MainWindowTk{
  }



  class WindowCanvas{
      +width
      +height
      +bkgd_color
      +MAX_ZOOM
      +MIN_ZOOM
      +scale_step
      +ZOOM_SCALE
      +initialdir
      +is_hover
      +canvas
      +world_grid

      +add_background()
      -_hover_motion()
      -_hover_leave()
      -_change_label()
      -_mouse_wheel()
      -_pan_release()
      -_pan_move()
    }
    class WorldGrid{

    }
    class MenuBar{
      +Open()
      +Delete()
      +Exit()
    }


```
