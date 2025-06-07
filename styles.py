from tkinter import ttk
import tkinter as tk

class StyleManager:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        
        # Modern color palette
        self.colors = {
            'primary': '#1B5E20',      # Dark green primary
            'primary_light': '#4CAF50', # Light green
            'primary_dark': '#0D2818',  # Very dark green
            'secondary': '#2196F3',     # Blue secondary
            'accent': '#FF6B35',        # Orange accent
            'success': '#4CAF50',       # Success green
            'warning': '#FF9800',       # Warning orange
            'danger': '#F44336',        # Danger red
            'info': '#2196F3',          # Info blue
            'light': '#FAFAFA',         # Very light gray
            'medium': '#E0E0E0',        # Medium gray
            'dark': '#212121',          # Dark gray
            'white': '#FFFFFF',
            'background': '#F5F7FA',    # Soft blue-gray background
            'surface': '#FFFFFF',
            'card': '#FFFFFF',
            'on_primary': '#FFFFFF',
            'on_surface': '#1A1A1A',
            'border': '#E1E5E9',
            'hover': '#E8F5E8',
            'shadow': '#00000020'
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
        
        # Configure relief for modern look
        self.style.configure('TFrame', relief='flat')
        self.style.configure('TLabelFrame', relief='flat')
    
    def configure_frame_styles(self):
        """Configure frame styles"""
        # Main frame
        self.style.configure('Main.TFrame',
            background=self.colors['background'],
            relief='flat',
            borderwidth=0
        )
        
        # Header frame with gradient effect
        self.style.configure('Header.TFrame',
            background=self.colors['primary'],
            relief='flat',
            borderwidth=0
        )
        
        # Navigation frame with modern look
        self.style.configure('Navigation.TFrame',
            background=self.colors['card'],
            relief='flat',
            borderwidth=0
        )
        
        # Content frame
        self.style.configure('Content.TFrame',
            background=self.colors['background'],
            relief='flat',
            borderwidth=0
        )
        
        # Card frame for modules with shadow effect
        self.style.configure('Card.TFrame',
            background=self.colors['card'],
            relief='raised',
            borderwidth=1
        )
        
        # Stats card frame
        self.style.configure('StatsCard.TFrame',
            background=self.colors['card'],
            relief='raised',
            borderwidth=1
        )
    
    def configure_label_styles(self):
        """Configure label styles"""
        # Title label
        self.style.configure('Title.TLabel',
            background=self.colors['primary'],
            foreground=self.colors['on_primary'],
            font=('Segoe UI', 20, 'bold')
        )
        
        # Module heading labels
        self.style.configure('Heading.TLabel',
            background=self.colors['background'],
            foreground=self.colors['primary'],
            font=('Segoe UI', 16, 'bold')
        )
        
        # Subheading labels
        self.style.configure('Subheading.TLabel',
            background=self.colors['card'],
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
            background=self.colors['card'],
            foreground=self.colors['primary'],
            font=('Segoe UI', 24, 'bold')
        )
        
        self.style.configure('StatLabel.TLabel',
            background=self.colors['card'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 14, 'bold')
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
        # Navigation buttons with modern style
        self.style.configure('Navigation.TButton',
            background=self.colors['card'],
            foreground=self.colors['on_surface'],
            font=('Segoe UI', 11, 'bold'),
            padding=(20, 12),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Navigation.TButton',
            background=[('active', self.colors['primary_light']),
                       ('pressed', self.colors['primary'])]
        )
        
        # Primary buttons
        self.style.configure('Primary.TButton',
            background=self.colors['primary'],
            foreground=self.colors['on_primary'],
            font=('Segoe UI', 11, 'bold'),
            padding=(20, 12),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Primary.TButton',
            background=[('active', self.colors['primary_light']),
                       ('pressed', self.colors['primary_dark'])]
        )
        
        # Secondary buttons
        self.style.configure('Secondary.TButton',
            background=self.colors['secondary'],
            foreground=self.colors['white'],
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 10),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Secondary.TButton',
            background=[('active', '#1976D2'),
                       ('pressed', '#0D47A1')]
        )
        
        # Accent buttons
        self.style.configure('Accent.TButton',
            background=self.colors['accent'],
            foreground=self.colors['white'],
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 10),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Accent.TButton',
            background=[('active', '#FF8A50'),
                       ('pressed', '#E64A19')]
        )
        
        # Danger buttons
        self.style.configure('Danger.TButton',
            background=self.colors['danger'],
            foreground=self.colors['white'],
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 10),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map('Danger.TButton',
            background=[('active', '#E53935'),
                       ('pressed', '#C62828')]
        )
    
    def configure_entry_styles(self):
        """Configure entry and combobox styles"""
        # Custom entry fields
        self.style.configure('Custom.TEntry',
            fieldbackground=self.colors['card'],
            borderwidth=1,
            relief='solid',
            padding=(10, 8),
            font=('Segoe UI', 11)
        )
        
        self.style.map('Custom.TEntry',
            focuscolor=[('!focus', self.colors['border']),
                       ('focus', self.colors['primary'])]
        )
        
        # Combobox styling
        self.style.configure('Custom.TCombobox',
            fieldbackground=self.colors['card'],
            borderwidth=1,
            relief='solid',
            padding=(10, 8),
            font=('Segoe UI', 11)
        )
        
        self.style.map('Custom.TCombobox',
            focuscolor=[('!focus', self.colors['border']),
                       ('focus', self.colors['primary'])]
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
