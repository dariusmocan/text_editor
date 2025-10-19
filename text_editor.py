import tkinter as tk
from tkinter import filedialog, colorchooser, ttk, messagebox
from tkinter import *
import numpy as np



class TextEditor():
    def __init__(self, root):
        self.root = root
        self.root.title('Labeled Text Editor')
        
        # window size
        window_width = 900
        window_height = 500

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

        # the FILE menu of the file
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=file_menu)
        # save existing file
        file_menu.add_command(label='Save', accelerator= "Ctrl + S", command=self.save_file)
        file_menu.add_separator()
        # save new file
        file_menu.add_command(label='Save As', accelerator= "Ctrl + Shift + S", command=self.save_as_file)
        file_menu.add_separator()
        # load option
        file_menu.add_command(label = 'Open File', accelerator= "Ctrl + O", command=self.load_file)
        file_menu.add_separator()
        # open new tab
        file_menu.add_command(label='New tab', accelerator= "Ctrl + N", command=self.new_tab)
        file_menu.add_separator()
        # close tab
        file_menu.add_command(label='Close Tab', accelerator= "Ctrl + W", command= self.close_tab)
        file_menu.add_separator()
        # new window
        file_menu.add_command(label='New Window', accelerator= "Ctrl + Shift + N", command=self.new_window)
        file_menu.add_separator()
        # close window
        file_menu.add_command(label='Close Window', accelerator= "Ctrl + Shift + W", command=self.close_window)
        file_menu.add_separator()
        # exit all
        file_menu.add_command(label='Exit all', command=self.exit_all)


        # the EDIT menu of the file
        edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label = "Edit", menu= edit_menu)

        # undo option
        edit_menu.add_command(label='Undo', accelerator= "Ctrl + Z", command=self.undo)
        edit_menu.add_separator()
        # redo option
        edit_menu.add_command(label='Redo', accelerator= "Ctrl + Y", command=self.redo)
        edit_menu.add_separator()
        # copy option
        edit_menu.add_command(label='Copy', accelerator= "Ctrl + C", command=self.copy_text)
        edit_menu.add_separator()
        # paste option
        edit_menu.add_command(label='Paste', accelerator= "Ctrl + V", command=self.paste_text)
        edit_menu.add_separator()
        # cut option
        edit_menu.add_command(label='Cut', accelerator= "Ctrl + X", command=self.cut_text)
        edit_menu.add_separator()
        # select all option
        edit_menu.add_command(label='Select All', accelerator= "Ctrl + A", command=self.select_all)
        edit_menu.add_separator()


        self.root.bind("<Control-o>", lambda event: self.load_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_as_file())
        self.root.bind("<Control-n>", lambda event: self.new_tab())
        self.root.bind("<Control-w>", lambda event: self.close_tab())
        self.root.bind("<Control-Shift-N>", lambda event: self.new_window())
        self.root.bind("<Control-Shift-W>", lambda event: self.close_window())
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)

        # exit protocol
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

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
        text = tk.Text(frame, wrap='word', undo = True, yscrollcommand=scrollbar.set)
        text.pack(expand=True, fill='both')
        scrollbar.config(command=text.yview)

        # initiating the changes, tabs and paths
        self.tabs[frame] = text
        self.file_paths[frame] = None
        self.changed[frame] = False

         # detect text changes
        text.bind("<<Modified>>", self.on_text_modified)
        text.bind("<Control-Right>", lambda event: self.move_end_word(event))
        text.bind("<Control-BackSpace>", lambda event: self.delete_whole_word(event))
        

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

        unsaved = [change for frame, change in self.changed.items() if change]

        if unsaved:
            answer = messagebox.askyesnocancel(
                "Unsaved Changes On This Tab",
                "Do you wish to save the changes?"
            )

            if answer:
                self.save_file()
                self.notebook.forget(current_frame)
                current_frame.destroy()
            elif answer == False:
                self.notebook.forget(current_frame)
                current_frame.destroy()
            else:
                return
        else:
            current_frame.destroy()

    def new_window(self, event = None):
        new_root =  tk.Toplevel(self.root)
        TextEditor(new_root)

    def exit_all(self, event = None):
        tk._default_root.destroy()

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


    def close_window(self, event = None):
        # check if any frame has changes
        unsaved = [change for frame, change in self.changed.items() if change]

        # if they do, make a pop up asking if they want to save the changes or not
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
    
    def delete_whole_word(self, event):
        text = event.widget
        current_insert = text.index("insert")
        
        # check if the index is at the beginning of the line
        if current_insert == "1.0":
            return "break"
        
        # we move the index to the left till it finds a character
        start_index = current_insert
        while start_index != "1.0" and text.get(f"{start_index} -1c").isspace():
            start_index = text.index(f"{start_index} -1c")

        # we set the start_index at the beginning of the word
        start_index = text.index(f"{start_index} -1c wordstart")

        # we delete the word
        text.delete(start_index, current_insert)

        return "break"
    
    def undo(self, event = None):
        text = self.get_current_text()
        try:
            text.edit_undo()
        except tk.TclError:
            pass

    def redo(self, event = None):
        text = self.get_current_text()
        try:
            text.edit_redo()
        except tk.TclError:
            pass

    def copy_text(self, event = None):
        text = self.get_current_text()
        try:
            selected = text.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass
    
    def paste_text(self, event = None):
        text = self.get_current_text()
        try:
            clip = self.root.clipboard_get()
            text.insert("insert", clip)
        except tk.TclError:
            pass

    def cut_text(self, event = None):
        text = self.get_current_text()
        try:
            selected = text.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
            text.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

    def select_all(self, event = None):
        text = self.get_current_text()
        text.tag_add("sel", "1.0", "end -1c")
        return "break"

    



root = tk.Tk()
editor = TextEditor(root)

root.mainloop()

