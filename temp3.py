# Import the required libraries
from tkinter import *

# Create an instance of tkinter frame or window
win = Tk()

# Set the size of the window
win.geometry("700x350")

# Create a canvas widget
canvas = Canvas(win,bg='grey')
canvas.pack(fill=BOTH)

def on_button_pressed(event):
   start_x = canvas.canvasx(event.x)
   start_y = canvas.canvasy(event.y)
   print("start_x, start_y =", start_x, start_y)

def on_button_motion(event):
   end_x = canvas.canvasx(event.x,100)
   end_y = canvas.canvasy(event.y,100)
   print("end_x, end_y=", end_x, end_y, event.x, event.y)

def scale(event):
    zoom_in = 0
    if event.delta == -120:
            zoom_in = -1
    if event.delta == 120:
            zoom_in = 1
    canvas.scale("all", event.x, event.y, 1.1**zoom_in, 1.1**zoom_in)

# Bind the canvas with Mouse buttons
canvas.bind("<MouseWheel>", scale)
canvas.bind("<Button1-Motion>", on_button_motion)
canvas.create_line(50,50,80,90)

# Add a Label widget in the window
Label(win, text="Move the Mouse Pointer and click " "anywhere on the Canvas").pack()

win.mainloop()