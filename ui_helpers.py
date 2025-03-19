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
        """Mouse enters button with smooth transition"""
        steps = 5
        r1, g1, b1 = self._hex_to_rgb(self.default_bg)
        r2, g2, b2 = self._hex_to_rgb(self.hover_bg)
        
        for i in range(steps + 1):
            r = r1 + (r2 - r1) * i // steps
            g = g1 + (g2 - g1) * i // steps
            b = b1 + (b2 - b1) * i // steps
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.after(i * 20, lambda c=color: self.config(bg=c))
        self.config(fg=self.hover_fg)
    
    def _on_leave(self, e):
        """Mouse leaves button with smooth transition"""
        steps = 5
        r1, g1, b1 = self._hex_to_rgb(self.hover_bg)
        r2, g2, b2 = self._hex_to_rgb(self.default_bg)
        
        for i in range(steps + 1):
            r = r1 + (r2 - r1) * i // steps
            g = g1 + (g2 - g1) * i // steps
            b = b1 + (b2 - b1) * i // steps
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.after(i * 20, lambda c=color: self.config(bg=c))
        self.config(fg=self.default_fg)
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

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
