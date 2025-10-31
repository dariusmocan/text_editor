import tkinter as tk

class VimEditor():
    def __init__(self, text, status_label):
        self.text = text
        self.status_label = status_label
        self.enabled = False
        self.cutting = False
        self.copying = False
        # self.full_command = ''
        self.mode = 'normal' # normal | insert
        self.command_buffer = ''

        # save and exit functions callback from text_editor
        self.save_callback = None
        self.exit_callback = None


        self.text.bind("<Key>", self.on_key, add = '+')
        self.text.bind('<Escape>', self.on_escape, add = '+')

    # ENABLE | DISABLE : 
    def enable(self):
        """enable vim mode"""
        self.enabled = True
        self.enter_normal()

    def disable(self):
        """disable vim mode"""
        self.enabled = False
        self.show_status('Standard')
    
    # ENTER MODES FUNCTIONS
    def enter_normal(self):
        """enter normal mode"""
        self.mode = 'normal'
        self.show_status('-- NORMAL --')
        self.text.config(insertontime = 700, insertofftime = 100)


    def enter_insert(self):
        """enter insert mode : 'i'"""
        self.mode = 'insert'
        self.show_status('-- INSERT --')
        self.text.config(insertontime = 600, insertofftime = 600)

    def enter_command(self):
        """enter command mode : ':'"""
        self.mode = 'command'
        self.command_buffer += ':'
        self.show_status(self.command_buffer)

    # AUXILIARY FUNCTIONS : 
    def show_status(self, text: str):
        """Update the bottom status label if provided."""
        if self.status_label is None:
            return
        if self.status_label.cget("text") != text:
            self.status_label.config(text=text)
            # optional: force immediate paint
            # self.status_label.update_idletasks()

    def current_line_col(self):
        """return: current line and column index"""
        line, col = self.text.index('insert').split('.')
        return int(line), int(col)
    
    def jump_start_line(self):
        """0 : jump to the start of the line"""
        line = self.current_line_col()[0]
        self.text.mark_set('insert', f"{line}.0")
        # return "break"

    def jump_end_line(self):
        """$ : jump to the end of the line"""
        line= self.current_line_col()[0]
        self.text.mark_set('insert', f"{line}.0 lineend-1c")
    
    def undo(self):
        """undo function"""
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        """redo function"""
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass

    def on_key(self, event = tk.Event):
        """
        handles all normal mode vim functions
        binded: to any key press
        insert mode | disabled = False : return None 
        """
        if not self.enabled:
            return None

        if self.mode == 'command':
            return self.handle_command(event)

        if self.mode == 'insert':
            return None
        
        if self.cutting == True:
            self.cut_options(event)

        if self.copying == True:
            self.copy_options(event)

        # only for normal mode
        ks = event.keysym
        ch = event.char

        # navigating in normal mode
        if ks in ['h', 'Left']:
            self.move_oriz(-1)      
        if ks in ['l', 'Right']:
            self.move_oriz(+1)
        if ks in ['j', 'Down']:
            self.move_vert(+1)
        if ks in ['k', 'Up']:
            self.move_vert(-1)
        if ks == '0':
            self.jump_start_line()
        if ch == '$':
            self.jump_end_line()


        # deleting a character
        if ks == 'x':
            self.delete_char()

        # cutting
        if ks == 'd':
            self.command_buffer += 'd'
            self.cutting = True
            self.show_status(self.command_buffer)

        # copying
        if ks == 'y':
            self.command_buffer += 'y'
            self.copying = True
            self.show_status(self.command_buffer)

        # pasting
        if ks == 'p':
            self.paste()

        # undo and redo
        if ks == 'u':
            self.undo()
        # event state fot Control = 0x4
        if ks == 'r' and (event.state & 0x4):
            self.redo()

        # open line and enter insert mode
        if ks == 'o':
            self.open_line()

        # entering insert mode
        if ks == 'i':
            self.enter_insert()

        # entering command mode
        if event.char == ':':
            self.enter_command()  

        # if ks is any other character, nothing happens
        if event.char and event.char.isprintable():
            return "break"
        return None
    
    # NORMAL MODE FUNCTIONS :
    def go_to_line_col(self, line, col):
        """cursor navigates to a specified position"""

        # max_line: the last line. line is bound to take a value between 1(first) and last line
        max_line = int(self.text.index('end-1c').split('.')[0])
        line = max(1, min(line, max_line))

        # max_col: the last column. col is bound to take a value between 0 (first) and last col
        max_col = int(self.text.index(f"{line}.0 lineend").split('.')[1])
        col = max(0, min(col, max_col))

        # we move cursor to the line and col
        self.text.mark_set("insert", f"{line}.{col}")
        self.text.see('insert')

    def move_vert(self, val):
        """move the cursor up | down"""
        line, col = self.current_line_col()
        # moves cursor +1 (down) or -1 (up)
        self.go_to_line_col(line + val, col)

    def move_oriz(self, val):
        """move the cursor left | right"""
        line, col = self.current_line_col()
        # moves cursor -1 (left) or +1 (right)
        self.go_to_line_col(line, col + val)

    def open_line(self):
        """o : opens line and changes to insert mode"""
        line = self.current_line_col()[0]
        line_end = self.text.index(f"{line}.0 lineend+1c")
        self.text.insert(line_end, '\n')
        self.text.mark_set('insert', f"{line + 1}.0")
        self.enter_insert()

    def delete_char(self, val = 0):
        """ x : delete a single character"""
        # position
        index = self.text.index('insert')
        line = index.split('.')[0]
        # be it different than endline
        if index != self.text.index(f"{line}.0 lineend"):
            self.text.delete(index, f"{index} + {val + 1}c")

        # return "break"

    def cut_options(self, event):
        """d : handle cutting functions in normal mode"""
        ks = event.keysym
        # if 'dd' - delete whole line
        if ks == 'd':
            line = self.current_line_col()[0]
            start_index = f"{line}.0"
            end_index = f"{line}.0 lineend +1c"
            self.text.delete(start_index, end_index)
            # self.text.update_idletasks()

            self.cutting = False
            self.command_buffer = ''
            self.show_status('-- NORMAL --')
            return "break"
        # if dk - delete current line and above
        elif ks == 'k':
            line = self.current_line_col()[0]
            if line > 1:
                start_index = f"{line-1}.0"
                end_index = f"{line}.0 lineend + 1c"
                self.text.delete(start_index, end_index)
                self.text.mark_set('index')
                # self.text.update_idletasks()

                self.cutting = False
                self.command_buffer =''
                self.show_status('-- NORMAL --')
            else:
                self.cutting = False
                self.command_buffer = ''
                self.show_status('-- NORMAL --')
        # deleting behind cursor
        elif ks == 'h' or ks == 'Shift':
            index = self.text.index('insert')
            col = self.current_line_col()[1]
            if col > 0:
                self.text.delete(f"{index} - 1c", f"{index}")
                self.text.mark_set('insert', 'insert +1c')

                self.cutting = False
                self.command_buffer =''
                self.show_status('-- NORMAL --')
            else:
                self.cutting = False
                self.command_buffer =''
                self.show_status('-- NORMAL --')
        # exiting d cut options
        elif ks == 'Escape':
            self.cutting = False
            self.command_buffer = ''
            self.show_status('-- NORMAL --')
            return "break"
        else:
            self.cutting = False
            self.command_buffer = ''
            self.show_status('-- NORMAL --')
            return "break"
        
    def copy_options(self, event):
        """y : handles copying functions in normal mode"""
        ks = event.keysym
        char = event.char
        
        # ignore modifier keys (avoiding cases where: e.g. the key returned by event is 'shift' for 'y$')
        if ks in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            return None
        
        # if 'yy' - copy whole line
        if ks == 'y':
            line = self.current_line_col()[0]
            start_index = f"{line}.0"
            end_index = f"{line}.0 lineend"
            selected = self.text.get(start_index, end_index)
            self.text.clipboard_clear()
            self.text.clipboard_append(selected)

            self.copying = False
            self.command_buffer = ''
            self.show_status('-- NORMAL --')
            return "break"
        # if 'y$' - copy whole line starting from the index
        elif char == '$':
            line = self.current_line_col()[0]
            start_index = "insert"
            end_index = f"{line}.0 lineend"
            selected = self.text.get(start_index, end_index)
            self.text.clipboard_clear()
            self.text.clipboard_append(selected)

            self.copying = False
            self.command_buffer = ''
            self.show_status('-- NORMAL --')
            return "break"
        else:
            self.copying = False
            self.command_buffer =''
            self.show_status('-- NORMAL --')
            return "break"
        
    def paste(self):
        """p : paste text from clipboard function"""
        try:
            coppied_text = self.text.clipboard_get()
            self.text.insert("insert", coppied_text)
        except tk.TclError:
            pass


    # COMMAND MODE FUNCTIONS:
    def handle_command(self, event):
        """handle keys in command mode"""
        ks = event.keysym
        # execute command on Enter
        if ks == 'Return':
            self.execute_command()
            return "break"
        
        # return to normal mode
        if ks == 'Escape':
            self.command_buffer = ''
            self.enter_normal()

        # Backspace
        if ks == 'Backspace':
            if len(self.command_buffer) > 1:
                self.command_buffer = self.command_buffer[:-1]
                self.show_status(self.command_buffer)

        # for characters, append on command_buffer
        if event.char and event.char.isprintable():
            self.command_buffer += event.char
            self.show_status(self.command_buffer)
            return "break"

        return "break"
            
    def execute_command(self):
        cmd = self.command_buffer[1:]

        # save file using save_callback : save_file function from textEditor
        if cmd == 'w':
            self.save_callback()
            self.enter_normal()

        # exit file usingexit_callback : exit_tab function from textEditor
        if cmd == 'q':
            self.exit_callback()

        # wq command - save and exit
        if cmd == 'wq':
            self.save_callback()
            self.exit_callback()

        self.command_buffer = ''

    def on_escape(self, event):
        """Esc : return to normal mode from insert | command mode"""
        if not self.enabled:
            return None
        
        # if vim mode is enabled, and is in insert|command mode, we enter back normal 
        if self.mode == 'insert' or self.mode == 'command':
            self.enter_normal()
            return "break"
        return "break"