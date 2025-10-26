import tkinter as tk
from tkinter import filedialog, colorchooser, ttk, messagebox
from tkinter import *
import tkinter.font as tkfont
import json
import os

# json file in which we will store the current family, size, slant, weight changes
FONT_FILE = "font.json"

class TextEditor():
    """The main class. Representing the window of the text editor with its functionalities"""
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
        # find option
        edit_menu.add_command(label='Find', accelerator= "Ctrl + F", command=self.find_word)
        edit_menu.add_separator()
        # select all option
        edit_menu.add_command(label='Select All', accelerator= "Ctrl + A", command=self.select_all)
        edit_menu.add_separator()


        # the CUSTOM menu of the file
        custom_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Custom menu", menu=custom_menu)

        # opening Custom Menu
        custom_menu.add_command(label="Open custom window", command=self.custom)


        # root function bindings
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
        """Initiating a tab"""
        # frame of scrollbar and text area
        frame = ttk.Frame(self.notebook, padding=10)
        frame.pack(expand=True, fill='both')

        #add the frame
        self.notebook.add(frame, text = title)

        # scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')

        # import settings or defaults
        settings = self.load_settings()

        # import the text styles
        text_font = tkfont.Font(
            family="Arial",
            size = settings.get("size", 12),
            weight= settings.get("weight", 'normal'),
            slant= settings.get("slant", 'roman'),
        )

        # text area
        text = tk.Text(frame, wrap='word', font = text_font, undo = True, yscrollcommand=scrollbar.set)
        text.pack(expand=True, fill='both')
        scrollbar.config(command=text.yview)

        # initiating the changes, tabs and paths
        self.tabs[frame] = text
        self.file_paths[frame] = None
        self.changed[frame] = False

        # detect text changes
        text.bind("<<Modified>>", self.on_text_modified)
        # other function bindings on text as Undo, Redo
        text.bind("<Control-Right>", lambda event: self.move_end_word(event))
        text.bind("<Control-BackSpace>", lambda event: self.delete_whole_word(event))
        
        self.notebook.select(frame)
        return text
        
    def get_current_text(self):
        """Returns : the current text in our text area"""
        current_tab = self.notebook.nametowidget(self.notebook.select())

        # notebook - dictionary in which keys -> frames/tabs ; values -> text widgets
        return self.tabs[current_tab]
    
    def save_file(self, event = None):
        """Saving an existing file => overwritting it"""
        # current tab : frame
        current_tab = self.notebook.nametowidget(self.notebook.select())
        current_text = self.get_current_text()
        # content : all the text from beginning : '1.0' to end : 'tk.END'
        content = current_text.get(1.0, tk.END)
        # search if the current file has a saved path
        path = self.file_paths.get(current_tab)

        # if it does, we just overwrite the content, else : we must save the new file
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            frm = self.notebook.nametowidget(self.notebook.select())
            self.changed[frm] = False
            label = self.notebook.tab(frm, "text").rstrip("*")
            self.notebook.tab(frm, text = label)
        else:
            self.save_as_file()
  
    def save_as_file(self, event = None):
        """Saving a new file non existing file | saving an existing file as another file"""
        text = self.get_current_text()
        current_tab = self.notebook.nametowidget(self.notebook.select())
        # open filedialog to save the file with a name and extention
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes= [('Text File', '*.txt'), ('All files', '*.*')]
        )
        if path:
            # content : the text from beginning to end
            content = text.get(1.0, tk.END)
            with open(file=path,mode="w", encoding="utf-8") as f:
                f.write(content)

            # updating the changed directory to no changes to this file after save, removing '*'
            self.changed[current_tab] = False
            label = self.notebook.tab(current_tab, "text").rstrip("*")
            self.notebook.tab(current_tab, text = label)

            # adding path
            self.file_paths[current_tab] = path

            # update the title
            self.notebook.tab(current_tab, text=path.split("/")[-1])

    def load_file(self, event = None):
        """Loading a text file in our text editor"""
        text = self.get_current_text()
        path = filedialog.askopenfilename(
            defaultextension='.txt',
            filetypes=[('text files' , '*.txt'), ('All files', '*.*')]
        )
        # if the path exists our current tab will delete its content and get the content of the opened file
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
        """Creating new tab in the window by using the funciton 'create_tab'"""
        self.tab_counter += 1
        self.create_tab(f"Untitled {self.tab_counter}")

    def close_tab(self, event = None):
        """Closes one tab of the window, verifying if there are changes made"""
        current_frame = self.notebook.nametowidget(self.notebook.select())

        # we store in unsaved if there are any frames with modified texts
        unsaved = [change for frame, change in self.changed.items() if change]

        # if there are we ask the user to save it, else: destory the tab
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
        """Create new text editor window"""
        new_root =  tk.Toplevel(self.root)
        TextEditor(new_root)

    def exit_all(self, event = None):
        """Closing all widows"""
        tk._default_root.destroy()

    def on_text_modified(self, event):
        """Function for monitoring text changes
        if text has changed '(.edit_modified())' : title is appended an '*'"""
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
        """Closing window function"""
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
        """Control + Right : move cursor at the end of the current/next word"""
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
        """Control + Backspace : Deleting an entire word"""
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
        """Undo function"""
        text = self.get_current_text()
        try:
            text.edit_undo()
        except tk.TclError:
            pass

    def redo(self, event = None):
        """Redo function"""
        text = self.get_current_text()
        try:
            text.edit_redo()
        except tk.TclError:
            pass

    def copy_text(self, event = None):
        """Copying selected text in clipboard"""
        text = self.get_current_text()
        try:
            selected = text.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass
    
    def paste_text(self, event = None):
        """Appending text from clipboard"""
        text = self.get_current_text()
        try:
            clip = self.root.clipboard_get()
            text.insert("insert", clip)
        except tk.TclError:
            pass

    def cut_text(self, event = None):
        """Deleting and storing in the clipboard text function"""
        text = self.get_current_text()
        try:
            selected = text.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
            text.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

    def select_all(self, event = None):
        """Selecting all text function"""
        text = self.get_current_text()
        text.tag_add("sel", "1.0", "end -1c")
        return "break"
    
    def find_word(self, event = None):
        """Opening a window for finding a word"""
        FindWindow(self.root, self.get_current_text())

    def custom(self, event = None):
        """Opening a window for customising"""
        CustomWindow(self.root, self.get_current_text())

    def load_settings(self):
        """Loading and returning json file content"""
        if os.path.exists(FONT_FILE):
            try:
                with open(FONT_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}

        return {}


class FindWindow():
    """Window for the find function"""
    def __init__(self, master, text_widget):
        """Return an entry of which the text is then searched in the imported text 
        widget using buttons for finding next and previous match"""
        self.top = tk.Toplevel(master)
        self.top.title("Find")
        self.text = text_widget

        # setting window sizes and position
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width // 2) 
        y = 300
        self.top.geometry(f"+{x}+{y}")

        # the "text area" where we insert the word we want to find
        self.entry = tk.Entry(self.top)
        self.entry.pack()

        tk.Button(self.top, text = "Find Prev", command=self.find_prev).pack()
        tk.Button(self.top, text = "Find Next", command=self.find_next).pack()

    def find_next(self):
        """Highlighting the next match and moving cursor at the end of it"""

        # query : the word we are searching for
        query = self.entry.get()

        # position : the position at which 'query' is found
        position = self.text.search(query, "insert", stopindex = "end")

        # if position is found we highlight and move cursor, else: warning
        if position:
            end = f"{position} + {len(query)}c"
            self.text.tag_remove("highlight", "1.0", "end")
            self.text.tag_add("highlight", position, end)
            self.text.tag_config("highlight", background="yellow")
            self.text.mark_set("insert", end)
            self.text.see(position)
        else:
            messagebox.showwarning("Word not found", "Word does not exist!")

    def find_prev(self):
        """Highlighting the previous match and moving cursor at the beginning of it"""

        # query : the word we are searching for
        query = self.entry.get()

        # position : the position at which 'query' is found
        position = self.text.search(query, "insert", stopindex = "1.0", backwards = True)

        # if position is found we highlight and move cursor, else: warning
        if position:
            end = f"{position} + {len(query)}c"
            self.text.tag_remove("highlight", "1.0", "end")
            self.text.tag_add("highlight", position, end)
            self.text.tag_config("highlight", background="yellow")
            self.text.mark_set("insert", position)
            self.text.see(position)
        else:
            messagebox.showwarning("Word not found", "Word does not exist!")


class CustomWindow():
    def __init__(self, master, text_widget):
        
        # initiating pop up window, title, and getting text
        self.top = tk.Toplevel(master)
        self.top.title('Customise')
        self.master = master
        self.text = text_widget

        # setting window sizes and geometry
        width = 550
        height = 250
        screen_width = master.winfo_screenwidth()
        x = (screen_width // 2) - (width // 5) 
        y = 300
        self.top.geometry(f"{width}x{height}+{x}+{y}")

        # saving custom settings on closing window
        self.top.protocol("WM_DELETE_WINDOW", self.close)

        # label to guide into choosing text style
        tk.Label(self.top, text="Select style").pack()

        # style_var will store the font style
        self.style_var = tk.StringVar()

        # dropdown that shows the options: normal, bold, italic styles
        self.dropdown = ttk.Combobox(
            self.top,
            textvariable=self.style_var,
            values=['Normal', 'Bold', 'Italic']
        )
        self.dropdown.current(0)
        self.dropdown.pack()

        # button to apply the style changes
        tk.Button(self.top, text="Apply", command=self.apply_style).pack()

        
        tk.Label(self.top, text= "Select size").pack()

        # entry from which we take the size for the text
        self.entry = tk.Entry(self.top)
        self.entry.pack()

        # size change
        size_button = tk.Button(self.top, text = 'Apply size', command=self.change_size)
        size_button.pack()

        # get current size and insert it as default value in the size entry
        current_font = tkfont.Font(font = self.text.cget('font'))
        current_size = current_font.cget('size')
        self.entry.insert(0,  current_size)

        # color change
        tk.Button(self.top, text = "Choose Text Color", command=self.choose_text_color).pack()

    def apply_style(self):
        """changes font style (weight | slant)"""

        # getting the text selected on dropdown
        style = self.style_var.get()
        # getting the current Font
        font = tkfont.Font(font=self.text.cget("font"))
                                
        # checks if the selected text is bold or italic, and toggles or clears the formatting.
        if style == "Bold":
            if font.actual("weight") == "bold":
                font.configure(weight="normal")
            else:
                font.configure(weight = "bold")
        elif style == "Italic":
            if font.actual("slant") == "italic":
                font.configure(slant= "roman")
            else:
                font.configure(slant = "italic")
        else:
            # Remove formatting
            font.configure(weight = "normal", slant="roman")

        self.text.configure(font = font)

    def change_size(self):
        """Configurating new text size"""
        new_size = int(self.entry.get())
        size = tkfont.Font(font = self.text.cget("font"))
        size.configure(size = int(new_size))
        self.text.configure(font = size)

    def choose_text_color(self):
        """Function for selecting and configurating text color"""
        color = colorchooser.askcolor(title= "choose text color")
        if color[1]:
            self.text.config(fg = color[1])

    def close(self):
        """On closing the window, it automatically saves changes made to font"""
        self.save_settings()
        self.top.destroy()

    def save_settings(self):
        """Saving actual font style, size, color"""

        # geting all the text settings needed
        font = tkfont.Font(font = self.text.cget("font"))
        family = font.cget('family')
        size = font.cget('size')
        slant = font.cget('slant')
        weight = font.cget('weight')

        # storing the settings in a dictionary
        current_settings = {
            'family' : family,
            'size' : size,
            'weight' : weight,
            'slant' : slant
        }

        # saving the settings in the FONT_FILE
        try:
            with open(FONT_FILE, "w") as f:
                json.dump(current_settings, f, indent = 4)
        except json.JSONDecodeError:
            return
        


root = tk.Tk()
editor = TextEditor(root)

root.mainloop()

