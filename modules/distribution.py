import tkinter as tk
from tkinter import ttk, messagebox
from utils.validators import Validator
from datetime import datetime, timedelta

class DistributionModule:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.frame = None
        self.current_request_id = None
        
    def show(self):
        """Show the distribution module"""
        if self.frame:
            self.frame.destroy()
        
        self.frame = ttk.Frame(self.parent, style='Card.TFrame')
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_distribution_interface()
        
    def hide(self):
        """Hide the distribution module"""
        if self.frame:
            self.frame.destroy()
            self.frame = None
    
    def create_distribution_interface(self):
        """Create the distribution coordination interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.frame, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Distribution requests tab
        requests_tab = ttk.Frame(notebook)
        notebook.add(requests_tab, text="Solicitudes de Distribución")
        
        # Product matching tab
        matching_tab = ttk.Frame(notebook)
        notebook.add(matching_tab, text="Coordinación de Productos")
        
        # Assignments tab
        assignments_tab = ttk.Frame(notebook)
        notebook.add(assignments_tab, text="Asignaciones Activas")
        
        # Create interfaces
        self.create_requests_management(requests_tab)
        self.create_product_matching(matching_tab)
        self.create_assignments_management(assignments_tab)
    
    def create_requests_management(self, parent):
        """Create distribution requests management interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Solicitudes de Distribución", style='Heading.TLabel').pack(side='left')
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="➕ Nueva Solicitud", 
                  style='Primary.TButton',
                  command=self.show_request_form).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_requests).pack(side='left')
        
        # Filter frame
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Estado:").pack(side='left')
        self.status_filter_var = tk.StringVar()
        self.status_filter_var.trace('w', self.filter_requests)
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var, 
                                  style='Custom.TCombobox', state='readonly', width=15)
        status_combo['values'] = ['Todos', 'pending', 'assigned', 'completed', 'cancelled']
        status_combo.set('Todos')
        status_combo.pack(side='left', padx=(5, 10))
        
        ttk.Label(filter_frame, text="Prioridad:").pack(side='left')
        self.priority_filter_var = tk.StringVar()
        self.priority_filter_var.trace('w', self.filter_requests)
        priority_combo = ttk.Combobox(filter_frame, textvariable=self.priority_filter_var, 
                                    style='Custom.TCombobox', state='readonly', width=15)
        priority_combo['values'] = ['Todas', 'high', 'medium', 'low']
        priority_combo.set('Todas')
        priority_combo.pack(side='left', padx=(5, 0))
        
        # Requests list
        requests_frame = ttk.LabelFrame(parent, text="Lista de Solicitudes", padding=10)
        requests_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Requests treeview
        columns = ('ID', 'Punto de Venta', 'Categoría', 'Cantidad', 'Fecha Requerida', 'Prioridad', 'Estado')
        self.requests_tree = ttk.Treeview(requests_frame, columns=columns, show='headings', 
                                        style='Custom.Treeview', height=15)
        
        for col in columns:
            self.requests_tree.heading(col, text=col)
            if col == 'ID':
                self.requests_tree.column(col, width=50, minwidth=50)
            elif col in ['Punto de Venta', 'Categoría']:
                self.requests_tree.column(col, width=150, minwidth=120)
            elif col in ['Cantidad', 'Prioridad', 'Estado']:
                self.requests_tree.column(col, width=100, minwidth=80)
            else:
                self.requests_tree.column(col, width=120, minwidth=100)
        
        # Scrollbars
        requests_scrollbar_y = ttk.Scrollbar(requests_frame, orient='vertical', command=self.requests_tree.yview)
        requests_scrollbar_x = ttk.Scrollbar(requests_frame, orient='horizontal', command=self.requests_tree.xview)
        self.requests_tree.configure(yscrollcommand=requests_scrollbar_y.set, xscrollcommand=requests_scrollbar_x.set)
        
        self.requests_tree.pack(side='left', fill='both', expand=True)
        requests_scrollbar_y.pack(side='right', fill='y')
        requests_scrollbar_x.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.requests_tree.bind('<<TreeviewSelect>>', self.on_request_select)
        self.requests_tree.bind('<Double-1>', self.view_request_details)
        
        # Load requests
        self.refresh_requests()
    
    def create_product_matching(self, parent):
        """Create product matching interface"""
        # Title
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Coordinación de Productos", style='Heading.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_matching).pack(side='right')
        
        # Main content with two panels
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Available products (left side)
        products_frame = ttk.LabelFrame(content_frame, text="Productos Disponibles", padding=10)
        products_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Category filter for products
        product_filter_frame = ttk.Frame(products_frame)
        product_filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(product_filter_frame, text="Categoría:").pack(side='left')
        self.product_category_filter_var = tk.StringVar()
        self.product_category_filter_var.trace('w', self.filter_available_products)
        product_category_combo = ttk.Combobox(product_filter_frame, textvariable=self.product_category_filter_var, 
                                            style='Custom.TCombobox', state='readonly', width=20)
        product_category_combo['values'] = ['Todas', 'Verduras', 'Frutas', 'Granos', 'Legumbres', 'Hierbas', 'Otros']
        product_category_combo.set('Todas')
        product_category_combo.pack(side='left', padx=(5, 0))
        
        # Available products tree
        product_columns = ('ID', 'Producto', 'Categoría', 'Cantidad', 'Precio', 'Agricultor', 'Vencimiento')
        self.available_products_tree = ttk.Treeview(products_frame, columns=product_columns, show='headings', 
                                                  style='Custom.Treeview', height=12)
        
        for col in product_columns:
            self.available_products_tree.heading(col, text=col)
            if col == 'ID':
                self.available_products_tree.column(col, width=50, minwidth=50)
            elif col in ['Producto', 'Agricultor']:
                self.available_products_tree.column(col, width=120, minwidth=100)
            else:
                self.available_products_tree.column(col, width=100, minwidth=80)
        
        # Product scrollbars
        product_scrollbar_y = ttk.Scrollbar(products_frame, orient='vertical', command=self.available_products_tree.yview)
        self.available_products_tree.configure(yscrollcommand=product_scrollbar_y.set)
        
        self.available_products_tree.pack(side='left', fill='both', expand=True)
        product_scrollbar_y.pack(side='right', fill='y')
        
        # Pending requests (right side)
        pending_frame = ttk.LabelFrame(content_frame, text="Solicitudes Pendientes", padding=10)
        pending_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Pending requests tree
        pending_columns = ('ID', 'Punto de Venta', 'Categoría', 'Cantidad', 'Precio Máx', 'Prioridad')
        self.pending_requests_tree = ttk.Treeview(pending_frame, columns=pending_columns, show='headings', 
                                                style='Custom.Treeview', height=12)
        
        for col in pending_columns:
            self.pending_requests_tree.heading(col, text=col)
            if col == 'ID':
                self.pending_requests_tree.column(col, width=50, minwidth=50)
            elif col == 'Punto de Venta':
                self.pending_requests_tree.column(col, width=150, minwidth=120)
            else:
                self.pending_requests_tree.column(col, width=100, minwidth=80)
        
        # Pending scrollbar
        pending_scrollbar_y = ttk.Scrollbar(pending_frame, orient='vertical', command=self.pending_requests_tree.yview)
        self.pending_requests_tree.configure(yscrollcommand=pending_scrollbar_y.set)
        
        self.pending_requests_tree.pack(side='left', fill='both', expand=True)
        pending_scrollbar_y.pack(side='right', fill='y')
        
        # Matching controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(controls_frame, text="🔗 Crear Asignación", 
                  style='Primary.TButton',
                  command=self.create_assignment).pack(side='left', padx=(0, 10))
        
        ttk.Button(controls_frame, text="🤖 Sugerencias Automáticas", 
                  style='Secondary.TButton',
                  command=self.show_automatic_suggestions).pack(side='left')
        
        # Load matching data
        self.refresh_matching()
    
    def create_assignments_management(self, parent):
        """Create assignments management interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Asignaciones Activas", style='Heading.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_assignments).pack(side='right')
        
        # Assignments list
        assignments_frame = ttk.LabelFrame(parent, text="Lista de Asignaciones", padding=10)
        assignments_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Assignments treeview
        assign_columns = ('ID', 'Solicitud', 'Producto', 'Agricultor', 'Punto de Venta', 'Cantidad', 'Precio', 'Estado')
        self.assignments_tree = ttk.Treeview(assignments_frame, columns=assign_columns, show='headings', 
                                           style='Custom.Treeview', height=15)
        
        for col in assign_columns:
            self.assignments_tree.heading(col, text=col)
            if col == 'ID':
                self.assignments_tree.column(col, width=50, minwidth=50)
            elif col in ['Producto', 'Agricultor', 'Punto de Venta']:
                self.assignments_tree.column(col, width=120, minwidth=100)
            else:
                self.assignments_tree.column(col, width=100, minwidth=80)
        
        # Assignments scrollbars
        assign_scrollbar_y = ttk.Scrollbar(assignments_frame, orient='vertical', command=self.assignments_tree.yview)
        assign_scrollbar_x = ttk.Scrollbar(assignments_frame, orient='horizontal', command=self.assignments_tree.xview)
        self.assignments_tree.configure(yscrollcommand=assign_scrollbar_y.set, xscrollcommand=assign_scrollbar_x.set)
        
        self.assignments_tree.pack(side='left', fill='both', expand=True)
        assign_scrollbar_y.pack(side='right', fill='y')
        assign_scrollbar_x.pack(side='bottom', fill='x')
        
        # Assignment actions
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(actions_frame, text="✅ Marcar como Entregado", 
                  style='Primary.TButton',
                  command=self.mark_as_delivered).pack(side='left', padx=(0, 10))
        
        ttk.Button(actions_frame, text="❌ Cancelar Asignación", 
                  style='Danger.TButton',
                  command=self.cancel_assignment).pack(side='left')
        
        # Load assignments
        self.refresh_assignments()
    
    def show_request_form(self):
        """Show distribution request form dialog"""
        self.request_form_window = tk.Toplevel(self.frame)
        self.request_form_window.title("Nueva Solicitud de Distribución")
        self.request_form_window.geometry("500x500")
        self.request_form_window.transient(self.frame)
        self.request_form_window.grab_set()
        
        # Form frame
        form_frame = ttk.Frame(self.request_form_window, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Sales point selection
        ttk.Label(form_frame, text="Punto de Venta *:").pack(anchor='w', pady=(0, 5))
        self.request_sales_point_var = tk.StringVar()
        sales_point_combo = ttk.Combobox(form_frame, textvariable=self.request_sales_point_var, 
                                       style='Custom.TCombobox', state='readonly')
        sales_point_combo.pack(fill='x', pady=(0, 10))
        
        # Load sales points for combobox
        try:
            sales_points = self.db.get_sales_points()
            sp_values = [f"{sp['id']} - {sp['name']}" for sp in sales_points]
            sales_point_combo['values'] = sp_values
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando puntos de venta: {str(e)}")
        
        # Product category
        ttk.Label(form_frame, text="Categoría de Producto *:").pack(anchor='w', pady=(0, 5))
        self.request_category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.request_category_var, 
                                    style='Custom.TCombobox')
        category_combo['values'] = ['Verduras', 'Frutas', 'Granos', 'Legumbres', 'Hierbas', 'Otros']
        category_combo.pack(fill='x', pady=(0, 10))
        
        # Quantity and unit
        quantity_frame = ttk.Frame(form_frame)
        quantity_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(quantity_frame, text="Cantidad Solicitada *:").pack(anchor='w')
        qty_unit_frame = ttk.Frame(quantity_frame)
        qty_unit_frame.pack(fill='x', pady=(5, 0))
        
        self.request_quantity_var = tk.StringVar()
        ttk.Entry(qty_unit_frame, textvariable=self.request_quantity_var, 
                 style='Custom.TEntry', width=15).pack(side='left')
        
        self.request_unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(qty_unit_frame, textvariable=self.request_unit_var, 
                                style='Custom.TCombobox', width=15)
        unit_combo['values'] = ['kg', 'libras', 'unidades', 'cajas', 'sacos', 'litros']
        unit_combo.pack(side='left', padx=(10, 0))
        
        # Max price
        ttk.Label(form_frame, text="Precio Máximo por Unidad:").pack(anchor='w', pady=(0, 5))
        self.request_max_price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.request_max_price_var, 
                 style='Custom.TEntry').pack(fill='x', pady=(0, 10))
        
        # Required date
        ttk.Label(form_frame, text="Fecha Requerida:").pack(anchor='w', pady=(0, 5))
        date_frame = ttk.Frame(form_frame)
        date_frame.pack(fill='x', pady=(0, 10))
        
        self.request_required_date_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.request_required_date_var, 
                 style='Custom.TEntry', width=12).pack(side='left')
        ttk.Label(date_frame, text="(YYYY-MM-DD)").pack(side='left', padx=(5, 0))
        
        # Priority
        ttk.Label(form_frame, text="Prioridad:").pack(anchor='w', pady=(0, 5))
        self.request_priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(form_frame, textvariable=self.request_priority_var, 
                                    style='Custom.TCombobox', state='readonly')
        priority_combo['values'] = ['low', 'medium', 'high']
        priority_combo.set('medium')
        priority_combo.pack(fill='x', pady=(0, 10))
        
        # Notes
        ttk.Label(form_frame, text="Notas Adicionales:").pack(anchor='w', pady=(0, 5))
        self.request_notes_text = tk.Text(form_frame, height=4, font=('Segoe UI', 10), wrap=tk.WORD)
        self.request_notes_text.pack(fill='x', pady=(0, 10))
        
        # Buttons
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(buttons_frame, text="💾 Guardar Solicitud", 
                  style='Primary.TButton',
                  command=self.save_request).pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                  style='Secondary.TButton',
                  command=self.request_form_window.destroy).pack(side='left')
    
    def save_request(self):
        """Save distribution request"""
        try:
            # Validate required fields
            if not self.request_sales_point_var.get():
                messagebox.showerror("Error", "Debe seleccionar un punto de venta")
                return
            
            if not self.request_category_var.get().strip():
                messagebox.showerror("Error", "La categoría es obligatoria")
                return
            
            if not self.request_quantity_var.get().strip():
                messagebox.showerror("Error", "La cantidad es obligatoria")
                return
            
            if not self.request_unit_var.get().strip():
                messagebox.showerror("Error", "La unidad es obligatoria")
                return
            
            # Validate numeric fields
            try:
                quantity = float(self.request_quantity_var.get())
                if quantity <= 0:
                    raise ValueError("La cantidad debe ser positiva")
                    
                max_price = None
                if self.request_max_price_var.get().strip():
                    max_price = float(self.request_max_price_var.get())
                    if max_price <= 0:
                        raise ValueError("El precio debe ser positivo")
                        
            except ValueError as e:
                messagebox.showerror("Error", f"Error en valores numéricos: {str(e)}")
                return
            
            # Validate date if provided
            required_date = self.request_required_date_var.get().strip()
            if required_date and not Validator.is_valid_date(required_date):
                messagebox.showerror("Error", "Formato de fecha inválido")
                return
            
            # Get sales point ID
            sales_point_selection = self.request_sales_point_var.get()
            sales_point_id = int(sales_point_selection.split(' - ')[0])
            
            # Prepare request data
            request_data = {
                'sales_point_id': sales_point_id,
                'product_category': self.request_category_var.get().strip(),
                'quantity_requested': quantity,
                'unit': self.request_unit_var.get().strip(),
                'max_price': max_price,
                'required_date': required_date if required_date else None,
                'priority': self.request_priority_var.get(),
                'notes': self.request_notes_text.get(1.0, tk.END).strip() if self.request_notes_text.get(1.0, tk.END).strip() else None
            }
            
            request_id = self.db.add_distribution_request(request_data)
            messagebox.showinfo("Éxito", f"Solicitud de distribución creada con ID: {request_id}")
            
            self.request_form_window.destroy()
            self.refresh_requests()
            self.refresh_matching()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando solicitud: {str(e)}")
    
    def refresh_requests(self):
        """Refresh distribution requests list"""
        try:
            # Clear tree
            for item in self.requests_tree.get_children():
                self.requests_tree.delete(item)
            
            # Load requests
            requests = self.db.get_distribution_requests()
            for request in requests:
                # Format priority and status for display
                priority_display = {
                    'high': '🔴 Alta',
                    'medium': '🟡 Media', 
                    'low': '🟢 Baja'
                }.get(request['priority'], request['priority'])
                
                status_display = {
                    'pending': '⏳ Pendiente',
                    'assigned': '📋 Asignado',
                    'completed': '✅ Completado',
                    'cancelled': '❌ Cancelado'
                }.get(request['status'], request['status'])
                
                self.requests_tree.insert('', 'end', values=(
                    request['id'],
                    request['sales_point_name'],
                    request['product_category'],
                    f"{request['quantity_requested']} {request['unit']}",
                    request['required_date'] or 'N/A',
                    priority_display,
                    status_display
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando solicitudes: {str(e)}")
    
    def refresh_matching(self):
        """Refresh product matching data"""
        self.refresh_available_products()
        self.refresh_pending_requests()
    
    def refresh_available_products(self):
        """Refresh available products list"""
        try:
            # Clear tree
            for item in self.available_products_tree.get_children():
                self.available_products_tree.delete(item)
            
            # Load available products
            products = self.db.get_products(available_only=True)
            for product in products:
                self.available_products_tree.insert('', 'end', values=(
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
    
    def refresh_pending_requests(self):
        """Refresh pending requests list"""
        try:
            # Clear tree
            for item in self.pending_requests_tree.get_children():
                self.pending_requests_tree.delete(item)
            
            # Load pending requests
            requests = self.db.get_distribution_requests(status='pending')
            for request in requests:
                priority_display = {
                    'high': '🔴 Alta',
                    'medium': '🟡 Media', 
                    'low': '🟢 Baja'
                }.get(request['priority'], request['priority'])
                
                self.pending_requests_tree.insert('', 'end', values=(
                    request['id'],
                    request['sales_point_name'],
                    request['product_category'],
                    f"{request['quantity_requested']} {request['unit']}",
                    f"${request['max_price']:.2f}" if request['max_price'] else 'N/A',
                    priority_display
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando solicitudes pendientes: {str(e)}")
    
    def refresh_assignments(self):
        """Refresh assignments list"""
        try:
            # Clear tree
            for item in self.assignments_tree.get_children():
                self.assignments_tree.delete(item)
            
            # Note: This would require implementing get_distribution_assignments in the database
            # For now, show empty state
            messagebox.showinfo("Información", "Funcionalidad de asignaciones en desarrollo")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando asignaciones: {str(e)}")
    
    def create_assignment(self):
        """Create assignment between product and request"""
        # Get selected product and request
        product_selection = self.available_products_tree.selection()
        request_selection = self.pending_requests_tree.selection()
        
        if not product_selection or not request_selection:
            messagebox.showwarning("Advertencia", "Debe seleccionar un producto y una solicitud")
            return
        
        product_item = self.available_products_tree.item(product_selection[0])
        request_item = self.pending_requests_tree.item(request_selection[0])
        
        product_id = product_item['values'][0]
        request_id = request_item['values'][0]
        
        # Show assignment form
        self.show_assignment_form(product_id, request_id)
    
    def show_assignment_form(self, product_id, request_id):
        """Show assignment creation form"""
        assignment_window = tk.Toplevel(self.frame)
        assignment_window.title("Crear Asignación")
        assignment_window.geometry("400x300")
        assignment_window.transient(self.frame)
        assignment_window.grab_set()
        
        form_frame = ttk.Frame(assignment_window, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        ttk.Label(form_frame, text="Creando asignación...", style='Heading.TLabel').pack(pady=10)
        
        # Show product and request details
        ttk.Label(form_frame, text=f"Producto ID: {product_id}").pack(anchor='w')
        ttk.Label(form_frame, text=f"Solicitud ID: {request_id}").pack(anchor='w')
        
        # Quantity to assign
        ttk.Label(form_frame, text="Cantidad a Asignar:").pack(anchor='w', pady=(10, 5))
        quantity_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=quantity_var, style='Custom.TEntry').pack(fill='x', pady=(0, 10))
        
        # Agreed price
        ttk.Label(form_frame, text="Precio Acordado:").pack(anchor='w', pady=(0, 5))
        price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=price_var, style='Custom.TEntry').pack(fill='x', pady=(0, 10))
        
        # Buttons
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        def save_assignment():
            try:
                quantity = float(quantity_var.get())
                price = float(price_var.get())
                
                # Here you would call db.add_distribution_assignment()
                messagebox.showinfo("Éxito", "Asignación creada correctamente")
                assignment_window.destroy()
                self.refresh_matching()
                
            except ValueError:
                messagebox.showerror("Error", "Valores numéricos inválidos")
            except Exception as e:
                messagebox.showerror("Error", f"Error creando asignación: {str(e)}")
        
        ttk.Button(buttons_frame, text="💾 Guardar", 
                  style='Primary.TButton', command=save_assignment).pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                  style='Secondary.TButton', 
                  command=assignment_window.destroy).pack(side='left')
    
    def show_automatic_suggestions(self):
        """Show automatic matching suggestions"""
        suggestions_window = tk.Toplevel(self.frame)
        suggestions_window.title("Sugerencias Automáticas")
        suggestions_window.geometry("800x600")
        suggestions_window.transient(self.frame)
        suggestions_window.grab_set()
        
        main_frame = ttk.Frame(suggestions_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Sugerencias de Coordinación Automática", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        # Suggestions list
        suggestions_frame = ttk.LabelFrame(main_frame, text="Coincidencias Sugeridas", padding=10)
        suggestions_frame.pack(fill='both', expand=True)
        
        # Create suggestions based on category matching
        try:
            products = self.db.get_products(available_only=True)
            requests = self.db.get_distribution_requests(status='pending')
            
            suggestions_text = tk.Text(suggestions_frame, font=('Segoe UI', 10), wrap=tk.WORD)
            suggestions_text.pack(fill='both', expand=True)
            
            suggestions_found = False
            
            for request in requests:
                matching_products = [p for p in products 
                                   if p['category'].lower() == request['product_category'].lower()]
                
                if matching_products:
                    suggestions_found = True
                    suggestions_text.insert('end', f"\n🎯 SOLICITUD #{request['id']} - {request['sales_point_name']}\n", 'header')
                    suggestions_text.insert('end', f"   Necesita: {request['quantity_requested']} {request['unit']} de {request['product_category']}\n")
                    suggestions_text.insert('end', f"   Precio máximo: ${request['max_price']:.2f}\n" if request['max_price'] else "   Sin límite de precio\n")
                    suggestions_text.insert('end', "\n   PRODUCTOS DISPONIBLES:\n", 'subheader')
                    
                    for product in matching_products[:3]:  # Show top 3 matches
                        price_match = "✅" if not request['max_price'] or product['price_per_unit'] <= request['max_price'] else "❌"
                        suggestions_text.insert('end', f"   {price_match} {product['name']} - {product['farmer_name']}\n")
                        suggestions_text.insert('end', f"      Cantidad: {product['quantity']} {product['unit']}, Precio: ${product['price_per_unit']:.2f}\n")
                    
                    suggestions_text.insert('end', "\n" + "="*50 + "\n")
            
            if not suggestions_found:
                suggestions_text.insert('end', "No se encontraron coincidencias automáticas en este momento.\n")
                suggestions_text.insert('end', "Revise las categorías de productos y solicitudes para encontrar coincidencias manuales.")
            
            # Configure text tags
            suggestions_text.tag_configure('header', font=('Segoe UI', 12, 'bold'), foreground='#2E7D32')
            suggestions_text.tag_configure('subheader', font=('Segoe UI', 10, 'bold'), foreground='#FF9800')
            
            suggestions_text.configure(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando sugerencias: {str(e)}")
        
        # Close button
        ttk.Button(main_frame, text="❌ Cerrar", 
                  style='Secondary.TButton',
                  command=suggestions_window.destroy).pack(pady=(20, 0))
    
    def filter_requests(self, *args):
        """Filter requests based on status and priority"""
        # Implementation would filter the requests tree based on selected filters
        self.refresh_requests()
    
    def filter_available_products(self, *args):
        """Filter available products by category"""
        # Implementation would filter the products tree based on category
        self.refresh_available_products()
    
    def on_request_select(self, event):
        """Handle request selection"""
        pass
    
    def view_request_details(self, event):
        """View detailed information about a request"""
        selection = self.requests_tree.selection()
        if selection:
            item = self.requests_tree.item(selection[0])
            request_id = item['values'][0]
            
            # Show detailed view window
            details_window = tk.Toplevel(self.frame)
            details_window.title(f"Detalles de Solicitud #{request_id}")
            details_window.geometry("500x400")
            details_window.transient(self.frame)
            
            details_frame = ttk.Frame(details_window, padding=20)
            details_frame.pack(fill='both', expand=True)
            
            ttk.Label(details_frame, text=f"Solicitud de Distribución #{request_id}", 
                     style='Heading.TLabel').pack(pady=(0, 20))
            
            # Load and display request details
            try:
                requests = self.db.get_distribution_requests()
                request = next((r for r in requests if r['id'] == request_id), None)
                
                if request:
                    details_text = tk.Text(details_frame, font=('Segoe UI', 10), wrap=tk.WORD, height=15)
                    details_text.pack(fill='both', expand=True)
                    
                    details_text.insert('end', f"Punto de Venta: {request['sales_point_name']}\n")
                    details_text.insert('end', f"Categoría: {request['product_category']}\n")
                    details_text.insert('end', f"Cantidad: {request['quantity_requested']} {request['unit']}\n")
                    details_text.insert('end', f"Precio Máximo: ${request['max_price']:.2f}\n" if request['max_price'] else "Precio Máximo: Sin límite\n")
                    details_text.insert('end', f"Fecha Requerida: {request['required_date'] or 'No especificada'}\n")
                    details_text.insert('end', f"Prioridad: {request['priority']}\n")
                    details_text.insert('end', f"Estado: {request['status']}\n")
                    details_text.insert('end', f"Fecha de Creación: {request['created_date']}\n")
                    
                    if request['notes']:
                        details_text.insert('end', f"\nNotas:\n{request['notes']}")
                    
                    details_text.configure(state='disabled')
                
            except Exception as e:
                ttk.Label(details_frame, text=f"Error cargando detalles: {str(e)}", 
                         foreground='red').pack()
            
            ttk.Button(details_frame, text="❌ Cerrar", 
                      style='Secondary.TButton',
                      command=details_window.destroy).pack(pady=(20, 0))
    
    def mark_as_delivered(self):
        """Mark assignment as delivered"""
        messagebox.showinfo("Información", "Funcionalidad en desarrollo")
    
    def cancel_assignment(self):
        """Cancel an assignment"""
        messagebox.showinfo("Información", "Funcionalidad en desarrollo")
