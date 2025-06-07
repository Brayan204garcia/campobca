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
        
        # Action buttons for requests
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(actions_frame, text="✏️ Editar Solicitud", 
                  style='Secondary.TButton',
                  command=self.edit_request).pack(side='left', padx=(0, 10))
        
        ttk.Button(actions_frame, text="❌ Cancelar Solicitud", 
                  style='Danger.TButton',
                  command=self.cancel_request).pack(side='left', padx=(0, 10))
        
        ttk.Button(actions_frame, text="📋 Ver Detalles", 
                  style='Info.TButton',
                  command=lambda: self.view_request_details()).pack(side='left', padx=(0, 10))
        
        ttk.Button(actions_frame, text="📊 Ver Total a Pagar", 
                  style='Primary.TButton',
                  command=self.show_payment_total).pack(side='left')
        
        # Requests list
        requests_frame = ttk.LabelFrame(parent, text="Lista de Solicitudes", padding=10)
        requests_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Requests treeview
        columns = ('ID', 'Punto de Venta', 'Productos', 'Cantidades', 'Fecha Requerida', 'Prioridad', 'Estado')
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
        
        # Create frame for tree and scrollbars
        tree_frame = ttk.Frame(assignments_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Assignments scrollbars
        assign_scrollbar_y = ttk.Scrollbar(tree_frame, orient='vertical', command=self.assignments_tree.yview)
        assign_scrollbar_x = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.assignments_tree.xview)
        self.assignments_tree.configure(yscrollcommand=assign_scrollbar_y.set, xscrollcommand=assign_scrollbar_x.set)
        
        # Grid layout for proper scrollbar positioning
        self.assignments_tree.grid(row=0, column=0, sticky='nsew')
        assign_scrollbar_y.grid(row=0, column=1, sticky='ns')
        assign_scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Assignment actions
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(actions_frame, text="✅ Marcar como Entregado", 
                  style='Primary.TButton',
                  command=self.mark_as_delivered).pack(side='left', padx=(0, 10))
        
        ttk.Button(actions_frame, text="📋 Ver Detalles", 
                  style='Secondary.TButton',
                  command=self.view_assignment_details).pack(side='left', padx=(0, 10))
        
        ttk.Button(actions_frame, text="✅ Completar Solicitud", 
                  style='Success.TButton',
                  command=self.complete_request).pack(side='left', padx=(0, 10))
        
        ttk.Button(actions_frame, text="🚛 Programar Entrega", 
                  style='Info.TButton',
                  command=self.schedule_delivery_from_assignment).pack(side='left', padx=(0, 10))
        
        ttk.Button(actions_frame, text="❌ Cancelar Asignación", 
                  style='Danger.TButton',
                  command=self.cancel_assignment).pack(side='left')
        
        # Bind double-click event
        self.assignments_tree.bind('<Double-1>', self.view_assignment_details)
        
        # Load assignments
        self.refresh_assignments()
    
    def show_request_form(self):
        """Show distribution request form dialog"""
        self.request_form_window = tk.Toplevel(self.frame)
        self.request_form_window.title("Nueva Solicitud de Distribución")
        self.request_form_window.geometry("700x650")
        self.request_form_window.transient(self.frame)
        self.request_form_window.grab_set()
        
        # Main container with scrollbar
        canvas = tk.Canvas(self.request_form_window)
        scrollbar = ttk.Scrollbar(self.request_form_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form frame
        form_frame = ttk.Frame(scrollable_frame, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Sales point selection
        ttk.Label(form_frame, text="Punto de Venta *:").pack(anchor='w', pady=(0, 2))
        self.request_sales_point_var = tk.StringVar()
        sales_point_combo = ttk.Combobox(form_frame, textvariable=self.request_sales_point_var, 
                                       style='Custom.TCombobox', state='readonly')
        sales_point_combo.pack(fill='x', pady=(0, 8))
        
        # Load sales points for combobox
        try:
            sales_points = self.db.get_sales_points()
            sp_values = [f"{sp['id']} - {sp['name']}" for sp in sales_points]
            sales_point_combo['values'] = sp_values
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando puntos de venta: {str(e)}")
        
        # Products selection section
        products_frame = ttk.LabelFrame(form_frame, text="Productos Solicitados")
        products_frame.pack(fill='both', expand=True, pady=(0, 8))
        
        # Available products list
        ttk.Label(products_frame, text="Productos Disponibles:").pack(anchor='w', pady=(5, 2))
        
        # Products listbox with scrollbar
        products_list_frame = ttk.Frame(products_frame)
        products_list_frame.pack(fill='both', expand=True, pady=3)
        
        self.available_products_listbox = tk.Listbox(products_list_frame, height=4)
        products_scrollbar = ttk.Scrollbar(products_list_frame, orient='vertical', command=self.available_products_listbox.yview)
        self.available_products_listbox.configure(yscrollcommand=products_scrollbar.set)
        
        self.available_products_listbox.pack(side='left', fill='both', expand=True)
        products_scrollbar.pack(side='right', fill='y')
        
        # Load available products
        try:
            products = self.db.get_products(available_only=True)
            self.product_data = {}
            for product in products:
                display_text = f"{product['name']} - {product['category']} ({product['quantity']} {product['unit']}) - ${product['price_per_unit']:.2f}/{product['unit']}"
                self.available_products_listbox.insert(tk.END, display_text)
                self.product_data[len(self.product_data)] = product
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {str(e)}")
        
        # Add/Remove buttons
        buttons_frame = ttk.Frame(products_frame)
        buttons_frame.pack(fill='x', pady=3)
        
        ttk.Button(buttons_frame, text="Agregar →", command=self.add_product_to_request).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="← Quitar", command=self.remove_product_from_request).pack(side='left')
        
        # Selected products
        ttk.Label(products_frame, text="Productos Seleccionados:").pack(anchor='w', pady=(8, 2))
        
        # Selected products treeview
        selected_frame = ttk.Frame(products_frame)
        selected_frame.pack(fill='both', expand=True, pady=3)
        
        columns = ('Producto', 'Cantidad', 'Unidad', 'Precio')
        self.selected_products_tree = ttk.Treeview(selected_frame, columns=columns, show='headings', height=3)
        
        for col in columns:
            self.selected_products_tree.heading(col, text=col)
            if col == 'Producto':
                self.selected_products_tree.column(col, width=200)
            else:
                self.selected_products_tree.column(col, width=80)
        
        selected_scrollbar = ttk.Scrollbar(selected_frame, orient='vertical', command=self.selected_products_tree.yview)
        self.selected_products_tree.configure(yscrollcommand=selected_scrollbar.set)
        
        self.selected_products_tree.pack(side='left', fill='both', expand=True)
        selected_scrollbar.pack(side='right', fill='y')
        
        # Keep track of selected products
        self.selected_products = []
        
        # Additional fields in rows for better layout
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill='x', pady=(8, 0))
        
        # Row 1: Priority and Date
        row1_frame = ttk.Frame(fields_frame)
        row1_frame.pack(fill='x', pady=(0, 5))
        
        # Priority column
        priority_frame = ttk.Frame(row1_frame)
        priority_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(priority_frame, text="Prioridad:").pack(anchor='w')
        self.request_priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.request_priority_var, 
                                    style='Custom.TCombobox', state='readonly')
        priority_combo['values'] = ['low', 'medium', 'high']
        priority_combo.set('medium')
        priority_combo.pack(fill='x')
        
        # Date column
        date_frame = ttk.Frame(row1_frame)
        date_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(date_frame, text="Fecha Requerida:").pack(anchor='w')
        date_input_frame = ttk.Frame(date_frame)
        date_input_frame.pack(fill='x')
        
        self.request_required_date_var = tk.StringVar()
        ttk.Entry(date_input_frame, textvariable=self.request_required_date_var, 
                 style='Custom.TEntry', width=15).pack(side='left')
        ttk.Label(date_input_frame, text="(YYYY-MM-DD)").pack(side='left', padx=(5, 0))
        
        # Notes
        ttk.Label(fields_frame, text="Notas Adicionales:").pack(anchor='w', pady=(5, 2))
        self.request_notes_text = tk.Text(fields_frame, height=3, font=('Segoe UI', 10), wrap=tk.WORD)
        self.request_notes_text.pack(fill='x', pady=(0, 8))
        
        # Buttons
        buttons_frame = ttk.Frame(fields_frame)
        buttons_frame.pack(fill='x', pady=(8, 0))
        
        ttk.Button(buttons_frame, text="💾 Guardar Solicitud", 
                  style='Primary.TButton',
                  command=self.save_request).pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                  style='Secondary.TButton',
                  command=self.request_form_window.destroy).pack(side='left')
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def add_product_to_request(self):
        """Add selected product to request"""
        selection = self.available_products_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la lista")
            return
        
        product_index = selection[0]
        product = self.product_data[product_index]
        
        # Ask for quantity
        quantity_window = tk.Toplevel(self.request_form_window)
        quantity_window.title("Cantidad Solicitada")
        quantity_window.geometry("300x150")
        quantity_window.transient(self.request_form_window)
        quantity_window.grab_set()
        
        ttk.Label(quantity_window, text=f"Producto: {product['name']}").pack(pady=10)
        ttk.Label(quantity_window, text=f"Disponible: {product['quantity']} {product['unit']}").pack()
        
        ttk.Label(quantity_window, text="Cantidad solicitada:").pack(pady=(10, 5))
        quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(quantity_window, textvariable=quantity_var, width=20)
        quantity_entry.pack(pady=5)
        quantity_entry.focus()
        
        def add_product():
            try:
                quantity = float(quantity_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser positiva")
                    return
                
                if quantity > product['quantity']:
                    messagebox.showerror("Error", "Cantidad no disponible")
                    return
                
                # Add to selected products
                selected_product = {
                    'id': product['id'],
                    'name': product['name'],
                    'quantity': quantity,
                    'unit': product['unit'],
                    'price': product['price_per_unit']
                }
                
                self.selected_products.append(selected_product)
                
                # Update tree
                self.selected_products_tree.insert('', 'end', values=(
                    product['name'],
                    f"{quantity:.1f}",
                    product['unit'],
                    f"${product['price_per_unit']:.2f}"
                ))
                
                quantity_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida")
        
        buttons_frame = ttk.Frame(quantity_window)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Agregar", command=add_product).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=quantity_window.destroy).pack(side='left')
    
    def remove_product_from_request(self):
        """Remove selected product from request"""
        selection = self.selected_products_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para quitar")
            return
        
        item = selection[0]
        product_name = self.selected_products_tree.item(item)['values'][0]
        
        # Remove from list and tree
        self.selected_products = [p for p in self.selected_products if p['name'] != product_name]
        self.selected_products_tree.delete(item)
    
    def save_request(self):
        """Save distribution request"""
        try:
            # Validate required fields
            if not self.request_sales_point_var.get():
                messagebox.showerror("Error", "Debe seleccionar un punto de venta")
                return
            
            if not self.selected_products:
                messagebox.showerror("Error", "Debe seleccionar al menos un producto")
                return
            
            # Calculate total price automatically based on selected products
            total_price = sum([p['price'] * p['quantity'] for p in self.selected_products])
            
            # Validate date if provided
            required_date = self.request_required_date_var.get().strip()
            if required_date and not Validator.is_valid_date(required_date):
                messagebox.showerror("Error", "Formato de fecha inválido")
                return
            
            # Get sales point ID
            sales_point_selection = self.request_sales_point_var.get()
            sales_point_id = int(sales_point_selection.split(' - ')[0])
            
            # Prepare product IDs and quantities
            product_ids = [p['id'] for p in self.selected_products]
            quantities = [p['quantity'] for p in self.selected_products]
            
            # Prepare request data
            request_data = {
                'sales_point_id': sales_point_id,
                'product_ids': product_ids,
                'quantities': quantities,
                'total_price': total_price,
                'required_date': required_date if required_date else None,
                'priority': self.request_priority_var.get(),
                'notes': self.request_notes_text.get(1.0, tk.END).strip() if self.request_notes_text.get(1.0, tk.END).strip() else None
            }
            
            # Create request and automatically generate assignments and update inventory
            request_id = self.db.add_distribution_request_with_auto_assignment(request_data)
            messagebox.showinfo("Éxito", f"Solicitud creada con ID: {request_id}\nTotal a pagar: ${total_price:.2f}\nInventario actualizado automáticamente")
            
            self.request_form_window.destroy()
            self.refresh_requests()
            self.refresh_matching()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando solicitud: {str(e)}")
    
    def edit_request(self):
        """Edit the selected distribution request"""
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud para editar")
            return
        
        item = self.requests_tree.item(selection[0])
        request_id = int(item['values'][0])
        
        # Get request details
        try:
            requests = self.db.get_distribution_requests()
            request = next((r for r in requests if r['id'] == request_id), None)
            if not request:
                messagebox.showerror("Error", "Solicitud no encontrada")
                return
            
            # Check if request can be edited (only pending or assigned status)
            if request['status'] not in ['pending', 'assigned']:
                messagebox.showwarning("Advertencia", "Solo se pueden editar solicitudes pendientes o asignadas")
                return
            
            self.show_edit_request_form(request)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando solicitud: {str(e)}")
    
    def cancel_request(self):
        """Cancel the selected distribution request"""
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud para cancelar")
            return
        
        item = self.requests_tree.item(selection[0])
        request_id = int(item['values'][0])
        
        # Confirm cancellation
        if not messagebox.askyesno("Confirmar", "¿Está seguro de cancelar esta solicitud?\nEsto restaurará el inventario de productos."):
            return
        
        try:
            self.db.cancel_distribution_request(request_id)
            messagebox.showinfo("Éxito", "Solicitud cancelada e inventario restaurado")
            self.refresh_requests()
            self.refresh_matching()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cancelando solicitud: {str(e)}")
    
    def show_payment_total(self):
        """Show payment total for the selected request"""
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud para ver el total")
            return
        
        item = self.requests_tree.item(selection[0])
        request_id = int(item['values'][0])
        
        try:
            requests = self.db.get_distribution_requests()
            request = next((r for r in requests if r['id'] == request_id), None)
            if not request:
                messagebox.showerror("Error", "Solicitud no encontrada")
                return
            
            # Show payment details window
            payment_window = tk.Toplevel(self.frame)
            payment_window.title(f"Total a Pagar - Solicitud #{request_id}")
            payment_window.geometry("500x400")
            payment_window.transient(self.frame)
            payment_window.grab_set()
            
            # Payment details frame
            details_frame = ttk.Frame(payment_window, padding=20)
            details_frame.pack(fill='both', expand=True)
            
            # Header
            ttk.Label(details_frame, text=f"Solicitud #{request_id}", style='Heading.TLabel').pack(pady=(0, 10))
            ttk.Label(details_frame, text=f"Punto de Venta: {request['sales_point_name']}").pack(anchor='w')
            ttk.Label(details_frame, text=f"Estado: {request['status']}").pack(anchor='w', pady=(0, 10))
            
            # Products breakdown
            ttk.Label(details_frame, text="Desglose de Productos:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 5))
            
            # Create treeview for product details
            columns = ('Producto', 'Cantidad', 'Precio Unit.', 'Subtotal')
            products_tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=8)
            
            for col in columns:
                products_tree.heading(col, text=col)
                if col == 'Producto':
                    products_tree.column(col, width=200)
                else:
                    products_tree.column(col, width=100)
            
            products_tree.pack(fill='both', expand=True, pady=5)
            
            # Load product details
            total_amount = 0
            for product_detail in request.get('product_details', []):
                subtotal = product_detail.get('quantity_requested', 0) * product_detail.get('price_per_unit', 0)
                total_amount += subtotal
                
                products_tree.insert('', 'end', values=(
                    product_detail.get('name', 'N/A'),
                    f"{product_detail.get('quantity_requested', 0):.1f} {product_detail.get('unit', '')}",
                    f"${product_detail.get('price_per_unit', 0):.2f}",
                    f"${subtotal:.2f}"
                ))
            
            # Total
            total_frame = ttk.Frame(details_frame)
            total_frame.pack(fill='x', pady=(10, 0))
            
            ttk.Label(total_frame, text=f"TOTAL A PAGAR: ${total_amount:.2f}", 
                     font=('Segoe UI', 12, 'bold')).pack(side='right')
            
            # Close button
            ttk.Button(details_frame, text="Cerrar", 
                      command=payment_window.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando total: {str(e)}")
    
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
                
                # Format products and quantities for display
                product_details = request.get('product_details', [])
                if product_details:
                    products_text = ", ".join([p['name'] for p in product_details[:2]])
                    if len(product_details) > 2:
                        products_text += f" (+{len(product_details)-2} más)"
                    
                    quantities_text = ", ".join([f"{p['quantity_requested']:.1f} {p['unit']}" for p in product_details[:2]])
                    if len(product_details) > 2:
                        quantities_text += "..."
                else:
                    products_text = "Sin productos"
                    quantities_text = "0"
                
                self.requests_tree.insert('', 'end', values=(
                    request['id'],
                    request['sales_point_name'],
                    products_text,
                    quantities_text,
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
                
                # Extract category and quantity information from product details
                product_details = request.get('product_details', [])
                if product_details:
                    # Get categories of all products in the request
                    categories = list(set([p.get('category', 'Sin categoría') for p in product_details]))
                    category_display = ", ".join(categories[:2])
                    if len(categories) > 2:
                        category_display += f" (+{len(categories)-2} más)"
                    
                    # Get total quantity requested
                    total_quantity = sum([p.get('quantity_requested', 0) for p in product_details])
                    units = list(set([p.get('unit', '') for p in product_details]))
                    unit_display = units[0] if len(units) == 1 else 'mixtas'
                    quantity_display = f"{total_quantity:.1f} {unit_display}"
                else:
                    category_display = "Sin productos"
                    quantity_display = "0"
                
                self.pending_requests_tree.insert('', 'end', values=(
                    request['id'],
                    request['sales_point_name'],
                    category_display,
                    quantity_display,
                    f"${request['max_price']:.2f}" if request.get('max_price') else 'N/A',
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
    
    def complete_request(self):
        """Complete a distribution request"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una asignación")
            return
        
        assignment_id = self.assignments_tree.item(selection[0])['values'][0]
        
        try:
            # Get assignment details
            assignments = self.db.get_distribution_assignments()
            assignment = next((a for a in assignments if a['id'] == assignment_id), None)
            
            if not assignment:
                messagebox.showerror("Error", "Asignación no encontrada")
                return
            
            request_id = assignment['request_id']
            
            # Update request status to completed
            self.db.update_request_status(request_id, 'completed')
            # Update assignment status to delivered
            self.db.update_assignment_status(assignment_id, 'delivered', 'Solicitud completada manualmente')
            
            messagebox.showinfo("Éxito", "Solicitud marcada como completada")
            self.refresh_assignments()
            self.refresh_requests()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error completando solicitud: {str(e)}")
    
    def view_assignment_details(self, event=None):
        """View assignment details"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una asignación")
            return
        
        assignment_id = self.assignments_tree.item(selection[0])['values'][0]
        
        try:
            assignments = self.db.get_distribution_assignments()
            assignment = next((a for a in assignments if a['id'] == assignment_id), None)
            
            if not assignment:
                messagebox.showerror("Error", "Asignación no encontrada")
                return
            
            # Create details window
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Detalles de Asignación #{assignment_id}")
            details_window.geometry("600x500")
            details_window.transient(self.parent)
            
            details_frame = ttk.Frame(details_window, padding=20)
            details_frame.pack(fill='both', expand=True)
            
            ttk.Label(details_frame, text=f"Asignación #{assignment_id}", 
                     style='Heading.TLabel').pack(pady=(0, 20))
            
            # Create details text
            details_text = tk.Text(details_frame, font=('Segoe UI', 10), wrap=tk.WORD, height=20)
            details_text.pack(fill='both', expand=True, pady=(0, 20))
            
            # Format assignment details
            details_content = f"""INFORMACIÓN DE LA ASIGNACIÓN

Solicitud ID: {assignment.get('request_id', 'N/A')}
Producto: {assignment.get('product_name', 'N/A')}
Categoría: {assignment.get('product_category', 'N/A')}
Agricultor: {assignment.get('farmer_name', 'N/A')}
Punto de Venta: {assignment.get('sales_point_name', 'N/A')}

CANTIDADES Y PRECIOS
Cantidad Asignada: {assignment.get('quantity_assigned', 0)} {assignment.get('product_unit', '')}
Precio Unitario: ${assignment.get('unit_price', 0):.2f}
Precio Total: ${assignment.get('total_price', 0):.2f}

ESTADO Y FECHAS
Estado: {assignment.get('status', 'N/A')}
Fecha de Asignación: {assignment.get('assigned_date', 'N/A')}
Fecha de Actualización: {assignment.get('updated_date', 'N/A')}

NOTAS
{assignment.get('notes', 'Sin notas adicionales')}
"""
            
            details_text.insert('1.0', details_content)
            details_text.configure(state='disabled')
            
            ttk.Button(details_frame, text="Cerrar", 
                      command=details_window.destroy).pack()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando detalles: {str(e)}")
    
    def schedule_delivery_from_assignment(self):
        """Schedule delivery from selected assignment"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una asignación")
            return
        
        assignment_id = self.assignments_tree.item(selection[0])['values'][0]
        
        # Create delivery scheduling window
        delivery_window = tk.Toplevel(self.parent)
        delivery_window.title("Programar Entrega")
        delivery_window.geometry("500x400")
        delivery_window.transient(self.parent)
        delivery_window.grab_set()
        
        form_frame = ttk.LabelFrame(delivery_window, text="Datos de la Entrega", padding=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Driver name
        ttk.Label(form_frame, text="Conductor:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        driver_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=driver_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Vehicle info
        ttk.Label(form_frame, text="Vehículo:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        vehicle_info_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=vehicle_info_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Scheduled date
        ttk.Label(form_frame, text="Fecha Programada:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        scheduled_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(form_frame, textvariable=scheduled_date_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Delivery address
        ttk.Label(form_frame, text="Dirección:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        address_text = tk.Text(form_frame, width=30, height=3)
        address_text.grid(row=3, column=1, padx=5, pady=5)
        
        # Notes
        ttk.Label(form_frame, text="Notas:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        notes_text = tk.Text(form_frame, width=30, height=3)
        notes_text.grid(row=4, column=1, padx=5, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(delivery_window)
        buttons_frame.pack(fill='x', padx=20, pady=10)
        
        def save_delivery():
            try:
                delivery_data = {
                    'assignment_id': assignment_id,
                    'driver_name': driver_name_var.get(),
                    'vehicle_info': vehicle_info_var.get(),
                    'scheduled_date': scheduled_date_var.get(),
                    'delivery_address': address_text.get('1.0', 'end-1c'),
                    'notes': notes_text.get('1.0', 'end-1c')
                }
                
                self.db.add_delivery(delivery_data)
                messagebox.showinfo("Éxito", "Entrega programada exitosamente")
                delivery_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error programando entrega: {str(e)}")
        
        ttk.Button(buttons_frame, text="Guardar", command=save_delivery).pack(side='right', padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=delivery_window.destroy).pack(side='right', padx=5)
    
    def mark_as_delivered(self):
        """Mark assignment as delivered"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una asignación")
            return
        
        assignment_id = self.assignments_tree.item(selection[0])['values'][0]
        
        try:
            self.db.update_assignment_status(assignment_id, 'delivered', 'Marcado como entregado manualmente')
            messagebox.showinfo("Éxito", "Asignación marcada como entregada")
            self.refresh_assignments()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando estado: {str(e)}")
    
    def cancel_assignment(self):
        """Cancel an assignment"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una asignación")
            return
        
        assignment_id = self.assignments_tree.item(selection[0])['values'][0]
        
        # Confirm cancellation
        if messagebox.askyesno("Confirmar", "¿Está seguro de cancelar esta asignación?"):
            try:
                self.db.update_assignment_status(assignment_id, 'cancelled', 'Cancelada por el usuario')
                messagebox.showinfo("Éxito", "Asignación cancelada")
                self.refresh_assignments()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cancelando asignación: {str(e)}")
