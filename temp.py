import tkinter
from tkinter import *

#Creates widgets for user input
class Imagespecs(Frame):

    def __init__(self,master):
        Frame.__init__(self,master)
        self.grid()
        self.y_axis()
        self.x_axis()

#Y axis input
        def y_axis(self):
            self.instruction = Label(self,text = "How many pixels high do you want the image?")
            self.instruction.grid(row = 8, column = 0, columnspan = 2, sticky = N)

        self.height = Entry(self)
        self.height.grid(row = 10, column = 1, sticky = E)

#Enters info to run fractal generation
        self.submit_button = Button(self,text = "Submit", command = self.fractals)
        self.submit_button.grid(row = 14, column = 2, sticky = E)

#X axis input
        def x_axis(self):
            self.instruction2 = Label(self,text = "How many pixels wide do you want the image?")
            self.instruction2.grid(row = 4, column = 0, columnspan = 2, sticky = E)

        self.width = Entry(self)
        self.width.grid(row = 6, column = 1, sticky = E)

    #generates fractal
        def fractals(self):
            #Replace non-input
            content = self.width.get()
            content2 = self.height.get()

            if content == "":
                content = 500

            if content2 == "":
                content2 = 500

        #Create window specs
        WIDTH = int(content2); HEIGHT = int(content)
        xa = -2.0; xb = 1.0
        ya = -1.5; yb = 1.5
        maxIt = 256

        window = Tk()
        canvas = Canvas(window, width = WIDTH, height = HEIGHT, bg = "#000000")
        img = PhotoImage(width = WIDTH, height = HEIGHT)

            #The Newton-Raphson iteration
        h = HEIGHT
        for ky in range(HEIGHT):
            print (h)
            h = h - 1
            for kx in range(WIDTH):
                c = complex(xa + (xb - xa) * kx / WIDTH, ya + (yb - ya) * ky / HEIGHT)
                z = complex(0.0, 0.0)
                for i in range(maxIt):
                    z = z * z + c
                if abs(z) >= 2.0:
                    break
                rd = hex(i % 4 * 64)[2:].zfill(2)
                gr = hex(i % 8 * 32)[2:].zfill(2)
                bl = hex(i % 16 * 16)[2:].zfill(2)
                img.put("#" + rd + gr + bl, (kx, ky))

            canvas.create_image((0, 0), image = img, state = "normal", anchor = tkinter.NW)

            #Run GUI
            canvas.pack()
            mainloop()

    root = Tk()
    root.title("Fractal GUI")
    root.geometry("300x200")
    app = Imagespecs(root)

    root.mainloop()