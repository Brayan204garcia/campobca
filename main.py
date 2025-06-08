import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from database import DatabaseManager
from styles import StyleManager
from modules.dashboard import Dashboard
from modules.farmers import FarmersModule
from modules.sales_points import SalesPointsModule  
from modules.distribution import DistributionModule
from modules.drivers import DriversModule
from modules.deliveries import DeliveriesModule
from modules.reports import ReportsModule

class AgriculturalCooperativeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Coordinación Agrícola")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Initialize database
        try:
            self.db = DatabaseManager()
            self.db.initialize_database()
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo inicializar la base de datos: {str(e)}")
            sys.exit(1)
        
        # Initialize styling
        self.style_manager = StyleManager(self.root)
        self.style_manager.apply_styles()
        
        # Configure root window
        self.root.configure(bg='#f8f9fa')
        
        # Initialize modules
        self.current_module = None
        self.modules = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Navigation
        self.create_navigation()
        
        # Content area
        self.content_frame = ttk.Frame(self.main_frame, style='Content.TFrame')
        self.content_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Load dashboard by default
        self.show_module('dashboard')
        
    def create_header(self):
        """Create the application header"""
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="🌾 Sistema de Coordinación Agrícola",
            style='Title.TLabel'
        )
        title_label.pack(side='left')
        
        # Status indicator
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side='right')
        
        ttk.Label(status_frame, text="Estado:", style='Status.TLabel').pack(side='left')
        ttk.Label(status_frame, text="● Conectado", style='StatusGreen.TLabel').pack(side='left', padx=(5, 0))
        
    def create_navigation(self):
        """Create the navigation menu"""
        nav_frame = ttk.Frame(self.main_frame, style='Navigation.TFrame')
        nav_frame.pack(fill='x', pady=(0, 10))
        
        nav_buttons = [
            ("📊 Panel Principal", 'dashboard'),
            ("👨‍🌾 Agricultores", 'farmers'),
            ("🏪 Puntos de Venta", 'sales_points'),
            ("🚚 Distribución", 'distribution'),
            ("🚗 Conductores", 'drivers'),
            ("🚛 Entregas", 'deliveries'),
            ("📈 Reportes", 'reports')
        ]
        
        for text, module_name in nav_buttons:
            btn = ttk.Button(
                nav_frame,
                text=text,
                style='Navigation.TButton',
                command=lambda m=module_name: self.show_module(m)
            )
            btn.pack(side='left', padx=(0, 10))
    
    def show_module(self, module_name):
        """Show the specified module"""
        # Hide current module
        if self.current_module:
            self.current_module.hide()
        
        # Create module if not exists
        if module_name not in self.modules:
            if module_name == 'dashboard':
                self.modules[module_name] = Dashboard(self.content_frame, self.db)
            elif module_name == 'farmers':
                self.modules[module_name] = FarmersModule(self.content_frame, self.db)
            elif module_name == 'sales_points':
                self.modules[module_name] = SalesPointsModule(self.content_frame, self.db)
            elif module_name == 'distribution':
                self.modules[module_name] = DistributionModule(self.content_frame, self.db)
            elif module_name == 'drivers':
                self.modules[module_name] = DriversModule(self.content_frame, self.db)
            elif module_name == 'deliveries':
                self.modules[module_name] = DeliveriesModule(self.content_frame, self.db)
            elif module_name == 'reports':
                self.modules[module_name] = ReportsModule(self.content_frame, self.db)
        
        # Show new module
        self.current_module = self.modules[module_name]
        self.current_module.show()
        
        # Refresh data when switching to distribution module to ensure updated status
        if module_name == 'distribution' and hasattr(self.current_module, 'refresh_requests'):
            self.current_module.refresh_requests()
    
    def refresh_all_modules(self):
        """Refresh data in all initialized modules"""
        for module in self.modules.values():
            if hasattr(module, 'refresh_requests'):
                module.refresh_requests()
            if hasattr(module, 'refresh_data'):
                module.refresh_data()
            if hasattr(module, 'refresh_dashboard'):
                module.refresh_dashboard()
        
    def run(self):
        """Start the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Salir", "¿Desea cerrar la aplicación?"):
            if hasattr(self, 'db'):
                self.db.close()
            self.root.destroy()

if __name__ == "__main__":
    try:
        app = AgriculturalCooperativeApp()
        app.run()
    except Exception as e:
        print(f"Error fatal: {e}")
        messagebox.showerror("Error Fatal", f"La aplicación no pudo iniciarse: {str(e)}")
