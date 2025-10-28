import tkinter as tk

class VimEditor():
    def __init__(self, text, status_label):
        self.text = text
        self.status_label = status_label
        self.enabled = False
        self.mode = 'normal' # normal | insert

        # save function callback from text_editor
        self.save_callback = None

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
        self.show_status(':')

    def show_status(self, text: str):
        """Update the bottom status label if provided."""
        if self.status_label is None:
            return
        if self.status_label.cget("text") != text:
            self.status_label.config(text=text)
            # optional: force immediate paint
            self.status_label.update_idletasks()

    def on_key(self, event = tk.Event):
        """
        handles all normal mode vim functions
        binded: to any key press
        """
        if not self.enabled:
            return None

        if self.mode == 'insert':
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


        if ks == 'i':
            self.enter_insert()

        # if ks is any other character, nothing happens
        if event.char and event.char.isprintable():
            return "break"
        return None
    


    def current_line_col(self):
        """return: current line and column index"""
        line, col = self.text.index('insert').split('.')
        return int(line), int(col)
    
    def go_to_line_col(self, line, col):
        """cursor navigates to another line"""
        max_line = int(self.text.index('end-1c').split('.')[0])
        line = max(1, min(line, max_line))

        max_col = int(self.text.index(f"{line}.0 lineend").split('.')[1])
        col = max(0, min(col, max_col))

        self.text.mark_set("insert", f"{line}.{col}")
        self.text.see('insert')

    def move_vert(self, val):
        """move the cursor up | down"""
        line, col = self.current_line_col()
        self.go_to_line_col(line + val, col)

    def move_oriz(self, val):
        """move the cursor left | right"""
        line, col = self.current_line_col()
        self.go_to_line_col(line, col + val)


    def on_escape(self, event):
        if not self.enabled:
            return None
        
        if self.mode == 'insert':
            self.enter_normal()
            return "break"
        return "break"