"""
UI Helper components for Tact Tool
Provides custom UI widgets and functions for a modern UI
"""
import tkinter as tk
from tkinter import ttk

class HoverButton(tk.Button):
    """Button with hover effect"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = kwargs.get('bg') or self.cget('bg')
        self.default_fg = kwargs.get('fg') or self.cget('fg')
        self.hover_bg = kwargs.get('activebackground') or self.default_bg
        self.hover_fg = kwargs.get('activeforeground') or self.default_fg
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        """Mouse enters button"""
        self.config(bg=self.hover_bg, fg=self.hover_fg)
    
    def _on_leave(self, e):
        """Mouse leaves button"""
        self.config(bg=self.default_bg, fg=self.default_fg)

def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    tooltip = None
    scheduled_id = None
    
    def enter(event):
        nonlocal scheduled_id
        scheduled_id = widget.after(500, schedule_tooltip)
    
    def leave(event):
        nonlocal tooltip, scheduled_id
        if scheduled_id:
            widget.after_cancel(scheduled_id)
            scheduled_id = None
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    def schedule_tooltip():
        nonlocal tooltip
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Create a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tooltip, 
            text=text, 
            justify=tk.LEFT,
            background="#202020", 
            foreground="white",
            relief=tk.SOLID, 
            borderwidth=1,
            padx=10,
            pady=5,
            font=("Arial", 9)
        )
        label.pack()
    
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
