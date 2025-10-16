import tkinter as tk
from tkinter import filedialog, colorchooser, ttk
from tkinter import *
import numpy as np

# saving a file
def save_file():
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes= [('Text File', '*.txt'), ('All files', '*.*')]
    )
    if path:
        content = text.get(1.0, tk.END)
        with open(file=path,mode="w", encoding="utf-8") as f:
            f.write(content)

# opening an existing file
def load_file():
    path = filedialog.askopenfilename(
        defaultextension='.txt',
        filetypes=[('text files' , '*.txt'), ('All files', '*.*')]
    )
    if path:
        with open(path, 'r', encoding='utf-8') as f:
            content =  f.read()
        text.delete(1.0,tk.END)
        text.insert(1.0, content)

# window, title, dimension, and events
root = tk.Tk()
root.title("My Text Editor")
root.geometry('300x200')

root.bind("<Control-o>", lambda event: load_file())
root.bind("<Control-Shift-S>", lambda event: save_file())


# the menu of the file in which other menus are created
menu = tk.Menu(root)
root.config(menu = menu)

# the file menu of the file
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='File', menu=file_menu)
# save option
file_menu.add_command(label='Save', command=save_file)
file_menu.add_separator()
# load option
file_menu.add_command(label = 'Open File', command=load_file)
file_menu.add_separator()
# exitting
file_menu.add_command(label='Exit', command=root.destroy)

# frame of scrollbar and text area
frame = ttk.Frame(root, padding=10)
frame.pack(expand=True, fill='both')

# scrollbar
scrollbar = ttk.Scrollbar(frame)
scrollbar.pack(side='right', fill='y')

# text area
text = tk.Text(frame, wrap='word', yscrollcommand=scrollbar.set)
text.pack(expand=True, fill='both')
scrollbar.config(command=text.yview)

root.mainloop()

