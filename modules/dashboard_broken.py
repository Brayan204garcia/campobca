import tkinter as tk
from tkinter import ttk, messagebox
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
            products = self.db.get_products()
            farmers = self.db.get_farmers()
            
            # Create farmer lookup
            farmer_lookup = {f['id']: f['name'] for f in farmers}
            
            # Find expiring products (within 7 days)
            from datetime import datetime, timedelta
            future_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            expiring_products = []
            for product in products:
                if not product.get('available', True):
                    continue
                expiry_date = product.get('expiry_date')
                if expiry_date and expiry_date <= future_date:
                    product['farmer_name'] = farmer_lookup.get(product.get('farmer_id'), 'Desconocido')
                    expiring_products.append(product)
            
            # Sort by expiry date
            expiring_products.sort(key=lambda x: x.get('expiry_date', ''))
            
            if expiring_products:
                alerts_text.insert('end', "⚠️ PRODUCTOS PRÓXIMOS A VENCER:\n\n", 'warning')
                for product in expiring_products[:5]:  # Show first 5
                    days_left = (datetime.strptime(product['expiry_date'], '%Y-%m-%d') - datetime.now()).days
                    alerts_text.insert('end', f"• {product['name']} ({product['farmer_name']}) - {days_left} días\n")
                
                if len(expiring_products) > 5:
                    alerts_text.insert('end', f"\n...y {len(expiring_products) - 5} productos más\n")
            else:
                alerts_text.insert('end', "✅ No hay productos próximos a vencer en los próximos 7 días.\n", 'success')
            
            # Configure text tags
            alerts_text.tag_configure('warning', font=('Segoe UI', 10, 'bold'), foreground='#FF9800')
            alerts_text.tag_configure('success', font=('Segoe UI', 10, 'bold'), foreground='#4CAF50')
            alerts_text.config(state='disabled')
            
        except Exception as e:
            alerts_text.insert('end', f"Error cargando alertas: {str(e)}")
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        if self.frame:
            self.frame.destroy()
            self.create_dashboard_content()
    
    def quick_add_farmer(self):
        """Quick add farmer action"""
        # Create quick add farmer dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Agricultor Rápido")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = ttk.LabelFrame(dialog, text="Información del Agricultor", padding=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Name field
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky='w', pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Phone field
        ttk.Label(form_frame, text="Teléfono:").grid(row=1, column=0, sticky='w', pady=5)
        phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=phone_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Location field
        ttk.Label(form_frame, text="Ubicación:").grid(row=2, column=0, sticky='w', pady=5)
        location_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=location_var, width=30).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Email field
        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky='w', pady=5)
        email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=email_var, width=30).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        def save_farmer():
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre es requerido")
                return
            
            farmer_data = {
                'name': name_var.get().strip(),
                'phone': phone_var.get().strip(),
                'location': location_var.get().strip(),
                'email': email_var.get().strip(),
                'active': True
            }
            
            try:
                self.db.add_farmer(farmer_data)
                messagebox.showinfo("Éxito", "Agricultor agregado exitosamente")
                dialog.destroy()
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Error agregando agricultor: {str(e)}")
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Guardar", command=save_farmer, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy, style='Secondary.TButton').pack(side='left')
    
    def quick_add_product(self):
        """Quick add product action"""
        # Create quick add product dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Producto Rápido")
        dialog.geometry("450x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = ttk.LabelFrame(dialog, text="Información del Producto", padding=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Get farmers for dropdown
        farmers = self.db.get_farmers(active_only=True)
        farmer_names = [f"{f['name']} (ID: {f['id']})" for f in farmers]
        
        if not farmers:
            messagebox.showwarning("Advertencia", "Primero debe agregar agricultores")
            dialog.destroy()
            return
        
        # Farmer selection
        ttk.Label(form_frame, text="Agricultor:").grid(row=0, column=0, sticky='w', pady=5)
        farmer_var = tk.StringVar()
        farmer_combo = ttk.Combobox(form_frame, textvariable=farmer_var, values=farmer_names, state='readonly', width=35)
        farmer_combo.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Product name
        ttk.Label(form_frame, text="Nombre:").grid(row=1, column=0, sticky='w', pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=35).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Category
        ttk.Label(form_frame, text="Categoría:").grid(row=2, column=0, sticky='w', pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, 
                                    values=['Verduras', 'Frutas', 'Granos', 'Legumbres', 'Hierbas', 'Otros'], 
                                    state='readonly', width=35)
        category_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Quantity
        ttk.Label(form_frame, text="Cantidad:").grid(row=3, column=0, sticky='w', pady=5)
        quantity_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=quantity_var, width=35).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Unit
        ttk.Label(form_frame, text="Unidad:").grid(row=4, column=0, sticky='w', pady=5)
        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(form_frame, textvariable=unit_var, 
                                values=['kg', 'g', 'lb', 'unidades', 'cajas', 'sacos'], 
                                state='readonly', width=35)
        unit_combo.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Price
        ttk.Label(form_frame, text="Precio por unidad:").grid(row=5, column=0, sticky='w', pady=5)
        price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=price_var, width=35).grid(row=5, column=1, pady=5, padx=(10, 0))
        
        # Expiry date
        ttk.Label(form_frame, text="Fecha vencimiento (YYYY-MM-DD):").grid(row=6, column=0, sticky='w', pady=5)
        expiry_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=expiry_var, width=35).grid(row=6, column=1, pady=5, padx=(10, 0))
        
        def save_product():
            if not all([farmer_var.get(), name_var.get().strip(), category_var.get(), 
                       quantity_var.get().strip(), unit_var.get(), price_var.get().strip()]):
                messagebox.showerror("Error", "Todos los campos son requeridos")
                return
            
            try:
                # Extract farmer ID from selection
                farmer_id = int(farmer_var.get().split("ID: ")[1].split(")")[0])
                quantity = float(quantity_var.get())
                price = float(price_var.get())
                
                product_data = {
                    'farmer_id': farmer_id,
                    'name': name_var.get().strip(),
                    'category': category_var.get(),
                    'quantity': quantity,
                    'unit': unit_var.get(),
                    'price_per_unit': price,
                    'expiry_date': expiry_var.get().strip() if expiry_var.get().strip() else None,
                    'available': True
                }
                
                self.db.add_product(product_data)
                messagebox.showinfo("Éxito", "Producto agregado exitosamente")
                dialog.destroy()
                self.refresh_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")
            except Exception as e:
                messagebox.showerror("Error", f"Error agregando producto: {str(e)}")
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Guardar", command=save_product, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy, style='Secondary.TButton').pack(side='left')
    
    def quick_add_sales_point(self):
        """Quick add sales point action"""
        # Create quick add sales point dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Punto de Venta Rápido")
        dialog.geometry("400x350")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = ttk.LabelFrame(dialog, text="Información del Punto de Venta", padding=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Name field
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky='w', pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Type field
        ttk.Label(form_frame, text="Tipo:").grid(row=1, column=0, sticky='w', pady=5)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, 
                                values=['Supermercado', 'Restaurante', 'Mercado', 'Tienda', 'Distribuidor'], 
                                state='readonly', width=28)
        type_combo.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Address field
        ttk.Label(form_frame, text="Dirección:").grid(row=2, column=0, sticky='w', pady=5)
        address_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=address_var, width=30).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Contact field
        ttk.Label(form_frame, text="Contacto:").grid(row=3, column=0, sticky='w', pady=5)
        contact_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=contact_var, width=30).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Phone field
        ttk.Label(form_frame, text="Teléfono:").grid(row=4, column=0, sticky='w', pady=5)
        phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=phone_var, width=30).grid(row=4, column=1, pady=5, padx=(10, 0))
        
        def save_sales_point():
            if not all([name_var.get().strip(), type_var.get(), address_var.get().strip()]):
                messagebox.showerror("Error", "Nombre, tipo y dirección son requeridos")
                return
            
            sales_point_data = {
                'name': name_var.get().strip(),
                'type': type_var.get(),
                'address': address_var.get().strip(),
                'contact_person': contact_var.get().strip(),
                'phone': phone_var.get().strip(),
                'active': True
            }
            
            try:
                self.db.add_sales_point(sales_point_data)
                messagebox.showinfo("Éxito", "Punto de venta agregado exitosamente")
                dialog.destroy()
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Error agregando punto de venta: {str(e)}")
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Guardar", command=save_sales_point, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy, style='Secondary.TButton').pack(side='left')
    
    def quick_add_request(self):
        """Quick add distribution request action"""
        # Create quick add request dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Nueva Solicitud de Distribución")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = ttk.LabelFrame(dialog, text="Nueva Solicitud", padding=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Get data for dropdowns
        sales_points = self.db.get_sales_points(active_only=True)
        products = self.db.get_products(available_only=True)
        
        if not sales_points:
            messagebox.showwarning("Advertencia", "Primero debe agregar puntos de venta")
            dialog.destroy()
            return
        
        if not products:
            messagebox.showwarning("Advertencia", "Primero debe agregar productos")
            dialog.destroy()
            return
        
        # Sales point selection
        ttk.Label(form_frame, text="Punto de Venta:").grid(row=0, column=0, sticky='w', pady=5)
        sales_point_var = tk.StringVar()
        sales_point_names = [f"{sp['name']} - {sp['type']}" for sp in sales_points]
        sales_point_combo = ttk.Combobox(form_frame, textvariable=sales_point_var, 
                                       values=sales_point_names, state='readonly', width=35)
        sales_point_combo.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Product selection
        ttk.Label(form_frame, text="Producto:").grid(row=1, column=0, sticky='w', pady=5)
        product_var = tk.StringVar()
        product_names = [f"{p['name']} - {p['farmer_name']} ({p['quantity']} {p['unit']})" for p in products]
        product_combo = ttk.Combobox(form_frame, textvariable=product_var, 
                                   values=product_names, state='readonly', width=35)
        product_combo.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Quantity requested
        ttk.Label(form_frame, text="Cantidad Solicitada:").grid(row=2, column=0, sticky='w', pady=5)
        quantity_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=quantity_var, width=35).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Delivery date
        ttk.Label(form_frame, text="Fecha Entrega (YYYY-MM-DD):").grid(row=3, column=0, sticky='w', pady=5)
        delivery_date_var = tk.StringVar()
        delivery_date_var.set((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
        ttk.Entry(form_frame, textvariable=delivery_date_var, width=35).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Priority
        ttk.Label(form_frame, text="Prioridad:").grid(row=4, column=0, sticky='w', pady=5)
        priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(form_frame, textvariable=priority_var, 
                                    values=['Normal', 'Alta', 'Urgente'], state='readonly', width=35)
        priority_combo.set('Normal')
        priority_combo.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Notes
        ttk.Label(form_frame, text="Notas:").grid(row=5, column=0, sticky='w', pady=5)
        notes_text = tk.Text(form_frame, height=4, width=35)
        notes_text.grid(row=5, column=1, pady=5, padx=(10, 0))
        
        def save_request():
            if not all([sales_point_var.get(), product_var.get(), quantity_var.get().strip(), delivery_date_var.get().strip()]):
                messagebox.showerror("Error", "Todos los campos son requeridos")
                return
            
            try:
                # Get selected sales point and product IDs
                sales_point_id = sales_points[sales_point_combo.current()]['id']
                product = products[product_combo.current()]
                product_id = product['id']
                quantity_requested = float(quantity_var.get())
                
                # Validate quantity
                if quantity_requested > product['quantity']:
                    messagebox.showerror("Error", f"Cantidad solicitada excede el stock disponible ({product['quantity']} {product['unit']})")
                    return
                
                request_data = {
                    'sales_point_id': sales_point_id,
                    'products': [{
                        'product_id': product_id,
                        'quantity': quantity_requested
                    }],
                    'delivery_date': delivery_date_var.get().strip(),
                    'priority': priority_var.get(),
                    'notes': notes_text.get(1.0, tk.END).strip(),
                    'status': 'Pendiente'
                }
                
                self.db.add_distribution_request_with_auto_assignment(request_data)
                messagebox.showinfo("Éxito", "Solicitud de distribución creada exitosamente")
                dialog.destroy()
                self.refresh_dashboard()
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error creando solicitud: {str(e)}")
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Guardar", command=save_request, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy, style='Secondary.TButton').pack(side='left')
            
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
    

