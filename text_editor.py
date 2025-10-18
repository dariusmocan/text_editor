import tkinter as tk
from tkinter import filedialog, colorchooser, ttk, messagebox
from tkinter import *
import numpy as np



class TextEditor():
    def __init__(self, root):
        self.root = root
        self.root.title('Labeled Text Editor')
        
        # window size
        window_width = 300
        window_height = 200

        # centering window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # setting sizes
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')
        self.tabs = {}
        self.tab_counter = 1

        # storing paths for saving
        self.file_paths = {}

        # storing changes for not exiting and losing progress
        self.changed = {}

        self.create_tab('Untitled')

        # the menu of the file in which other menus are created
        self.menu = tk.Menu(root)
        self.root.config(menu = self.menu)

        # the file menu of the file
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=file_menu)
        # save existing file
        file_menu.add_command(label='Save', command=self.save_file)
        file_menu.add_separator()
        # save new file
        file_menu.add_command(label='Save As', command=self.save_as_file)
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
        file_menu.add_command(label='Exit', command=self.on_exit)

        self.root.bind("<Control-o>", lambda event: self.load_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_as_file())
        self.root.bind("<Control-n>", lambda event: self.new_tab())
        self.root.bind("<Control-w>", lambda event: self.close_tab())
        

        # exit protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

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

        # initiating the changes, tabs and paths
        self.tabs[frame] = text
        self.file_paths[frame] = None
        self.changed[frame] = False

         # detect text changes
        text.bind("<<Modified>>", self.on_text_modified)
        text.bind("<Control-Right>", lambda event: self.move_end_word(event))

        self.notebook.select(frame)
        return text
        
    def get_current_text(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        return self.tabs[current_tab]
    
    # overwritting and saving an existing file
    def save_file(self, event = None):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        current_text = self.get_current_text()
        content = current_text.get(1.0, tk.END)
        path = self.file_paths.get(current_tab)

        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            frm = self.notebook.nametowidget(self.notebook.select())
            self.changed[frm] = False
            label = self.notebook.tab(frm, "text").rstrip("*")
            self.notebook.tab(frm, text = label)
        else:
            self.save_as_file()
    
    # saving a new file
    def save_as_file(self, event = None):
        text = self.get_current_text()
        current_tab = self.notebook.nametowidget(self.notebook.select())
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes= [('Text File', '*.txt'), ('All files', '*.*')]
        )
        if path:
            content = text.get(1.0, tk.END)
            with open(file=path,mode="w", encoding="utf-8") as f:
                f.write(content)

            self.changed[current_tab] = False
            label = self.notebook.tab(current_tab, "text").rstrip("*")
            self.notebook.tab(current_tab, text = label)

            # adding path
            self.file_paths[current_tab] = path

            # update the title
            self.notebook.tab(current_tab, text=path.split("/")[-1])

    # opening an existing file
    def load_file(self, event = None):
        text = self.get_current_text()
        path = filedialog.askopenfilename(
            defaultextension='.txt',
            filetypes=[('text files' , '*.txt'), ('All files', '*.*')]
        )
        if path:
            current_tab = self.notebook.nametowidget(self.notebook.select())
            self.file_paths[current_tab] = path
            with open(path, 'r', encoding='utf-8') as f:
                content =  f.read()
            text.delete(1.0,tk.END)
            text.insert(1.0, content)

            # adding the title
            self.notebook.tab(current_tab, text = path.split('/')[-1])

    def new_tab(self, event=None):
        self.tab_counter += 1
        self.create_tab(f"Untitled {self.tab_counter}")

    def close_tab(self, event = None):
        current_frame = self.notebook.nametowidget(self.notebook.select())
        self.notebook.forget(current_frame)
        current_frame.destroy()

    # adds the title the asterix: * if it was changed
    def on_text_modified(self, event):
        if not self.root.winfo_exists(): 
            return
    
        text = self.get_current_text()
        frm = text.master
        # return True if was modified
        if text.edit_modified():
            self.changed[frm] = True

            # gets the title and checks for adding the asterix
            current_label = self.notebook.tab(frm, "text")
            if not current_label.endswith("*"):
                self.notebook.tab(frm, text = current_label + '*')

            # not anymore modified after changing title
            text.edit_modified(False)


    def on_exit(self, event = None):
        unsaved = [change for frame, change in self.changed.items() if change]

        if unsaved:
            answer = messagebox.askyesnocancel (
                "Unsaved Changes",
                "Do you wish to save the changes?"
            )

            if answer:
                self.save_file()
                self.root.destroy()
            elif answer == False:
                self.root.destroy()
            else:
                return
        else:
            self.root.destroy()

    def move_end_word(self, event):
        text = event.widget
        current = text.index("insert")
        end_current = text.index("insert wordend")

        # if our cursor is on a space we jump at the end of the next word, otherwise the cursor jumps 
        # at the end of the current word
        char = text.get(current)
        if char.isspace():
            text.mark_set("insert", "insert +1c wordend")
        else:
            text.mark_set("insert", end_current)

        return "break"


root = tk.Tk()
editor = TextEditor(root)

root.mainloop()

