import tkinter as tk
from tkinter import filedialog, colorchooser, ttk
from tkinter import *
import numpy as np



class TextEditor():
    def __init__(self, root):
        self.root = root
        self.root.title('Labeled Text Editor')
        self.root.geometry('300x200')

        # notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')
        self.tabs = {}
        self.tab_counter = 1
        self.create_tab('Untitled')

        # the menu of the file in which other menus are created
        self.menu = tk.Menu(root)
        self.root.config(menu = self.menu)

        # the file menu of the file
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=file_menu)
        # save option
        file_menu.add_command(label='Save', command=self.save_file)
        file_menu.add_separator()
        # load option
        file_menu.add_command(label = 'Open File', command=self.load_file)
        file_menu.add_separator()
        # open new tab
        file_menu.add_command(label='New tab', command=self.new_tab)
        file_menu.add_separator()
        # close tab
        file_menu.add_command(label='Close Tab', command= self.close_tab)
        file_menu.add_separator()
        # exitting
        file_menu.add_command(label='Exit', command=root.destroy)

        self.root.bind("<Control-o>", lambda event: self.load_file())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_file())
        self.root.bind("<Control-n>", lambda event: self.new_tab())
        self.root.bind("<Control-w>", lambda event: self.close_tab())

    def create_tab(self, title):
        # frame of scrollbar and text area
        frame = ttk.Frame(self.notebook, padding=10)
        frame.pack(expand=True, fill='both')

        #add the frame
        self.notebook.add(frame, text = title)

        # scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')

        # text area
        text = tk.Text(frame, wrap='word', yscrollcommand=scrollbar.set)
        text.pack(expand=True, fill='both')
        scrollbar.config(command=text.yview)

        self.tabs[frame] = text
        self.notebook.select(frame)
        return text
        
    def get_current_text(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        return self.tabs[current_tab]
    
    # saving a file
    def save_file(self, event = None):
        text = self.get_current_text()
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes= [('Text File', '*.txt'), ('All files', '*.*')]
        )
        if path:
            content = text.get(1.0, tk.END)
            with open(file=path,mode="w", encoding="utf-8") as f:
                f.write(content)

    # opening an existing file
    def load_file(self, event = None):
        text = self.get_current_text()
        path = filedialog.askopenfilename(
            defaultextension='.txt',
            filetypes=[('text files' , '*.txt'), ('All files', '*.*')]
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                content =  f.read()
            text.delete(1.0,tk.END)
            text.insert(1.0, content)

    def new_tab(self, event=None):
        self.tab_counter += 1
        self.create_tab(f"Untitled {self.tab_counter}")

    def close_tab(self, event = None):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        self.notebook.forget(current_frame)
        current_frame.destroy()

root = tk.Tk()
editor = TextEditor(root)

root.mainloop()

