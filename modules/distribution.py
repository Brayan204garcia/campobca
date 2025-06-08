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
        self.selected_products = []
        
        # Initialize tree widget references
        self.requests_tree = None
        self.available_products_tree = None
        self.pending_requests_tree = None
        self.request_products_tree = None
        
        # Initialize filter variables
        self.status_filter_var = None
        self.priority_filter_var = None
        
    def show(self):
        """Show the distribution module"""
        if self.frame:
            self.frame.pack(fill='both', expand=True)
        else:
            self.frame = ttk.Frame(self.parent, style='Card.TFrame')
            self.frame.pack(fill='both', expand=True, padx=10, pady=10)
            self.create_distribution_interface()
        
    def hide(self):
        """Hide the distribution module"""
        if self.frame:
            self.frame.pack_forget()
    
    def create_distribution_interface(self):
        """Create the distribution coordination interface"""
        # Header
        header_frame = ttk.Frame(self.frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(20, 0))
        
        # Title and subtitle
        title_label = ttk.Label(header_frame, text="Gestión de Solicitudes de Distribución", 
                               style='Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Administra las solicitudes de distribución de productos", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Content frame
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        # Create requests management interface
        self.create_requests_management(content_frame)
    
    def create_requests_management(self, parent):
        """Create distribution requests management interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Solicitudes de Distribución", style='Heading.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="➕ Nueva Solicitud", 
                  style='Primary.TButton',
                  command=self.show_request_form).pack(side='right')
        
        # Filter frame
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Estado:").pack(side='left')
        self.status_filter_var = tk.StringVar()
        self.status_filter_var.trace('w', self.filter_requests)
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var, 
                                  style='Custom.TCombobox', state='readonly', width=15)
        status_combo['values'] = ['Todos', 'pendiente', 'confirmado', 'en_transito', 'entregado', 'cancelado']
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
                  command=lambda: self.view_request_details(None)).pack(side='left', padx=(0, 10))
        
        # Payment/Invoice button (changes based on status)
        self.payment_btn = ttk.Button(actions_frame, text="💰 Ver Total a Pagar",
                                     style='Primary.TButton',
                                     command=self.show_payment_or_invoice, state='disabled')
        self.payment_btn.pack(side='left')
        
        # Requests list
        requests_frame = ttk.LabelFrame(parent, text="Lista de Solicitudes", padding=10)
        requests_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Requests treeview
        columns = ('ID', 'Punto de Venta', 'Productos', 'Cantidades', 'Total a Pagar', 'Fecha Requerida', 'Prioridad', 'Estado')
        self.requests_tree = ttk.Treeview(requests_frame, columns=columns, show='headings', 
                                        style='Custom.Treeview', height=15)
        
        for col in columns:
            self.requests_tree.heading(col, text=col)
            if col == 'ID':
                self.requests_tree.column(col, width=50, minwidth=50)
            elif col in ['Punto de Venta', 'Productos']:
                self.requests_tree.column(col, width=150, minwidth=120)
            elif col == 'Estado':
                self.requests_tree.column(col, width=100, minwidth=80)
            else:
                self.requests_tree.column(col, width=120, minwidth=100)
        
        # Scrollbars for requests
        requests_scrollbar_y = ttk.Scrollbar(requests_frame, orient='vertical', command=self.requests_tree.yview)
        requests_scrollbar_x = ttk.Scrollbar(requests_frame, orient='horizontal', command=self.requests_tree.xview)
        self.requests_tree.configure(yscrollcommand=requests_scrollbar_y.set, xscrollcommand=requests_scrollbar_x.set)
        
        self.requests_tree.pack(side='left', fill='both', expand=True)
        requests_scrollbar_y.pack(side='right', fill='y')
        requests_scrollbar_x.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.requests_tree.bind('<<TreeviewSelect>>', self.on_request_select)
        self.requests_tree.bind('<Double-1>', self.view_request_details)
        
        # Store selected request for button updates
        self.selected_request = None
        
        # Load requests
        self.refresh_requests()
    
    def show_request_form(self):
        """Show distribution request form dialog"""
        # Create modal window
        modal = tk.Toplevel(self.parent)
        modal.title("Nueva Solicitud de Distribución")
        modal.transient(self.parent)
        modal.grab_set()
        
        # Configure scrollable main frame
        canvas = tk.Canvas(modal)
        scrollbar = ttk.Scrollbar(modal, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Auto-size and center the modal
        modal.update_idletasks()
        width = min(900, modal.winfo_screenwidth() - 100)
        height = min(800, modal.winfo_screenheight() - 100)
        x = (modal.winfo_screenwidth() // 2) - (width // 2)
        y = (modal.winfo_screenheight() // 2) - (height // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Nueva Solicitud de Distribución", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        # Form variables
        self.request_sales_point_var = tk.StringVar()
        self.request_required_date_var = tk.StringVar()
        self.request_priority_var = tk.StringVar(value='medium')
        
        # Sales point selection
        sp_frame = ttk.LabelFrame(main_frame, text="Punto de Venta", padding=10)
        sp_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(sp_frame, text="Seleccionar Punto de Venta *:").pack(anchor='w', pady=(0, 5))
        sp_combo = ttk.Combobox(sp_frame, textvariable=self.request_sales_point_var, 
                               style='Custom.TCombobox', state='readonly')
        
        # Load sales points
        try:
            sales_points = self.db.get_sales_points()
            sp_values = [f"{sp['id']} - {sp['name']}" for sp in sales_points]
            sp_combo['values'] = sp_values
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando puntos de venta: {str(e)}")
        
        sp_combo.pack(fill='x', ipady=5)
        
        # Product selection
        product_frame = ttk.LabelFrame(main_frame, text="Selección de Productos", padding=10)
        product_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Available products section
        available_frame = ttk.Frame(product_frame)
        available_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Label(available_frame, text="Productos Disponibles:").pack(anchor='w', pady=(0, 5))
        
        # Available products tree
        avail_columns = ('ID', 'Producto', 'Precio', 'Cantidad', 'Agricultor')
        self.available_tree = ttk.Treeview(available_frame, columns=avail_columns, show='headings', height=8)
        
        for col in avail_columns:
            self.available_tree.heading(col, text=col)
            if col == 'ID':
                self.available_tree.column(col, width=40)
            elif col == 'Producto':
                self.available_tree.column(col, width=120)
            else:
                self.available_tree.column(col, width=80)
        
        self.available_tree.pack(fill='both', expand=True)
        
        # Selected products section
        selected_frame = ttk.Frame(product_frame)
        selected_frame.pack(side='right', fill='both', expand=True)
        
        ttk.Label(selected_frame, text="Productos Seleccionados:").pack(anchor='w', pady=(0, 5))
        
        # Selected products tree
        sel_columns = ('Producto', 'Cantidad', 'Precio Unit.', 'Total')
        self.selected_products_tree = ttk.Treeview(selected_frame, columns=sel_columns, show='headings', height=8)
        
        for col in sel_columns:
            self.selected_products_tree.heading(col, text=col)
            self.selected_products_tree.column(col, width=80)
        
        self.selected_products_tree.pack(fill='both', expand=True)
        
        # Product action buttons
        button_frame = ttk.Frame(product_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="➕ Agregar", 
                  command=self.add_product_to_request).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="➖ Quitar", 
                  command=self.remove_product_from_request).pack(side='left')
        
        # Additional details
        details_frame = ttk.LabelFrame(main_frame, text="Detalles Adicionales", padding=10)
        details_frame.pack(fill='x', pady=(0, 15))
        
        # Date and priority in same row
        date_priority_frame = ttk.Frame(details_frame)
        date_priority_frame.pack(fill='x', pady=(0, 10))
        
        # Required date
        date_frame = ttk.Frame(date_priority_frame)
        date_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(date_frame, text="Fecha Requerida (YYYY-MM-DD):").pack(anchor='w', pady=(0, 5))
        ttk.Entry(date_frame, textvariable=self.request_required_date_var, 
                 style='Custom.TEntry').pack(fill='x', ipady=5)
        
        # Priority
        priority_frame = ttk.Frame(date_priority_frame)
        priority_frame.pack(side='right', fill='x', expand=True)
        ttk.Label(priority_frame, text="Prioridad:").pack(anchor='w', pady=(0, 5))
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.request_priority_var, 
                                    style='Custom.TCombobox', state='readonly')
        priority_combo['values'] = ['high', 'medium', 'low']
        priority_combo.pack(fill='x', ipady=5)
        
        # Notes
        ttk.Label(details_frame, text="Notas e Instrucciones Especiales:").pack(anchor='w', pady=(0, 5))
        self.request_notes_text = tk.Text(details_frame, height=4, wrap=tk.WORD)
        self.request_notes_text.pack(fill='x')
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(buttons_frame, text="Cancelar", style='Secondary.TButton',
                  command=modal.destroy).pack(side='right', padx=(10, 0))
        
        ttk.Button(buttons_frame, text="Guardar Solicitud", style='Primary.TButton',
                  command=self.save_request).pack(side='right')
        
        # Initialize empty selected products list
        self.selected_products = []
        
        # Load available products
        self.load_available_products()
    
    def load_available_products(self):
        """Load available products into the tree"""
        try:
            # Clear existing items
            for item in self.available_tree.get_children():
                self.available_tree.delete(item)
            
            # Load products
            products = self.db.get_products(available_only=True)
            
            for product in products:
                self.available_tree.insert('', 'end', values=(
                    product['id'],
                    product['name'],
                    f"${product['price_per_unit']:.2f}",
                    f"{product['quantity']} {product['unit']}",
                    product.get('farmer_name', 'N/A')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {str(e)}")
    
    def add_product_to_request(self):
        """Add selected product to request"""
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para agregar")
            return
        
        item = self.available_tree.item(selection[0])
        product_id = int(item['values'][0])
        product_name = item['values'][1]
        price_str = item['values'][2].replace('$', '')
        price = float(price_str)
        
        # Ask for quantity
        quantity_dialog = tk.Toplevel(self.parent)
        quantity_dialog.title("Cantidad")
        quantity_dialog.geometry("300x150")
        quantity_dialog.transient(self.parent)
        quantity_dialog.grab_set()
        
        # Center dialog
        quantity_dialog.update_idletasks()
        x = (quantity_dialog.winfo_screenwidth() // 2) - (quantity_dialog.winfo_width() // 2)
        y = (quantity_dialog.winfo_screenheight() // 2) - (quantity_dialog.winfo_height() // 2)
        quantity_dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(quantity_dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text=f"Cantidad para {product_name}:").pack(pady=(0, 10))
        
        quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(main_frame, textvariable=quantity_var)
        quantity_entry.pack(fill='x', pady=(0, 10))
        quantity_entry.focus()
        
        def add_product():
            try:
                quantity = float(quantity_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                    return
                
                # Check if product already selected
                for selected in self.selected_products:
                    if selected['id'] == product_id:
                        messagebox.showwarning("Advertencia", "Este producto ya está seleccionado")
                        quantity_dialog.destroy()
                        return
                
                # Add to selected products
                total = price * quantity
                product_data = {
                    'id': product_id,
                    'name': product_name,
                    'quantity': quantity,
                    'price': price,
                    'total': total
                }
                self.selected_products.append(product_data)
                
                # Update selected products tree
                self.selected_products_tree.insert('', 'end', values=(
                    product_name,
                    f"{quantity:.1f}",
                    f"${price:.2f}",
                    f"${total:.2f}"
                ))
                
                quantity_dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=quantity_dialog.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Agregar", 
                  command=add_product).pack(side='right')
        
        # Bind Enter key
        quantity_entry.bind('<Return>', lambda e: add_product())
    
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
                'total_amount': total_price,
                'requested_date': required_date if required_date else None,
                'priority': self.request_priority_var.get(),
                'special_instructions': self.request_notes_text.get(1.0, tk.END).strip() if self.request_notes_text.get(1.0, tk.END).strip() else None
            }
            
            # Create request and automatically generate assignments and update inventory
            request_id = self.db.add_distribution_request_with_auto_assignment(request_data)
            messagebox.showinfo("Éxito", f"Solicitud creada con ID: {request_id}\nTotal a pagar: ${total_price:.2f}\nInventario actualizado automáticamente")
            
            # Close modal and refresh
            self.refresh_requests()
            
            # Find and close the modal window
            for widget in self.parent.winfo_children():
                if isinstance(widget, tk.Toplevel) and widget.winfo_exists():
                    widget.destroy()
                    break
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando solicitud: {str(e)}")
    
    def edit_request(self):
        """Edit the selected distribution request"""
        if not hasattr(self, 'requests_tree') or self.requests_tree is None:
            return
            
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud para editar")
            return
        
        request_id = int(self.requests_tree.item(selection[0])['values'][0])
        
        try:
            requests = self.db.get_distribution_requests()
            request = next((r for r in requests if r['id'] == request_id), None)
            if not request:
                messagebox.showerror("Error", "Solicitud no encontrada")
                return
            
            if request['status'] != 'pendiente':
                messagebox.showwarning("Advertencia", "Solo se pueden editar solicitudes pendientes")
                return
            
            self.show_edit_request_form(request)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando solicitud: {str(e)}")
    
    def cancel_request(self):
        """Cancel the selected distribution request"""
        if not hasattr(self, 'requests_tree') or self.requests_tree is None:
            return
            
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud para cancelar")
            return
        
        request_id = int(self.requests_tree.item(selection[0])['values'][0])
        
        # Confirm cancellation
        result = messagebox.askyesno("Confirmar Cancelación", 
                                   "¿Está seguro de que desea cancelar esta solicitud?\n\nEsta acción no se puede deshacer.")
        if result:
            try:
                self.db.cancel_distribution_request(request_id)
                messagebox.showinfo("Éxito", "Solicitud cancelada correctamente")
                self.refresh_requests()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cancelando solicitud: {str(e)}")
    
    def show_payment_or_invoice(self):
        """Show payment total or invoice based on request status"""
        if not self.requests_tree:
            return
            
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
            payment_window = tk.Toplevel(self.parent)
            payment_window.title(f"Total a Pagar - Solicitud #{request_id}")
            payment_window.transient(self.parent)
            payment_window.grab_set()
            
            # Auto-size and center the window
            payment_window.update_idletasks()
            width = min(600, payment_window.winfo_screenwidth() - 100)
            height = min(500, payment_window.winfo_screenheight() - 100)
            x = (payment_window.winfo_screenwidth() // 2) - (width // 2)
            y = (payment_window.winfo_screenheight() // 2) - (height // 2)
            payment_window.geometry(f"{width}x{height}+{x}+{y}")
            
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
                subtotal = product_detail.get('line_total', 0)
                total_amount += subtotal
                
                products_tree.insert('', 'end', values=(
                    product_detail.get('product_name', 'N/A'),
                    f"{product_detail.get('quantity', 0)} {product_detail.get('unit', '')}",
                    f"${product_detail.get('price_per_unit', 0):.2f}",
                    f"${subtotal:.2f}"
                ))
            
            # Total amount
            ttk.Separator(details_frame, orient='horizontal').pack(fill='x', pady=10)
            ttk.Label(details_frame, text=f"Total: ${total_amount:.2f}", 
                     font=('Segoe UI', 12, 'bold')).pack(anchor='e')
            
            # Status-specific information
            if request['status'] == 'entregado':
                ttk.Label(details_frame, text="Estado: ENTREGADO ✓", 
                         foreground='green', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 0))
                if 'delivered_date' in request:
                    ttk.Label(details_frame, text=f"Fecha de entrega: {request['delivered_date'][:10]}").pack(anchor='w')
            
            # Close button
            ttk.Button(details_frame, text="Cerrar", 
                      command=payment_window.destroy).pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando detalles de pago: {str(e)}")
    
    def show_edit_request_form(self, request):
        """Show form to edit distribution request"""
        # Implementation similar to show_request_form but with pre-filled data
        # For brevity, keeping this as a placeholder
        messagebox.showinfo("Info", "Función de edición en desarrollo")
    
    def validate_date_format(self, date_string):
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def refresh_requests(self):
        """Refresh distribution requests list"""
        if not hasattr(self, 'requests_tree') or self.requests_tree is None:
            return
            
        try:
            # Clear existing items
            for item in self.requests_tree.get_children():
                self.requests_tree.delete(item)
            
            # Load requests with up-to-date status information
            requests = self.db.get_distribution_requests()
            
            for request in requests:
                # Format products list
                product_names = []
                quantities = []
                
                for product_detail in request.get('product_details', []):
                    product_names.append(product_detail.get('product_name', 'N/A'))
                    quantities.append(str(product_detail.get('quantity', 0)))
                
                products_str = ', '.join(product_names)
                quantities_str = ', '.join(quantities)
                
                # Truncate if too long
                if len(products_str) > 30:
                    products_str = products_str[:30] + "..."
                if len(quantities_str) > 20:
                    quantities_str = quantities_str[:20] + "..."
                
                self.requests_tree.insert('', 'end', values=(
                    request['id'],
                    request.get('sales_point_name', 'N/A'),
                    products_str,
                    quantities_str,
                    f"${request.get('total_amount', 0):.2f}",
                    request.get('requested_date', 'N/A'),
                    request.get('priority', 'N/A'),
                    request.get('status', 'N/A')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando solicitudes: {str(e)}")
    
    def filter_requests(self, *args):
        """Filter requests based on status and priority"""
        # Implementation for filtering
        self.refresh_requests()
    
    def on_request_select(self, event):
        """Handle request selection"""
        if not hasattr(self, 'requests_tree') or self.requests_tree is None:
            return
            
        selection = self.requests_tree.selection()
        if selection:
            item = self.requests_tree.item(selection[0])
            request_status = item['values'][7]  # Status is in column 7
            
            # Update button text based on status
            if request_status == 'entregado':
                self.payment_btn.config(text="📄 Ver Factura", state='normal')
            else:
                self.payment_btn.config(text="💰 Ver Total a Pagar", state='normal')
        else:
            self.payment_btn.config(state='disabled')
    
    def view_request_details(self, event):
        """View detailed information about a request"""
        if not hasattr(self, 'requests_tree') or self.requests_tree is None:
            return
            
        selection = self.requests_tree.selection()
        if not selection:
            if event is None:  # Only show warning if called by button, not double-click
                messagebox.showwarning("Advertencia", "Seleccione una solicitud para ver detalles")
            return
        
        request_id = int(self.requests_tree.item(selection[0])['values'][0])
        
        try:
            requests = self.db.get_distribution_requests()
            request = next((r for r in requests if r['id'] == request_id), None)
            if not request:
                messagebox.showerror("Error", "Solicitud no encontrada")
                return
            
            # Create details window
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Detalles de Solicitud #{request_id}")
            details_window.geometry("600x500")
            details_window.transient(self.parent)
            details_window.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(details_window, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title and basic info
            ttk.Label(main_frame, text=f"Solicitud #{request_id}", 
                     style='Heading.TLabel').pack(pady=(0, 20))
            
            # Request information
            info_frame = ttk.LabelFrame(main_frame, text="Información General", padding=10)
            info_frame.pack(fill='x', pady=(0, 15))
            
            ttk.Label(info_frame, text=f"Punto de Venta: {request.get('sales_point_name', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Estado: {request.get('status', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Prioridad: {request.get('priority', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Fecha Solicitada: {request.get('requested_date', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Fecha de Creación: {request.get('created_date', 'N/A')[:10]}").pack(anchor='w')
            
            # Products details
            products_frame = ttk.LabelFrame(main_frame, text="Productos Solicitados", padding=10)
            products_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            # Products treeview
            columns = ('Producto', 'Cantidad', 'Precio Unit.', 'Subtotal')
            products_tree = ttk.Treeview(products_frame, columns=columns, show='headings', height=8)
            
            for col in columns:
                products_tree.heading(col, text=col)
                if col == 'Producto':
                    products_tree.column(col, width=200)
                else:
                    products_tree.column(col, width=100)
            
            products_tree.pack(fill='both', expand=True)
            
            # Load product details
            total_amount = 0
            for product_detail in request.get('product_details', []):
                subtotal = product_detail.get('line_total', 0)
                total_amount += subtotal
                
                products_tree.insert('', 'end', values=(
                    product_detail.get('product_name', 'N/A'),
                    f"{product_detail.get('quantity', 0)} {product_detail.get('unit', '')}",
                    f"${product_detail.get('price_per_unit', 0):.2f}",
                    f"${subtotal:.2f}"
                ))
            
            # Total and notes
            ttk.Label(main_frame, text=f"Total: ${total_amount:.2f}", 
                     font=('Segoe UI', 12, 'bold')).pack(anchor='e', pady=(10, 0))
            
            if request.get('special_instructions'):
                notes_frame = ttk.LabelFrame(main_frame, text="Instrucciones Especiales", padding=10)
                notes_frame.pack(fill='x', pady=(10, 0))
                ttk.Label(notes_frame, text=request['special_instructions'], wraplength=500).pack(anchor='w')
            
            # Close button
            ttk.Button(main_frame, text="Cerrar", 
                      command=details_window.destroy).pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando detalles: {str(e)}")