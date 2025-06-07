import tkinter as tk
from tkinter import ttk, messagebox
from utils.validators import Validator
from datetime import datetime

class FarmersModule:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.frame = None
        self.current_farmer_id = None
        
    def show(self):
        """Show the farmers module"""
        if self.frame:
            self.frame.destroy()
        
        self.frame = ttk.Frame(self.parent, style='Card.TFrame')
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_farmers_interface()
        
    def hide(self):
        """Hide the farmers module"""
        if self.frame:
            self.frame.destroy()
            self.frame = None
    
    def create_farmers_interface(self):
        """Create the farmers management interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.frame, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Farmers tab
        farmers_tab = ttk.Frame(notebook)
        notebook.add(farmers_tab, text="Gestión de Agricultores")
        
        # Products tab
        products_tab = ttk.Frame(notebook)
        notebook.add(products_tab, text="Gestión de Productos")
        
        # Create farmers management
        self.create_farmers_management(farmers_tab)
        
        # Create products management
        self.create_products_management(products_tab)
    
    def create_farmers_management(self, parent):
        """Create farmers management interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Gestión de Agricultores", style='Heading.TLabel').pack(side='left')
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="➕ Nuevo Agricultor", 
                  style='Primary.TButton',
                  command=self.show_farmer_form).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_farmers).pack(side='left')
        
        # Main content frame
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Farmers list (left side)
        list_frame = ttk.LabelFrame(content_frame, text="Lista de Agricultores", padding=10)
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Search frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Buscar:").pack(side='left')
        self.farmer_search_var = tk.StringVar()
        self.farmer_search_var.trace('w', self.filter_farmers)
        ttk.Entry(search_frame, textvariable=self.farmer_search_var, 
                 style='Custom.TEntry', width=30).pack(side='left', padx=(5, 0))
        
        # Farmers treeview
        columns = ('ID', 'Nombre', 'Email', 'Teléfono', 'Fecha Registro')
        self.farmers_tree = ttk.Treeview(list_frame, columns=columns, show='headings', 
                                       style='Custom.Treeview', height=15)
        
        for col in columns:
            self.farmers_tree.heading(col, text=col)
            if col == 'ID':
                self.farmers_tree.column(col, width=50, minwidth=50)
            elif col == 'Nombre':
                self.farmers_tree.column(col, width=150, minwidth=120)
            elif col == 'Email':
                self.farmers_tree.column(col, width=200, minwidth=150)
            elif col == 'Teléfono':
                self.farmers_tree.column(col, width=120, minwidth=100)
            else:
                self.farmers_tree.column(col, width=120, minwidth=100)
        
        # Scrollbars for farmers tree
        farmers_scrollbar_y = ttk.Scrollbar(list_frame, orient='vertical', command=self.farmers_tree.yview)
        farmers_scrollbar_x = ttk.Scrollbar(list_frame, orient='horizontal', command=self.farmers_tree.xview)
        self.farmers_tree.configure(yscrollcommand=farmers_scrollbar_y.set, xscrollcommand=farmers_scrollbar_x.set)
        
        self.farmers_tree.pack(side='left', fill='both', expand=True)
        farmers_scrollbar_y.pack(side='right', fill='y')
        farmers_scrollbar_x.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.farmers_tree.bind('<<TreeviewSelect>>', self.on_farmer_select)
        
        # Form frame (right side)
        self.farmer_form_frame = ttk.LabelFrame(content_frame, text="Información del Agricultor", padding=10)
        self.farmer_form_frame.pack(side='right', fill='y', padx=(5, 0))
        
        self.create_farmer_form()
        
        # Load farmers
        self.refresh_farmers()
    
    def create_farmer_form(self):
        """Create farmer form"""
        # Form fields
        fields_frame = ttk.Frame(self.farmer_form_frame)
        fields_frame.pack(fill='both', expand=True)
        
        # Name
        ttk.Label(fields_frame, text="Nombre *:").pack(anchor='w', pady=(0, 5))
        self.farmer_name_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.farmer_name_var, 
                 style='Custom.TEntry', width=30).pack(fill='x', pady=(0, 10))
        
        # Email
        ttk.Label(fields_frame, text="Email:").pack(anchor='w', pady=(0, 5))
        self.farmer_email_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.farmer_email_var, 
                 style='Custom.TEntry', width=30).pack(fill='x', pady=(0, 10))
        
        # Phone
        ttk.Label(fields_frame, text="Teléfono:").pack(anchor='w', pady=(0, 5))
        self.farmer_phone_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.farmer_phone_var, 
                 style='Custom.TEntry', width=30).pack(fill='x', pady=(0, 10))
        
        # Address
        ttk.Label(fields_frame, text="Dirección:").pack(anchor='w', pady=(0, 5))
        self.farmer_address_text = tk.Text(fields_frame, height=4, width=30, 
                                         font=('Segoe UI', 10), wrap=tk.WORD)
        self.farmer_address_text.pack(fill='x', pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(fields_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        self.save_farmer_btn = ttk.Button(buttons_frame, text="💾 Guardar", 
                                        style='Primary.TButton',
                                        command=self.save_farmer)
        self.save_farmer_btn.pack(side='left', padx=(0, 5))
        
        self.edit_farmer_btn = ttk.Button(buttons_frame, text="✏️ Editar", 
                                        style='Secondary.TButton',
                                        command=self.edit_farmer, state='disabled')
        self.edit_farmer_btn.pack(side='left', padx=(0, 5))
        
        ttk.Button(buttons_frame, text="🗑️ Limpiar", 
                  style='Secondary.TButton',
                  command=self.clear_farmer_form).pack(side='left')
    
    def create_products_management(self, parent):
        """Create products management interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Gestión de Productos", style='Heading.TLabel').pack(side='left')
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="➕ Nuevo Producto", 
                  style='Primary.TButton',
                  command=self.show_product_form).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_products).pack(side='left')
        
        # Filter frame
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filtrar por Agricultor:").pack(side='left')
        self.product_farmer_filter = ttk.Combobox(filter_frame, style='Custom.TCombobox', 
                                                state='readonly', width=30)
        self.product_farmer_filter.pack(side='left', padx=(5, 10))
        self.product_farmer_filter.bind('<<ComboboxSelected>>', self.filter_products_by_farmer)
        
        ttk.Label(filter_frame, text="Buscar:").pack(side='left', padx=(10, 0))
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace('w', self.filter_products)
        ttk.Entry(filter_frame, textvariable=self.product_search_var, 
                 style='Custom.TEntry', width=20).pack(side='left', padx=(5, 0))
        
        # Products list
        products_frame = ttk.LabelFrame(parent, text="Lista de Productos", padding=10)
        products_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Products treeview
        columns = ('ID', 'Producto', 'Categoría', 'Cantidad', 'Precio/Unidad', 'Agricultor', 'Vencimiento')
        self.products_tree = ttk.Treeview(products_frame, columns=columns, show='headings', 
                                        style='Custom.Treeview', height=20)
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            if col == 'ID':
                self.products_tree.column(col, width=50, minwidth=50)
            elif col in ['Producto', 'Agricultor']:
                self.products_tree.column(col, width=150, minwidth=120)
            elif col in ['Categoría', 'Cantidad']:
                self.products_tree.column(col, width=100, minwidth=80)
            else:
                self.products_tree.column(col, width=120, minwidth=100)
        
        # Scrollbars for products tree
        products_scrollbar_y = ttk.Scrollbar(products_frame, orient='vertical', command=self.products_tree.yview)
        products_scrollbar_x = ttk.Scrollbar(products_frame, orient='horizontal', command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=products_scrollbar_y.set, xscrollcommand=products_scrollbar_x.set)
        
        self.products_tree.pack(side='left', fill='both', expand=True)
        products_scrollbar_y.pack(side='right', fill='y')
        products_scrollbar_x.pack(side='bottom', fill='x')
        
        # Load products
        self.refresh_products()
    
    def show_farmer_form(self):
        """Show farmer form for new entry"""
        self.clear_farmer_form()
        self.current_farmer_id = None
        self.save_farmer_btn.configure(text="💾 Guardar")
        self.edit_farmer_btn.configure(state='disabled')
    
    def show_product_form(self):
        """Show product form dialog"""
        self.product_form_window = tk.Toplevel(self.frame)
        self.product_form_window.title("Nuevo Producto")
        self.product_form_window.geometry("500x600")
        self.product_form_window.transient(self.frame)
        self.product_form_window.grab_set()
        
        # Form frame
        form_frame = ttk.Frame(self.product_form_window, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Farmer selection
        ttk.Label(form_frame, text="Agricultor *:").pack(anchor='w', pady=(0, 5))
        self.product_farmer_var = tk.StringVar()
        farmer_combo = ttk.Combobox(form_frame, textvariable=self.product_farmer_var, 
                                  style='Custom.TCombobox', state='readonly')
        farmer_combo.pack(fill='x', pady=(0, 10))
        
        # Load farmers for combobox
        try:
            farmers = self.db.get_farmers()
            farmer_values = [f"{farmer['id']} - {farmer['name']}" for farmer in farmers]
            farmer_combo['values'] = farmer_values
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando agricultores: {str(e)}")
        
        # Product name
        ttk.Label(form_frame, text="Nombre del Producto *:").pack(anchor='w', pady=(0, 5))
        self.product_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.product_name_var, 
                 style='Custom.TEntry').pack(fill='x', pady=(0, 10))
        
        # Category
        ttk.Label(form_frame, text="Categoría *:").pack(anchor='w', pady=(0, 5))
        self.product_category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.product_category_var, 
                                    style='Custom.TCombobox')
        category_combo['values'] = ['Verduras', 'Frutas', 'Granos', 'Legumbres', 'Hierbas', 'Otros']
        category_combo.pack(fill='x', pady=(0, 10))
        
        # Quantity and unit
        quantity_frame = ttk.Frame(form_frame)
        quantity_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(quantity_frame, text="Cantidad *:").pack(anchor='w')
        qty_unit_frame = ttk.Frame(quantity_frame)
        qty_unit_frame.pack(fill='x', pady=(5, 0))
        
        self.product_quantity_var = tk.StringVar()
        ttk.Entry(qty_unit_frame, textvariable=self.product_quantity_var, 
                 style='Custom.TEntry', width=15).pack(side='left')
        
        self.product_unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(qty_unit_frame, textvariable=self.product_unit_var, 
                                style='Custom.TCombobox', width=15)
        unit_combo['values'] = ['kg', 'libras', 'unidades', 'cajas', 'sacos', 'litros']
        unit_combo.pack(side='left', padx=(10, 0))
        
        # Price per unit
        ttk.Label(form_frame, text="Precio por Unidad *:").pack(anchor='w', pady=(0, 5))
        self.product_price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.product_price_var, 
                 style='Custom.TEntry').pack(fill='x', pady=(0, 10))
        
        # Dates
        dates_frame = ttk.Frame(form_frame)
        dates_frame.pack(fill='x', pady=(0, 10))
        
        # Harvest date
        date_frame1 = ttk.Frame(dates_frame)
        date_frame1.pack(fill='x', pady=(0, 5))
        ttk.Label(date_frame1, text="Fecha de Cosecha:").pack(side='left')
        self.product_harvest_date_var = tk.StringVar()
        ttk.Entry(date_frame1, textvariable=self.product_harvest_date_var, 
                 style='Custom.TEntry', width=12).pack(side='right')
        ttk.Label(date_frame1, text="(YYYY-MM-DD)").pack(side='right', padx=(0, 5))
        
        # Expiry date
        date_frame2 = ttk.Frame(dates_frame)
        date_frame2.pack(fill='x')
        ttk.Label(date_frame2, text="Fecha de Vencimiento:").pack(side='left')
        self.product_expiry_date_var = tk.StringVar()
        ttk.Entry(date_frame2, textvariable=self.product_expiry_date_var, 
                 style='Custom.TEntry', width=12).pack(side='right')
        ttk.Label(date_frame2, text="(YYYY-MM-DD)").pack(side='right', padx=(0, 5))
        
        # Quality grade
        ttk.Label(form_frame, text="Grado de Calidad:").pack(anchor='w', pady=(0, 5))
        self.product_quality_var = tk.StringVar()
        quality_combo = ttk.Combobox(form_frame, textvariable=self.product_quality_var, 
                                   style='Custom.TCombobox')
        quality_combo['values'] = ['Excelente', 'Buena', 'Regular', 'Básica']
        quality_combo.pack(fill='x', pady=(0, 10))
        
        # Description
        ttk.Label(form_frame, text="Descripción:").pack(anchor='w', pady=(0, 5))
        self.product_description_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), wrap=tk.WORD)
        self.product_description_text.pack(fill='x', pady=(0, 10))
        
        # Buttons
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(buttons_frame, text="💾 Guardar Producto", 
                  style='Primary.TButton',
                  command=self.save_product).pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                  style='Secondary.TButton',
                  command=self.product_form_window.destroy).pack(side='left')
    
    def save_farmer(self):
        """Save farmer data"""
        try:
            # Validate required fields
            if not self.farmer_name_var.get().strip():
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            # Validate email if provided
            email = self.farmer_email_var.get().strip()
            if email and not Validator.is_valid_email(email):
                messagebox.showerror("Error", "El formato del email no es válido")
                return
            
            # Prepare farmer data
            farmer_data = {
                'name': self.farmer_name_var.get().strip(),
                'email': email if email else None,
                'phone': self.farmer_phone_var.get().strip() if self.farmer_phone_var.get().strip() else None,
                'address': self.farmer_address_text.get(1.0, tk.END).strip() if self.farmer_address_text.get(1.0, tk.END).strip() else None
            }
            
            if self.current_farmer_id:
                # Update existing farmer
                self.db.update_farmer(self.current_farmer_id, farmer_data)
                messagebox.showinfo("Éxito", "Agricultor actualizado correctamente")
            else:
                # Add new farmer
                farmer_id = self.db.add_farmer(farmer_data)
                messagebox.showinfo("Éxito", f"Agricultor agregado con ID: {farmer_id}")
            
            self.refresh_farmers()
            self.clear_farmer_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando agricultor: {str(e)}")
    
    def save_product(self):
        """Save product data"""
        try:
            # Validate required fields
            if not self.product_farmer_var.get():
                messagebox.showerror("Error", "Debe seleccionar un agricultor")
                return
            
            if not self.product_name_var.get().strip():
                messagebox.showerror("Error", "El nombre del producto es obligatorio")
                return
            
            if not self.product_category_var.get().strip():
                messagebox.showerror("Error", "La categoría es obligatoria")
                return
            
            if not self.product_quantity_var.get().strip():
                messagebox.showerror("Error", "La cantidad es obligatoria")
                return
            
            if not self.product_unit_var.get().strip():
                messagebox.showerror("Error", "La unidad es obligatoria")
                return
            
            if not self.product_price_var.get().strip():
                messagebox.showerror("Error", "El precio es obligatorio")
                return
            
            # Validate numeric fields
            try:
                quantity = float(self.product_quantity_var.get())
                price = float(self.product_price_var.get())
                
                if quantity <= 0 or price <= 0:
                    raise ValueError("Los valores deben ser positivos")
                    
            except ValueError as e:
                messagebox.showerror("Error", "Cantidad y precio deben ser números válidos y positivos")
                return
            
            # Get farmer ID
            farmer_selection = self.product_farmer_var.get()
            farmer_id = int(farmer_selection.split(' - ')[0])
            
            # Prepare product data
            product_data = {
                'farmer_id': farmer_id,
                'name': self.product_name_var.get().strip(),
                'category': self.product_category_var.get().strip(),
                'quantity': quantity,
                'unit': self.product_unit_var.get().strip(),
                'price_per_unit': price,
                'harvest_date': self.product_harvest_date_var.get().strip() if self.product_harvest_date_var.get().strip() else None,
                'expiry_date': self.product_expiry_date_var.get().strip() if self.product_expiry_date_var.get().strip() else None,
                'quality_grade': self.product_quality_var.get().strip() if self.product_quality_var.get().strip() else None,
                'description': self.product_description_text.get(1.0, tk.END).strip() if self.product_description_text.get(1.0, tk.END).strip() else None
            }
            
            # Validate dates if provided
            for date_field in ['harvest_date', 'expiry_date']:
                if product_data[date_field]:
                    if not Validator.is_valid_date(product_data[date_field]):
                        messagebox.showerror("Error", f"Formato de fecha inválido para {date_field.replace('_', ' ')}")
                        return
            
            product_id = self.db.add_product(product_data)
            messagebox.showinfo("Éxito", f"Producto agregado con ID: {product_id}")
            
            self.product_form_window.destroy()
            self.refresh_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando producto: {str(e)}")
    
    def refresh_farmers(self):
        """Refresh farmers list"""
        try:
            # Clear tree
            for item in self.farmers_tree.get_children():
                self.farmers_tree.delete(item)
            
            # Load farmers
            farmers = self.db.get_farmers()
            for farmer in farmers:
                self.farmers_tree.insert('', 'end', values=(
                    farmer['id'],
                    farmer['name'],
                    farmer['email'] or '',
                    farmer['phone'] or '',
                    farmer['registration_date'][:10] if farmer['registration_date'] else ''
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando agricultores: {str(e)}")
    
    def refresh_products(self):
        """Refresh products list"""
        try:
            # Clear tree
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Update farmer filter combobox
            farmers = self.db.get_farmers()
            farmer_values = ['Todos'] + [f"{farmer['id']} - {farmer['name']}" for farmer in farmers]
            self.product_farmer_filter['values'] = farmer_values
            if not self.product_farmer_filter.get():
                self.product_farmer_filter.set('Todos')
            
            # Load products
            products = self.db.get_products()
            for product in products:
                self.products_tree.insert('', 'end', values=(
                    product['id'],
                    product['name'],
                    product['category'],
                    f"{product['quantity']} {product['unit']}",
                    f"${product['price_per_unit']:.2f}",
                    product['farmer_name'],
                    product['expiry_date'] or 'N/A'
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {str(e)}")
    
    def on_farmer_select(self, event):
        """Handle farmer selection"""
        selection = self.farmers_tree.selection()
        if selection:
            item = self.farmers_tree.item(selection[0])
            farmer_data = item['values']
            
            if farmer_data:
                self.current_farmer_id = farmer_data[0]
                self.farmer_name_var.set(farmer_data[1])
                self.farmer_email_var.set(farmer_data[2])
                self.farmer_phone_var.set(farmer_data[3])
                
                # Load full farmer data for address
                try:
                    farmers = self.db.get_farmers()
                    selected_farmer = next((f for f in farmers if f['id'] == self.current_farmer_id), None)
                    if selected_farmer:
                        self.farmer_address_text.delete(1.0, tk.END)
                        if selected_farmer['address']:
                            self.farmer_address_text.insert(1.0, selected_farmer['address'])
                except Exception as e:
                    print(f"Error loading farmer address: {e}")
                
                self.save_farmer_btn.configure(text="💾 Actualizar")
                self.edit_farmer_btn.configure(state='normal')
    
    def edit_farmer(self):
        """Enable farmer editing"""
        if self.current_farmer_id:
            self.save_farmer_btn.configure(text="💾 Actualizar")
    
    def clear_farmer_form(self):
        """Clear farmer form"""
        self.current_farmer_id = None
        self.farmer_name_var.set('')
        self.farmer_email_var.set('')
        self.farmer_phone_var.set('')
        self.farmer_address_text.delete(1.0, tk.END)
        self.save_farmer_btn.configure(text="💾 Guardar")
        self.edit_farmer_btn.configure(state='disabled')
    
    def filter_farmers(self, *args):
        """Filter farmers based on search"""
        search_term = self.farmer_search_var.get().lower()
        
        # Clear current items
        for item in self.farmers_tree.get_children():
            self.farmers_tree.delete(item)
        
        try:
            farmers = self.db.get_farmers()
            for farmer in farmers:
                # Check if search term matches any field
                if (search_term in farmer['name'].lower() or 
                    (farmer['email'] and search_term in farmer['email'].lower()) or
                    (farmer['phone'] and search_term in farmer['phone'].lower())):
                    
                    self.farmers_tree.insert('', 'end', values=(
                        farmer['id'],
                        farmer['name'],
                        farmer['email'] or '',
                        farmer['phone'] or '',
                        farmer['registration_date'][:10] if farmer['registration_date'] else ''
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Error filtrando agricultores: {str(e)}")
    
    def filter_products_by_farmer(self, event=None):
        """Filter products by selected farmer"""
        self.filter_products()
    
    def filter_products(self, *args):
        """Filter products based on farmer and search term"""
        farmer_filter = self.product_farmer_filter.get()
        search_term = self.product_search_var.get().lower()
        
        # Clear current items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        try:
            products = self.db.get_products()
            
            for product in products:
                # Apply farmer filter
                if farmer_filter and farmer_filter != 'Todos':
                    farmer_id_from_filter = int(farmer_filter.split(' - ')[0])
                    if product['farmer_id'] != farmer_id_from_filter:
                        continue
                
                # Apply search filter
                if search_term:
                    if not (search_term in product['name'].lower() or 
                           search_term in product['category'].lower() or
                           search_term in product['farmer_name'].lower()):
                        continue
                
                self.products_tree.insert('', 'end', values=(
                    product['id'],
                    product['name'],
                    product['category'],
                    f"{product['quantity']} {product['unit']}",
                    f"${product['price_per_unit']:.2f}",
                    product['farmer_name'],
                    product['expiry_date'] or 'N/A'
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error filtrando productos: {str(e)}")
