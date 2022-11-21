from tkinter import ttk
from ttkthemes import ThemedStyle

class ToolBoxTab():
    def __init__(self,app,width,height,row,column,sticky,rowspan=1,columnspan =1):
        my_notebook = ttk.Notebook(app)
        my_notebook.grid(padx=5,pady=4,rowspan=rowspan,columnspan=columnspan)

        my_frame1 = ttk.Frame(my_notebook, width=width, height=height)
        my_frame2 = ttk.Frame(my_notebook, width=width, height=height)
        my_frame3 = ttk.Frame(my_notebook, width=width, height=height)

        my_frame1.grid(row=row,column=column,sticky=sticky)
        my_frame2.grid(row=row,column=column,sticky=sticky)
        my_frame3.grid(row=row,column=column,sticky=sticky)

        my_notebook.add(my_frame1,text='Home')
        my_notebook.add(my_frame2,text='Insert')
        my_notebook.add(my_frame3,text='Annotate')

        f1_button = ttk.Button(my_frame1,text= 'hihi',command=lambda:canvas.draw_shape.change_draw_label())
        f1_button.grid(row=0,column=0,sticky=W)


class frame_home(ttk.Frame):
    def

if __name__ == "__main__":
    pass 