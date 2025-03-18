"""
UI Helper components for Tact Tool
Provides custom UI widgets and functions for a modern UI
"""
import tkinter as tk
import time

class HoverButton(tk.Button):
    """Button with hover effect"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = kwargs.get('bg', self.cget('bg'))
        self.default_fg = kwargs.get('fg', self.cget('fg'))
        self.hover_bg = kwargs.get('activebackground', self.default_bg)
        self.hover_fg = kwargs.get('activeforeground', self.default_fg)
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, e):
        if self.cget('state') != 'disabled':
            self.config(bg=self.hover_bg, fg=self.hover_fg)
        
    def _on_leave(self, e):
        if self.cget('state') != 'disabled':
            self.config(bg=self.default_bg, fg=self.default_fg)

class RoundedFrame(tk.Frame):
    """Frame with rounded corners using a Canvas"""
    def __init__(self, parent, bg, radius=20, **kwargs):
        tk.Frame.__init__(self, parent, background=bg, **kwargs)
        
        # Store parameters
        self.radius = radius
        self.bg = bg
        
        # Create a canvas for drawing the rounded rectangle
        self.canvas = tk.Canvas(
            self,
            bg=bg,
            highlightthickness=0,
            **kwargs
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Create a frame inside the canvas to hold the widgets
        self.container = tk.Frame(self.canvas, bg=bg, **kwargs)
        
        # Add the frame to the canvas using a window
        self.canvas_window = self.canvas.create_window(0, 0, anchor="nw", window=self.container)
        
        # Bind events to redraw the rounded corners when the widget is resized
        self.bind("<Configure>", self._on_configure)
        
    def _on_configure(self, event):
        """Redraw the rounded rectangle when the widget is resized"""
        # Get the widget width and height
        width = event.width
        height = event.height
        
        # Configure the canvas and inner frame
        self.canvas.config(width=width, height=height)
        self.canvas.coords(self.canvas_window, 0, 0)
        self.container.config(width=width, height=height)
        
        # Create a rounded rectangle on the canvas
        self.canvas.delete("rounded_rect")
        self.canvas.create_rounded_rectangle(
            0, 0, width, height,
            radius=self.radius,
            fill=self.bg,
            tags=("rounded_rect",)
        )
        
        # Ensure the inner frame is above the rounded rectangle
        self.canvas.tag_lower("rounded_rect")

# Add rounded rectangle capability to Canvas
def _create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    """Create a rounded rectangle on a canvas"""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return self.create_polygon(points, **kwargs, smooth=True)

# Add method to Canvas class
tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle

def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    tooltip = None
    tooltip_id = None
    
    def enter(event):
        nonlocal tooltip, tooltip_id
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Create a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        frame = tk.Frame(tooltip, background="#1a1a1a", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(
            frame, 
            text=text, 
            justify=tk.LEFT,
            background="#1a1a1a", 
            foreground="#ffffff",
            padx=10,
            pady=5,
            wraplength=250,
            font=("Segoe UI", 9)
        )
        label.pack()
        
    def leave(event):
        nonlocal tooltip, tooltip_id
        if tooltip:
            tooltip.destroy()
            tooltip = None
        if tooltip_id:
            widget.after_cancel(tooltip_id)
            tooltip_id = None
    
    def schedule_tooltip(event):
        nonlocal tooltip_id
        tooltip_id = widget.after(500, lambda: enter(event))
    
    widget.bind("<Enter>", schedule_tooltip)
    widget.bind("<Leave>", leave)
    widget.bind("<ButtonPress>", leave)

def create_button(parent, text, command, **kwargs):
    """Create a styled button"""
    button = HoverButton(
        parent,
        text=text,
        command=command,
        **kwargs
    )
    return button

def create_input(parent, placeholder=None, **kwargs):
    """Create a styled input field with optional placeholder"""
    entry = tk.Entry(parent, **kwargs)
    
    if placeholder:
        entry.insert(0, placeholder)
        
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=kwargs.get('fg', 'black'))
                
        def on_focus_out(event):
            if entry.get() == "":
                entry.insert(0, placeholder)
                entry.config(fg=kwargs.get('placeholder_color', '#858585'))
                
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.config(fg=kwargs.get('placeholder_color', '#858585'))
    
    return entry

class AnimatedProgressBar(tk.Canvas):
    """An animated progress bar"""
    def __init__(self, parent, width=300, height=20, bg_color="#1a1a1a", 
                 fg_color="#00b4ff", **kwargs):
        super().__init__(parent, width=width, height=height, 
                       bg=bg_color, highlightthickness=0, **kwargs)
        
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.width = width
        self.height = height
        self._value = 0
        self.animation_running = False
        
        # Draw the initial bar
        self.draw_bar()
        
    def draw_bar(self):
        """Draw the progress bar"""
        self.delete("all")
        
        # Draw background
        self.create_rounded_rectangle(
            0, 0, self.width, self.height,
            radius=self.height/2,
            fill=self.bg_color,
            outline=""
        )
        
        # Draw progress
        if self._value > 0:
            progress_width = (self.width * self._value) / 100
            self.create_rounded_rectangle(
                0, 0, progress_width, self.height,
                radius=self.height/2,
                fill=self.fg_color,
                outline=""
            )
            
    def set_value(self, value):
        """Set progress value (0-100)"""
        target_value = max(0, min(100, value))
        
        if not self.animation_running:
            self._animate_to(target_value)
            
    def _animate_to(self, target_value):
        """Animate the progress bar to the target value"""
        self.animation_running = True
        current_value = self._value
        steps = 10
        step_value = (target_value - current_value) / steps
        
        def step_animation(current, target, step_num=0):
            if step_num >= steps or self._value == target:
                self._value = target
                self.draw_bar()
                self.animation_running = False
                return
            
            self._value += step_value
            self.draw_bar()
            self.after(20, lambda: step_animation(self._value, target, step_num + 1))
            
        step_animation(current_value, target_value)
