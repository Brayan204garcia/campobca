import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional

class DeliveriesModule:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.frame = None
        
        # Initialize tree references
        self.deliveries_tree = None
        self.assignments_tree = None  
        self.requests_tree = None
        self.delivery_form_window = None
        
    def show(self):
        """Show the deliveries module"""
        if self.frame:
            self.frame.pack(fill='both', expand=True)
        else:
            self.create_deliveries_interface()
        self.refresh_data()
    
    def hide(self):
        """Hide the deliveries module"""
        if self.frame:
            self.frame.pack_forget()
    
    def create_deliveries_interface(self):
        """Create the deliveries management interface"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        self.frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(self.frame, text="Gestión de Entregas", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Entregas Programadas
        deliveries_frame = ttk.Frame(notebook)
        notebook.add(deliveries_frame, text="Entregas")
        self.create_deliveries_management(deliveries_frame)
        
        # Tab 2: Solicitudes Confirmadas
        requests_frame = ttk.Frame(notebook)
        notebook.add(requests_frame, text="Solicitudes Confirmadas")
        self.create_requests_management(requests_frame)
    
    def create_deliveries_management(self, parent):
        """Create deliveries management interface"""
        # Controls frame
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Filter controls
        filter_frame = ttk.LabelFrame(controls_frame, text="Filtros")
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Status filter
        ttk.Label(filter_frame, text="Estado:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.delivery_status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.delivery_status_var, width=15)
        status_combo['values'] = ("all", "programado", "en_camino", "entregado", "cancelado")
        status_combo.grid(row=0, column=1, padx=5, pady=5)
        status_combo.bind('<<ComboboxSelected>>', self.filter_deliveries)
        
        # Date range filter
        ttk.Label(filter_frame, text="Fecha desde:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.date_from_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_from_entry = ttk.Entry(filter_frame, textvariable=self.date_from_var, width=12)
        date_from_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Fecha hasta:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.date_to_var = tk.StringVar(value=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        date_to_entry = ttk.Entry(filter_frame, textvariable=self.date_to_var, width=12)
        date_to_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Filter button
        filter_btn = ttk.Button(filter_frame, text="Aplicar Filtros", command=self.filter_deliveries)
        filter_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Action buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(buttons_frame, text="Actualizar Estado", 
                  command=self.update_delivery_status).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Ver Detalles", 
                  command=self.view_delivery_details).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Imprimir Ruta", 
                  command=self.print_delivery_route).pack(side='left', padx=5)
        
        # Deliveries list
        list_frame = ttk.LabelFrame(parent, text="Lista de Entregas")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for deliveries
        columns = ('ID', 'Producto', 'Agricultor', 'Punto de Venta', 'Conductor', 
                  'Fecha Programada', 'Estado', 'Cantidad', 'Valor Total')
        self.deliveries_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = [50, 120, 120, 120, 100, 100, 80, 80, 100]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.deliveries_tree.heading(col, text=col)
            self.deliveries_tree.column(col, width=width, minwidth=50)
        
        # Scrollbars for deliveries tree
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.deliveries_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.deliveries_tree.xview)
        self.deliveries_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack deliveries tree and scrollbars
        self.deliveries_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event
        self.deliveries_tree.bind('<Double-1>', self.view_delivery_details)
    
    def create_assignments_management(self, parent):
        """Create assignments management interface"""
        # Controls frame
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Action buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(buttons_frame, text="Programar Entrega", 
                  command=self.schedule_delivery).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Ver Detalles", 
                  command=self.view_assignment_details).pack(side='left', padx=5)
        
        # Assignments list
        list_frame = ttk.LabelFrame(parent, text="Asignaciones Pendientes de Entrega")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for assignments
        columns = ('ID', 'Producto', 'Agricultor', 'Punto de Venta', 'Cantidad', 
                  'Precio Unitario', 'Valor Total', 'Fecha Asignación')
        self.assignments_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = [50, 150, 120, 120, 80, 80, 100, 100]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.assignments_tree.heading(col, text=col)
            self.assignments_tree.column(col, width=width, minwidth=50)
        
        # Scrollbars for assignments tree
        v_scrollbar2 = ttk.Scrollbar(list_frame, orient='vertical', command=self.assignments_tree.yview)
        h_scrollbar2 = ttk.Scrollbar(list_frame, orient='horizontal', command=self.assignments_tree.xview)
        self.assignments_tree.configure(yscrollcommand=v_scrollbar2.set, xscrollcommand=h_scrollbar2.set)
        
        # Pack assignments tree and scrollbars
        self.assignments_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar2.grid(row=0, column=1, sticky='ns')
        h_scrollbar2.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event
        self.assignments_tree.bind('<Double-1>', self.schedule_delivery)
        
        # Load initial data
        self.refresh_assignments()
    
    def create_requests_management(self, parent):
        """Create requests management interface for delivery scheduling"""
        # Controls frame
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Action buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(buttons_frame, text="Programar Entrega", 
                  command=self.schedule_delivery_from_request).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Ver Detalles", 
                  command=self.view_request_details).pack(side='left', padx=5)
        
        # Requests list
        list_frame = ttk.LabelFrame(parent, text="Solicitudes Confirmadas Pendientes de Entrega")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for confirmed requests
        columns = ('ID', 'Punto de Venta', 'Dirección', 'Productos', 'Total', 'Fecha Confirmación', 'Estado')
        self.requests_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = [50, 150, 200, 150, 100, 120, 100]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.requests_tree.heading(col, text=col)
            self.requests_tree.column(col, width=width, minwidth=50)
        
        # Scrollbars for requests tree
        v_scrollbar3 = ttk.Scrollbar(list_frame, orient='vertical', command=self.requests_tree.yview)
        h_scrollbar3 = ttk.Scrollbar(list_frame, orient='horizontal', command=self.requests_tree.xview)
        self.requests_tree.configure(yscrollcommand=v_scrollbar3.set, xscrollcommand=h_scrollbar3.set)
        
        # Pack requests tree and scrollbars
        self.requests_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar3.grid(row=0, column=1, sticky='ns')
        h_scrollbar3.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event
        self.requests_tree.bind('<Double-1>', self.schedule_delivery_from_request)
        
        # Load initial data
        self.refresh_requests()
    
    def refresh_data(self):
        """Refresh all data"""
        self.refresh_deliveries()
        self.refresh_assignments()
        self.refresh_requests()
    
    def refresh_deliveries(self):
        """Refresh deliveries list"""
        try:
            # Check if tree exists
            if not hasattr(self, 'deliveries_tree') or self.deliveries_tree is None:
                return
                
            # Clear existing data
            for item in self.deliveries_tree.get_children():
                self.deliveries_tree.delete(item)
            
            # Get deliveries
            status_filter = None if self.delivery_status_var.get() == "all" else self.delivery_status_var.get()
            deliveries = self.db.get_deliveries(status=status_filter)
            
            # Populate tree
            for delivery in deliveries:
                scheduled_date = delivery.get('scheduled_date', '')
                if scheduled_date:
                    try:
                        date_obj = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
                        scheduled_date = date_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                
                status_text = {
                    'scheduled': 'Programada',
                    'in_transit': 'En Tránsito',
                    'delivered': 'Entregada',
                    'cancelled': 'Cancelada'
                }.get(delivery.get('status', ''), delivery.get('status', ''))
                
                self.deliveries_tree.insert('', 'end', values=(
                    delivery.get('id', ''),
                    delivery.get('product_name', ''),
                    delivery.get('farmer_name', ''),
                    delivery.get('sales_point_name', ''),
                    delivery.get('driver_name', ''),
                    scheduled_date,
                    status_text,
                    f"{delivery.get('quantity', 0):.1f}",
                    f"${delivery.get('total_price', 0):.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando entregas: {str(e)}")
    
    def refresh_assignments(self):
        """Refresh assignments list"""
        try:
            # Check if tree exists
            if not hasattr(self, 'assignments_tree') or self.assignments_tree is None:
                return
                
            # Clear existing data
            for item in self.assignments_tree.get_children():
                self.assignments_tree.delete(item)
            
            # Get assignments without delivery
            all_assignments = self.db.get_distribution_assignments(status='assigned')
            deliveries = self.db.get_deliveries()
            
            # Get assignment IDs that already have deliveries
            assigned_delivery_ids = {d.get('assignment_id') for d in deliveries}
            
            # Filter assignments without deliveries
            pending_assignments = [a for a in all_assignments 
                                 if a.get('id') not in assigned_delivery_ids]
            
            # Populate tree
            for assignment in pending_assignments:
                assigned_date = assignment.get('assigned_date', '')
                if assigned_date:
                    try:
                        date_obj = datetime.fromisoformat(assigned_date.replace('Z', '+00:00'))
                        assigned_date = date_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                
                self.assignments_tree.insert('', 'end', values=(
                    assignment.get('id', ''),
                    assignment.get('product_name', ''),
                    assignment.get('farmer_name', ''),
                    assignment.get('sales_point_name', ''),
                    f"{assignment.get('quantity_assigned', 0):.1f}",
                    f"${assignment.get('unit_price', 0):.2f}",
                    f"${assignment.get('total_price', 0):.2f}",
                    assigned_date
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando asignaciones: {str(e)}")
    
    def refresh_requests(self):
        """Refresh confirmed requests list for delivery scheduling"""
        try:
            # Check if tree exists
            if not hasattr(self, 'requests_tree') or self.requests_tree is None:
                return
                
            # Clear existing data
            for item in self.requests_tree.get_children():
                self.requests_tree.delete(item)
            
            # Get confirmed requests that are ready for delivery
            requests = self.db.get_distribution_requests(status='confirmado')
            
            for request in requests:
                # Format product list
                product_list = ', '.join([pd['product_name'] for pd in request.get('product_details', [])])
                if len(product_list) > 30:
                    product_list = product_list[:30] + "..."
                
                self.requests_tree.insert('', 'end', values=(
                    request['id'],
                    request.get('sales_point_name', 'N/A'),
                    request.get('sales_point_address', 'N/A'),
                    product_list,
                    f"${request.get('total_amount', 0):.2f}",
                    request.get('created_date', '')[:10] if request.get('created_date') else 'N/A',
                    request.get('status', 'N/A')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando solicitudes: {str(e)}")
    
    def schedule_delivery_from_request(self):
        """Schedule delivery from selected confirmed request"""
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud para programar entrega")
            return
        
        request_id = int(self.requests_tree.item(selection[0])['values'][0])
        
        # Get request details
        try:
            requests = self.db.get_distribution_requests()
            request = next((r for r in requests if r['id'] == request_id), None)
            if not request:
                messagebox.showerror("Error", "Solicitud no encontrada")
                return
            
            # Create delivery scheduling window
            delivery_window = tk.Toplevel(self.parent)
            delivery_window.title(f"Programar Entrega - Solicitud #{request_id}")
            delivery_window.geometry("500x600")
            delivery_window.transient(self.parent)
            delivery_window.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(delivery_window, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title
            ttk.Label(main_frame, text=f"Programar Entrega - Solicitud #{request_id}", 
                     style='Heading.TLabel').pack(pady=(0, 20))
            
            # Request info
            info_frame = ttk.LabelFrame(main_frame, text="Información de la Solicitud", padding=10)
            info_frame.pack(fill='x', pady=(0, 20))
            
            ttk.Label(info_frame, text=f"Punto de Venta: {request.get('sales_point_name', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Dirección: {request.get('sales_point_address', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Total: ${request.get('total_amount', 0):.2f}").pack(anchor='w')
            
            # Driver selection
            driver_frame = ttk.LabelFrame(main_frame, text="Seleccionar Conductor", padding=10)
            driver_frame.pack(fill='x', pady=(0, 15))
            
            ttk.Label(driver_frame, text="Conductor *:").pack(anchor='w', pady=(0, 5))
            driver_var = tk.StringVar()
            driver_combo = ttk.Combobox(driver_frame, textvariable=driver_var, style='Custom.TCombobox')
            
            # Load drivers
            drivers = self.db.get_drivers(active_only=True)
            driver_values = [f"{d['id']} - {d['name']} ({d['vehicle_type']} - {d['vehicle_plate']})" for d in drivers]
            driver_combo['values'] = driver_values
            driver_combo.pack(fill='x', ipady=5)
            
            # Delivery details
            details_frame = ttk.LabelFrame(main_frame, text="Detalles de Entrega", padding=10)
            details_frame.pack(fill='x', pady=(0, 15))
            
            # Scheduled date
            ttk.Label(details_frame, text="Fecha Programada *:").pack(anchor='w', pady=(0, 5))
            date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
            date_entry = ttk.Entry(details_frame, textvariable=date_var, style='Custom.TEntry')
            date_entry.pack(fill='x', ipady=5, pady=(0, 10))
            
            # Estimated time
            ttk.Label(details_frame, text="Hora Estimada:").pack(anchor='w', pady=(0, 5))
            time_var = tk.StringVar()
            time_entry = ttk.Entry(details_frame, textvariable=time_var, style='Custom.TEntry')
            time_entry.pack(fill='x', ipady=5, pady=(0, 10))
            
            # Special instructions
            ttk.Label(details_frame, text="Instrucciones Especiales:").pack(anchor='w', pady=(0, 5))
            instructions_text = tk.Text(details_frame, height=4, wrap=tk.WORD)
            instructions_text.pack(fill='x', pady=(0, 10))
            
            # Buttons
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill='x', pady=(20, 0))
            
            def save_delivery():
                """Save delivery and close window"""
                if not driver_var.get():
                    messagebox.showerror("Error", "Debe seleccionar un conductor")
                    return
                
                if not date_var.get():
                    messagebox.showerror("Error", "Debe especificar la fecha programada")
                    return
                
                try:
                    driver_id = int(driver_var.get().split(' - ')[0])
                    
                    delivery_data = {
                        'request_id': request_id,
                        'driver_id': driver_id,
                        'scheduled_date': date_var.get(),
                        'delivery_address': request.get('sales_point_address', ''),
                        'estimated_time': time_var.get() if time_var.get() else None,
                        'special_instructions': instructions_text.get(1.0, tk.END).strip() if instructions_text.get(1.0, tk.END).strip() else None
                    }
                    
                    delivery_id = self.db.add_delivery(delivery_data)
                    messagebox.showinfo("Éxito", f"Entrega programada con ID: {delivery_id}")
                    
                    self.refresh_deliveries()
                    self.refresh_requests()
                    delivery_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error programando entrega: {str(e)}")
            
            ttk.Button(buttons_frame, text="Cancelar", style='Secondary.TButton',
                      command=delivery_window.destroy).pack(side='right', padx=(10, 0))
            
            ttk.Button(buttons_frame, text="Programar Entrega", style='Primary.TButton',
                      command=save_delivery).pack(side='right')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al programar entrega: {str(e)}")
    
    def view_request_details(self):
        """View details of selected request"""
        selection = self.requests_tree.selection()
        if not selection:
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
            
            # Title
            ttk.Label(main_frame, text=f"Solicitud #{request_id}", 
                     style='Heading.TLabel').pack(pady=(0, 20))
            
            # Request information
            info_frame = ttk.LabelFrame(main_frame, text="Información General", padding=10)
            info_frame.pack(fill='x', pady=(0, 15))
            
            ttk.Label(info_frame, text=f"Punto de Venta: {request.get('sales_point_name', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Dirección: {request.get('sales_point_address', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Estado: {request.get('status', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Fecha de Creación: {request.get('created_date', 'N/A')[:10]}").pack(anchor='w')
            
            # Products details
            products_frame = ttk.LabelFrame(main_frame, text="Productos", padding=10)
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
            
            # Total
            ttk.Label(main_frame, text=f"Total: ${total_amount:.2f}", 
                     font=('Segoe UI', 12, 'bold')).pack(anchor='e', pady=(10, 0))
            
            # Close button
            ttk.Button(main_frame, text="Cerrar", 
                      command=details_window.destroy).pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
    
    def schedule_delivery(self):
        """Schedule a delivery for selected assignment"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una asignación para programar entrega")
            return
        
        assignment_id = self.assignments_tree.item(selection[0])['values'][0]
        self.show_delivery_form(assignment_id)
    
    def show_delivery_form(self, assignment_id):
        """Show delivery scheduling form"""
        if self.delivery_form_window:
            self.delivery_form_window.destroy()
        
        self.delivery_form_window = tk.Toplevel(self.parent)
        self.delivery_form_window.title("Programar Entrega")
        self.delivery_form_window.geometry("500x400")
        self.delivery_form_window.transient(self.parent)
        self.delivery_form_window.grab_set()
        
        # Form frame
        form_frame = ttk.LabelFrame(self.delivery_form_window, text="Datos de la Entrega")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Driver name
        ttk.Label(form_frame, text="Conductor:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.driver_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.driver_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Vehicle info
        ttk.Label(form_frame, text="Vehículo:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.vehicle_info_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.vehicle_info_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Scheduled date
        ttk.Label(form_frame, text="Fecha Programada:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.scheduled_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(form_frame, textvariable=self.scheduled_date_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Delivery address
        ttk.Label(form_frame, text="Dirección de Entrega:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.delivery_address_var = tk.StringVar()
        address_entry = tk.Text(form_frame, width=30, height=3)
        address_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Notes
        ttk.Label(form_frame, text="Notas:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.delivery_notes_var = tk.StringVar()
        notes_entry = tk.Text(form_frame, width=30, height=3)
        notes_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(self.delivery_form_window)
        buttons_frame.pack(fill='x', padx=20, pady=10)
        
        def save_delivery():
            try:
                delivery_data = {
                    'assignment_id': assignment_id,
                    'driver_name': self.driver_name_var.get(),
                    'vehicle_info': self.vehicle_info_var.get(),
                    'scheduled_date': self.scheduled_date_var.get(),
                    'delivery_address': address_entry.get('1.0', 'end-1c'),
                    'notes': notes_entry.get('1.0', 'end-1c')
                }
                
                self.db.add_delivery(delivery_data)
                messagebox.showinfo("Éxito", "Entrega programada exitosamente")
                self.delivery_form_window.destroy()
                self.refresh_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error programando entrega: {str(e)}")
        
        ttk.Button(buttons_frame, text="Guardar", command=save_delivery).pack(side='right', padx=5)
        ttk.Button(buttons_frame, text="Cancelar", 
                  command=self.delivery_form_window.destroy).pack(side='right', padx=5)
    
    def update_delivery_status(self):
        """Update delivery status"""
        if not hasattr(self, 'deliveries_tree') or self.deliveries_tree is None:
            return
            
        selection = self.deliveries_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una entrega para actualizar")
            return
        
        delivery_id = int(self.deliveries_tree.item(selection[0])['values'][0])
        
        # Show status update dialog
        status_window = tk.Toplevel(self.parent)
        status_window.title("Actualizar Estado de Entrega")
        status_window.geometry("400x200")
        status_window.transient(self.parent)
        status_window.grab_set()
        
        # Status selection
        ttk.Label(status_window, text="Nuevo Estado:").pack(pady=10)
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(status_window, textvariable=status_var, width=20)
        status_combo['values'] = ("programado", "en_camino", "entregado", "cancelado")
        status_combo.pack(pady=5)
        
        # Notes
        ttk.Label(status_window, text="Notas:").pack(pady=(10, 5))
        notes_text = tk.Text(status_window, width=40, height=4)
        notes_text.pack(pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(status_window)
        buttons_frame.pack(pady=10)
        
        def update_status():
            try:
                new_status = status_var.get()
                notes = notes_text.get('1.0', 'end-1c')
                
                if not new_status:
                    messagebox.showwarning("Advertencia", "Seleccione un estado")
                    return
                
                self.db.update_delivery_status(delivery_id, new_status, notes)
                messagebox.showinfo("Éxito", "Estado actualizado exitosamente")
                status_window.destroy()
                self.refresh_deliveries()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error actualizando estado: {str(e)}")
        
        ttk.Button(buttons_frame, text="Actualizar", command=update_status).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=status_window.destroy).pack(side='left', padx=5)
    
    def view_delivery_details(self, event=None):
        """View delivery details"""
        selection = self.deliveries_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una entrega para ver detalles")
            return
        
        delivery_id = self.deliveries_tree.item(selection[0])['values'][0]
        
        try:
            deliveries = self.db.get_deliveries()
            delivery = next((d for d in deliveries if d['id'] == delivery_id), None)
            
            if not delivery:
                messagebox.showerror("Error", "Entrega no encontrada")
                return
            
            # Show details window
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Detalles de Entrega #{delivery_id}")
            details_window.geometry("600x500")
            details_window.transient(self.parent)
            
            # Create details text
            details_text = tk.Text(details_window, wrap='word', padx=10, pady=10)
            details_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Format delivery details
            details = f"""DETALLES DE LA ENTREGA #{delivery_id}
            
Información del Producto:
- Producto: {delivery.get('product_name', '')}
- Cantidad: {delivery.get('quantity', 0)}
- Valor Total: ${delivery.get('total_price', 0):.2f}

Información del Agricultor:
- Agricultor: {delivery.get('farmer_name', '')}

Punto de Venta:
- Nombre: {delivery.get('sales_point_name', '')}

Información de Entrega:
- Conductor: {delivery.get('driver_name', '')}
- Vehículo: {delivery.get('vehicle_info', '')}
- Fecha Programada: {delivery.get('scheduled_date', '')}
- Dirección: {delivery.get('delivery_address', '')}
- Estado: {delivery.get('status', '')}

Fechas:
- Fecha de Creación: {delivery.get('created_date', '')}
- Fecha de Actualización: {delivery.get('updated_date', '')}
- Fecha de Entrega: {delivery.get('delivered_date', '')}

Notas:
{delivery.get('notes', '')}
"""
            
            details_text.insert('1.0', details)
            details_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando detalles: {str(e)}")
    
    def view_assignment_details(self):
        """View assignment details"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una asignación para ver detalles")
            return
        
        assignment_id = self.assignments_tree.item(selection[0])['values'][0]
        
        try:
            assignments = self.db.get_distribution_assignments()
            assignment = next((a for a in assignments if a['id'] == assignment_id), None)
            
            if not assignment:
                messagebox.showerror("Error", "Asignación no encontrada")
                return
            
            # Show details window
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Detalles de Asignación #{assignment_id}")
            details_window.geometry("600x400")
            details_window.transient(self.parent)
            
            # Create details text
            details_text = tk.Text(details_window, wrap='word', padx=10, pady=10)
            details_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Format assignment details
            details = f"""DETALLES DE LA ASIGNACIÓN #{assignment_id}

Información del Producto:
- Producto: {assignment.get('product_name', '')}
- Categoría: {assignment.get('product_category', '')}
- Cantidad Asignada: {assignment.get('quantity_assigned', 0)}
- Precio Unitario: ${assignment.get('unit_price', 0):.2f}
- Valor Total: ${assignment.get('total_price', 0):.2f}

Información del Agricultor:
- Agricultor: {assignment.get('farmer_name', '')}

Punto de Venta:
- Nombre: {assignment.get('sales_point_name', '')}

Estado: {assignment.get('status', '')}
Fecha de Asignación: {assignment.get('assigned_date', '')}

Notas:
{assignment.get('notes', '')}
"""
            
            details_text.insert('1.0', details)
            details_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando detalles: {str(e)}")
    
    def print_delivery_route(self):
        """Print delivery route (placeholder for now)"""
        selection = self.deliveries_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una entrega para imprimir ruta")
            return
        
        messagebox.showinfo("Información", "Función de impresión de ruta en desarrollo")
    
    def filter_deliveries(self, *args):
        """Filter deliveries based on criteria"""
        self.refresh_deliveries()