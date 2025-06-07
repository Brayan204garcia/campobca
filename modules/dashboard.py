import tkinter as tk
from tkinter import ttk
from typing import Dict
from datetime import datetime, timedelta
import sqlite3

class Dashboard:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.frame = None
        
    def show(self):
        """Show the dashboard module"""
        if self.frame:
            self.frame.destroy()
        
        self.frame = ttk.Frame(self.parent, style='Card.TFrame')
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_dashboard_content()
        
    def hide(self):
        """Hide the dashboard module"""
        if self.frame:
            self.frame.destroy()
            self.frame = None
    
    def create_dashboard_content(self):
        """Create the dashboard content"""
        # Title
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(title_frame, text="Panel Principal", style='Heading.TLabel').pack(side='left')
        
        # Refresh button
        ttk.Button(title_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_dashboard).pack(side='right')
        
        # Stats section
        self.create_stats_section()
        
        # Quick actions section
        self.create_quick_actions_section()
        
        # Recent activity section
        self.create_recent_activity_section()
        
        # Alerts section
        self.create_alerts_section()
    
    def create_stats_section(self):
        """Create the statistics section"""
        stats_frame = ttk.LabelFrame(self.frame, text="Estadísticas Generales", padding=20)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        try:
            stats = self.db.get_dashboard_stats()
            
            # Create stat cards
            cards_frame = ttk.Frame(stats_frame)
            cards_frame.pack(fill='x')
            
            stat_cards = [
                ("👨‍🌾", "Agricultores", stats.get('total_farmers', 0)),
                ("🥕", "Productos", stats.get('total_products', 0)),
                ("🏪", "Puntos de Venta", stats.get('total_sales_points', 0)),
                ("📋", "Solicitudes Pendientes", stats.get('pending_requests', 0)),
                ("⚠️", "Productos por Vencer", stats.get('expiring_soon', 0))
            ]
            
            for i, (icon, label, value) in enumerate(stat_cards):
                card = ttk.Frame(cards_frame, style='Card.TFrame', relief='raised', borderwidth=1)
                card.pack(side='left', fill='both', expand=True, padx=(0, 10) if i < len(stat_cards)-1 else (0, 0))
                
                # Icon and value
                icon_frame = ttk.Frame(card)
                icon_frame.pack(pady=10)
                
                ttk.Label(icon_frame, text=icon, font=('Segoe UI', 20)).pack()
                ttk.Label(icon_frame, text=str(value), style='StatValue.TLabel').pack()
                ttk.Label(icon_frame, text=label, style='StatLabel.TLabel').pack()
                
        except Exception as e:
            error_label = ttk.Label(stats_frame, text=f"Error cargando estadísticas: {str(e)}", 
                                  foreground='red')
            error_label.pack()
    
    def create_quick_actions_section(self):
        """Create quick actions section"""
        actions_frame = ttk.LabelFrame(self.frame, text="Acciones Rápidas", padding=20)
        actions_frame.pack(fill='x', padx=20, pady=10)
        
        buttons_frame = ttk.Frame(actions_frame)
        buttons_frame.pack()
        
        quick_buttons = [
            ("➕ Nuevo Agricultor", self.quick_add_farmer),
            ("🥕 Nuevo Producto", self.quick_add_product),
            ("🏪 Nuevo Punto de Venta", self.quick_add_sales_point),
            ("📋 Nueva Solicitud", self.quick_add_request)
        ]
        
        for text, command in quick_buttons:
            btn = ttk.Button(buttons_frame, text=text, style='Primary.TButton', command=command)
            btn.pack(side='left', padx=(0, 10))
    
    def create_recent_activity_section(self):
        """Create recent activity section"""
        activity_frame = ttk.LabelFrame(self.frame, text="Actividad Reciente", padding=20)
        activity_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create treeview for recent activities
        columns = ('Fecha', 'Tipo', 'Descripción')
        activity_tree = ttk.Treeview(activity_frame, columns=columns, show='headings', 
                                   style='Custom.Treeview', height=8)
        
        for col in columns:
            activity_tree.heading(col, text=col)
            if col == 'Fecha':
                activity_tree.column(col, width=120, minwidth=100)
            elif col == 'Tipo':
                activity_tree.column(col, width=150, minwidth=120)
            else:
                activity_tree.column(col, minwidth=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(activity_frame, orient='vertical', command=activity_tree.yview)
        activity_tree.configure(yscrollcommand=scrollbar.set)
        
        activity_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load recent activity
        self.load_recent_activity(activity_tree)
    
    def create_alerts_section(self):
        """Create alerts section"""
        alerts_frame = ttk.LabelFrame(self.frame, text="Alertas y Notificaciones", padding=20)
        alerts_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        self.load_alerts(alerts_frame)
    
    def load_recent_activity(self, tree):
        """Load recent activity data"""
        try:
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            # Get recent products (last 10)
            products = self.db.get_products()
            recent_products = sorted(products, key=lambda x: x.get('created_date', ''), reverse=True)[:5]
            
            for product in recent_products:
                date_str = product.get('created_date', '')[:10] if product.get('created_date') else 'N/A'
                tree.insert('', 'end', values=(
                    date_str,
                    'Nuevo Producto',
                    f"{product['name']} - {product['farmer_name']}"
                ))
            
            # If no recent activity
            if not recent_products:
                tree.insert('', 'end', values=('', 'Sin actividad', 'No hay actividad reciente'))
                
        except Exception as e:
            tree.insert('', 'end', values=('Error', 'Error', f'Error cargando actividad: {str(e)}'))
    
    def load_alerts(self, parent):
        """Load alerts and notifications"""
        try:
            alerts_text = tk.Text(parent, height=4, wrap=tk.WORD, font=('Segoe UI', 10))
            alerts_text.pack(fill='x')
            
            # Get products expiring soon
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.name, p.expiry_date, f.name as farmer_name
                FROM products p
                JOIN farmers f ON p.farmer_id = f.id
                WHERE p.available = 1 AND p.expiry_date <= date('now', '+7 days')
                ORDER BY p.expiry_date
            ''')
            
            expiring_products = cursor.fetchall()
            conn.close()
            
            if expiring_products:
                alerts_text.insert('end', "⚠️ PRODUCTOS POR VENCER:\n", 'warning')
                for product in expiring_products:
                    alerts_text.insert('end', f"• {product['name']} ({product['farmer_name']}) - Vence: {product['expiry_date']}\n")
            else:
                alerts_text.insert('end', "✅ No hay alertas críticas en este momento.\n", 'success')
            
            # Configure text tags
            alerts_text.tag_configure('warning', foreground='#FF9800', font=('Segoe UI', 10, 'bold'))
            alerts_text.tag_configure('success', foreground='#4CAF50', font=('Segoe UI', 10, 'bold'))
            
            alerts_text.configure(state='disabled')
            
        except Exception as e:
            error_label = ttk.Label(parent, text=f"Error cargando alertas: {str(e)}", 
                                  foreground='red')
            error_label.pack()
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        self.create_dashboard_content()
    
    # Quick action methods (these would typically open the respective modules)
    def quick_add_farmer(self):
        """Quick add farmer action"""
        pass  # Would open farmer module with add form
    
    def quick_add_product(self):
        """Quick add product action"""
        pass  # Would open farmer module with product form
    
    def quick_add_sales_point(self):
        """Quick add sales point action"""
        pass  # Would open sales point module with add form
    
    def quick_add_request(self):
        """Quick add distribution request action"""
        pass  # Would open distribution module with request form
