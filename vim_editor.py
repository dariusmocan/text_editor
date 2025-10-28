import tkinter as tk

class VimEditor():
    def __init__(self, text, status_label):
        self.text = text
        self.status_label = status_label
        self.enabled = False
        self.mode = 'normal' # normal | insert
        self.command_buffer = ''

        # save and exit functions callback from text_editor
        self.save_callback = None
        self.exit_callback = None


        self.text.bind("<Key>", self.on_key, add = '+')
        self.text.bind('<Escape>', self.on_escape, add = '+')

    
    def enable(self):
        """enable vim mode"""
        self.enabled = True
        self.enter_normal()

    def disable(self):
        """disable vim mode"""
        self.enabled = False
        self.show_status('Standard')
    

    def enter_normal(self):
        """enter normal mode"""
        self.mode = 'normal'
        self.show_status('-- NORMAL --')


    def enter_insert(self):
        """enter insert mode : 'i'"""
        self.mode = 'insert'
        self.show_status('-- INSERT --')

    def enter_command(self):
        """enter command mode : ':'"""
        self.mode = 'command'
        self.command_buffer += ':'
        self.show_status(self.command_buffer)

    def show_status(self, text: str):
        """Update the bottom status label if provided."""
        if self.status_label is None:
            return
        if self.status_label.cget("text") != text:
            self.status_label.config(text=text)
            # optional: force immediate paint
            # self.status_label.update_idletasks()

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

        if self.mode == 'insert' or self.mode == 'command':
            return None

        # only for normal mode
        ks = event.keysym

        # navigating in normal mode
        if ks in ['h', 'Left']:
            self.move_oriz(-1)      
        if ks in ['l', 'Right']:
            self.move_oriz(+1)
        if ks in ['j', 'Down']:
            self.move_vert(+1)
        if ks in ['k', 'Up']:
            self.move_vert(-1)

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




    def current_line_col(self):
        """return: current line and column index"""
        line, col = self.text.index('insert').split('.')
        return int(line), int(col)
    
    def go_to_line_col(self, line, col):
        """cursor navigates to another line"""
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


    def on_escape(self, event):
        if not self.enabled:
            return None
        
        # if vim mode is enabled, and is in insert|command mode, we enter back normal 
        if self.mode == 'insert' or self.mode == 'command':
            self.enter_normal()
            return "break"
        return "break"