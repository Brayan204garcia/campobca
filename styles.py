from tkinter import ttk
import tkinter as tk

class StyleManager:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        
        # Color palette
        self.colors = {
            'primary': '#2E7D32',      # Green primary
            'primary_light': '#4CAF50', # Light green
            'primary_dark': '#1B5E20',  # Dark green
            'secondary': '#FF9800',     # Orange secondary
            'success': '#4CAF50',       # Success green
            'warning': '#FF9800',       # Warning orange
            'danger': '#F44336',        # Danger red
            'info': '#2196F3',          # Info blue
            'light': '#F5F5F5',         # Light gray
            'dark': '#212121',          # Dark gray
            'white': '#FFFFFF',
            'background': '#F8F9FA',
            'surface': '#FFFFFF',
            'on_primary': '#FFFFFF',
            'on_surface': '#212121',
            'border': '#E0E0E0',
            'hover': '#E8F5E8'
        }
    
    def apply_styles(self):
        """Apply all custom styles"""
        # Configure the theme
        self.style.theme_use('clam')
        
        # Configure general styles
        self.configure_general_styles()
        self.configure_frame_styles()
        self.configure_label_styles()
        self.configure_button_styles()
        self.configure_entry_styles()
        self.configure_treeview_styles()
        self.configure_notebook_styles()
        
    def configure_general_styles(self):
        """Configure general application styles"""
        self.style.configure('.',
            background=self.colors['background'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 10)
        )
    
    def configure_frame_styles(self):
        """Configure frame styles"""
        # Main frame
        self.style.configure('Main.TFrame',
            background=self.colors['background'],
            relief='flat',
            borderwidth=0
        )
        
        # Header frame
        self.style.configure('Header.TFrame',
            background=self.colors['primary'],
            relief='flat',
            borderwidth=0
        )
        
        # Navigation frame
        self.style.configure('Navigation.TFrame',
            background=self.colors['surface'],
            relief='solid',
            borderwidth=1
        )
        
        # Content frame
        self.style.configure('Content.TFrame',
            background=self.colors['surface'],
            relief='solid',
            borderwidth=1
        )
        
        # Card frame for modules
        self.style.configure('Card.TFrame',
            background=self.colors['surface'],
            relief='solid',
            borderwidth=1
        )
    
    def configure_label_styles(self):
        """Configure label styles"""
        # Title label
        self.style.configure('Title.TLabel',
            background=self.colors['primary'],
            foreground=self.colors['on_primary'],
            font=('Segoe UI', 18, 'bold')
        )
        
        # Heading labels
        self.style.configure('Heading.TLabel',
            background=self.colors['surface'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 14, 'bold')
        )
        
        # Subheading labels
        self.style.configure('Subheading.TLabel',
            background=self.colors['surface'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 12, 'bold')
        )
        
        # Status labels
        self.style.configure('Status.TLabel',
            background=self.colors['primary'],
            foreground=self.colors['on_primary'],
            font=('Segoe UI', 10)
        )
        
        self.style.configure('StatusGreen.TLabel',
            background=self.colors['primary'],
            foreground=self.colors['success'],
            font=('Segoe UI', 10, 'bold')
        )
        
        # Stats labels
        self.style.configure('StatValue.TLabel',
            background=self.colors['surface'],
            foreground=self.colors['primary'],
            font=('Segoe UI', 24, 'bold')
        )
        
        self.style.configure('StatLabel.TLabel',
            background=self.colors['surface'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 10)
        )
    
    def configure_button_styles(self):
        """Configure button styles"""
        # Navigation buttons
        self.style.configure('Navigation.TButton',
            background=self.colors['surface'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 10),
            padding=(15, 8),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Navigation.TButton',
            background=[('active', self.colors['hover']),
                       ('pressed', self.colors['primary_light'])]
        )
        
        # Primary buttons
        self.style.configure('Primary.TButton',
            background=self.colors['primary'],
            foreground=self.colors['on_primary'],
            font=('Segoe UI', 10, 'bold'),
            padding=(20, 10),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Primary.TButton',
            background=[('active', self.colors['primary_light']),
                       ('pressed', self.colors['primary_dark'])]
        )
        
        # Secondary buttons
        self.style.configure('Secondary.TButton',
            background=self.colors['light'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 10),
            padding=(15, 8),
            relief='solid',
            borderwidth=1
        )
        
        self.style.map('Secondary.TButton',
            background=[('active', self.colors['border']),
                       ('pressed', self.colors['light'])]
        )
        
        # Danger buttons
        self.style.configure('Danger.TButton',
            background=self.colors['danger'],
            foreground=self.colors['white'],
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 8),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Danger.TButton',
            background=[('active', '#E53935'),
                       ('pressed', '#C62828')]
        )
    
    def configure_entry_styles(self):
        """Configure entry and combobox styles"""
        self.style.configure('Custom.TEntry',
            fieldbackground=self.colors['surface'],
            foreground=self.colors['on_surface'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['border'],
            darkcolor=self.colors['border'],
            insertcolor=self.colors['on_surface'],
            font=('Segoe UI', 10),
            padding=(8, 6)
        )
        
        self.style.configure('Custom.TCombobox',
            fieldbackground=self.colors['surface'],
            foreground=self.colors['on_surface'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['border'],
            darkcolor=self.colors['border'],
            font=('Segoe UI', 10),
            padding=(8, 6)
        )
    
    def configure_treeview_styles(self):
        """Configure treeview styles"""
        self.style.configure('Custom.Treeview',
            background=self.colors['surface'],
            foreground=self.colors['on_surface'],
            fieldbackground=self.colors['surface'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['border'],
            darkcolor=self.colors['border'],
            font=('Segoe UI', 10),
            rowheight=25
        )
        
        self.style.configure('Custom.Treeview.Heading',
            background=self.colors['primary'],
            foreground=self.colors['on_primary'],
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            borderwidth=1
        )
        
        self.style.map('Custom.Treeview',
            background=[('selected', self.colors['primary_light'])],
            foreground=[('selected', self.colors['on_primary'])]
        )
    
    def configure_notebook_styles(self):
        """Configure notebook/tab styles"""
        self.style.configure('Custom.TNotebook',
            background=self.colors['surface'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['border'],
            darkcolor=self.colors['border']
        )
        
        self.style.configure('Custom.TNotebook.Tab',
            background=self.colors['light'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 10),
            padding=(20, 10)
        )
        
        self.style.map('Custom.TNotebook.Tab',
            background=[('selected', self.colors['primary']),
                       ('active', self.colors['hover'])],
            foreground=[('selected', self.colors['on_primary'])]
        )
