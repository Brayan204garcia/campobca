import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional

class DeliveriesModule:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.frame = None
        
        # Initialize tree references safely
        self.deliveries_tree = None
        self.requests_tree = None
        self.delivery_form_window = None
        
        # Filter variables
        self.delivery_status_var = None
        self.date_from_var = None
        self.date_to_var = None
        
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
        ttk.Button(buttons_frame, text="Refrescar", 
                  command=self.refresh_deliveries).pack(side='left', padx=5)
        
        # Deliveries list
        list_frame = ttk.LabelFrame(parent, text="Lista de Entregas")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for deliveries
        columns = ('ID', 'Solicitud', 'Punto de Venta', 'Conductor', 
                  'Fecha Programada', 'Estado', 'Valor Total')
        self.deliveries_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = [50, 80, 200, 150, 120, 100, 120]
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
        ttk.Button(buttons_frame, text="Refrescar", 
                  command=self.refresh_requests).pack(side='left', padx=5)
        
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
    
    def refresh_data(self):
        """Refresh all data"""
        self.refresh_deliveries()
        self.refresh_requests()
    
    def refresh_deliveries(self):
        """Refresh deliveries list"""
        if not self.deliveries_tree:
            return
            
        try:
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
                    'programado': 'Programada',
                    'en_camino': 'En Tránsito',
                    'entregado': 'Entregada',
                    'cancelado': 'Cancelada'
                }.get(delivery.get('status', ''), delivery.get('status', ''))
                
                self.deliveries_tree.insert('', 'end', values=(
                    delivery.get('id', ''),
                    delivery.get('request_id', ''),
                    delivery.get('sales_point_name', ''),
                    delivery.get('driver_name', ''),
                    scheduled_date,
                    status_text,
                    f"${delivery.get('total_amount', 0):.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando entregas: {str(e)}")
    
    def refresh_requests(self):
        """Refresh confirmed requests list for delivery scheduling"""
        if not self.requests_tree:
            return
            
        try:
            # Clear existing data
            for item in self.requests_tree.get_children():
                self.requests_tree.delete(item)
            
            # Get confirmed requests that are ready for delivery but don't have delivery yet
            requests = self.db.get_distribution_requests(status='confirmado')
            deliveries = self.db.get_deliveries()
            
            # Get request IDs that already have deliveries
            delivered_request_ids = {d.get('request_id') for d in deliveries}
            
            # Filter requests without deliveries
            pending_requests = [r for r in requests if r.get('id') not in delivered_request_ids]
            
            # Populate tree
            for request in pending_requests:
                confirmed_date = request.get('confirmed_date', '')
                if confirmed_date:
                    try:
                        date_obj = datetime.fromisoformat(confirmed_date.replace('Z', '+00:00'))
                        confirmed_date = date_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                
                # Get product list
                products_list = []
                for item in request.get('products', []):
                    products_list.append(f"{item.get('product_name', '')} ({item.get('quantity', 0)})")
                products_str = ", ".join(products_list)
                
                status_text = {
                    'confirmado': 'Confirmada',
                    'en_transito': 'En Tránsito',
                    'entregado': 'Entregada'
                }.get(request.get('status', ''), request.get('status', ''))
                
                self.requests_tree.insert('', 'end', values=(
                    request.get('id', ''),
                    request.get('sales_point_name', ''),
                    request.get('sales_point_address', ''),
                    products_str[:50] + "..." if len(products_str) > 50 else products_str,
                    f"${request.get('total_amount', 0):.2f}",
                    confirmed_date,
                    status_text
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando solicitudes: {str(e)}")
    
    def schedule_delivery_from_request(self):
        """Schedule delivery from selected confirmed request"""
        if not self.requests_tree:
            return
            
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud para programar entrega")
            return
        
        request_id = int(self.requests_tree.item(selection[0])['values'][0])
        
        try:
            requests = self.db.get_distribution_requests()
            request = next((r for r in requests if r['id'] == request_id), None)
            if not request:
                messagebox.showerror("Error", "Solicitud no encontrada")
                return
            
            # Show delivery scheduling form
            delivery_window = tk.Toplevel(self.parent)
            delivery_window.title(f"Programar Entrega - Solicitud #{request_id}")
            delivery_window.geometry("600x700")
            delivery_window.transient(self.parent)
            delivery_window.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(delivery_window, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title
            ttk.Label(main_frame, text=f"Programar Entrega para Solicitud #{request_id}", 
                     style='Heading.TLabel').pack(pady=(0, 20))
            
            # Request information
            info_frame = ttk.LabelFrame(main_frame, text="Información de la Solicitud", padding=10)
            info_frame.pack(fill='x', pady=(0, 15))
            
            ttk.Label(info_frame, text=f"Punto de Venta: {request.get('sales_point_name', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Dirección: {request.get('sales_point_address', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Total: ${request.get('total_amount', 0):.2f}").pack(anchor='w')
            
            # Driver selection
            driver_frame = ttk.LabelFrame(main_frame, text="Selección de Conductor", padding=10)
            driver_frame.pack(fill='x', pady=(0, 15))
            
            ttk.Label(driver_frame, text="Conductor *:").pack(anchor='w', pady=(0, 5))
            driver_var = tk.StringVar()
            driver_combo = ttk.Combobox(driver_frame, textvariable=driver_var, width=50)
            
            # Load available drivers
            drivers = self.db.get_drivers(active_only=True)
            driver_values = [f"{d['id']} - {d['name']} ({d['vehicle_type']} - {d['vehicle_plate']})" for d in drivers]
            driver_combo['values'] = driver_values
            driver_combo.pack(fill='x', pady=(0, 10))
            
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
    
    def update_delivery_status(self):
        """Update delivery status"""
        if not self.deliveries_tree:
            return
            
        selection = self.deliveries_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una entrega para actualizar")
            return
        
        delivery_id = int(self.deliveries_tree.item(selection[0])['values'][0])
        
        # Show status update dialog
        status_window = tk.Toplevel(self.parent)
        status_window.title("Actualizar Estado de Entrega")
        status_window.geometry("400x300")
        status_window.transient(self.parent)
        status_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(status_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"Actualizar Estado - Entrega #{delivery_id}", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        # Status selection
        ttk.Label(main_frame, text="Nuevo Estado:").pack(anchor='w', pady=(0, 5))
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(main_frame, textvariable=status_var, width=30)
        status_combo['values'] = ("programado", "en_camino", "entregado", "cancelado")
        status_combo.pack(fill='x', pady=(0, 15))
        
        # Notes
        ttk.Label(main_frame, text="Notas (opcional):").pack(anchor='w', pady=(0, 5))
        notes_text = tk.Text(main_frame, width=40, height=6, wrap=tk.WORD)
        notes_text.pack(fill='both', expand=True, pady=(0, 15))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        def update_status():
            try:
                new_status = status_var.get()
                notes = notes_text.get('1.0', 'end-1c').strip()
                
                if not new_status:
                    messagebox.showwarning("Advertencia", "Seleccione un estado")
                    return
                
                self.db.update_delivery_status(delivery_id, new_status, notes if notes else None)
                messagebox.showinfo("Éxito", "Estado actualizado exitosamente")
                status_window.destroy()
                self.refresh_deliveries()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error actualizando estado: {str(e)}")
        
        ttk.Button(buttons_frame, text="Cancelar", style='Secondary.TButton',
                  command=status_window.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(buttons_frame, text="Actualizar", style='Primary.TButton',
                  command=update_status).pack(side='right')
    
    def view_delivery_details(self, event=None):
        """View delivery details"""
        if not self.deliveries_tree:
            return
            
        selection = self.deliveries_tree.selection()
        if not selection:
            if event is None:  # Only show warning if called by button, not double-click
                messagebox.showwarning("Advertencia", "Seleccione una entrega para ver detalles")
            return
        
        delivery_id = int(self.deliveries_tree.item(selection[0])['values'][0])
        
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
            status_text = {
                'programado': 'Programada',
                'en_camino': 'En Tránsito',
                'entregado': 'Entregada',
                'cancelado': 'Cancelada'
            }.get(delivery.get('status', ''), delivery.get('status', ''))
            
            details = f"""DETALLES DE LA ENTREGA #{delivery_id}

Información General:
- Estado: {status_text}
- Solicitud ID: {delivery.get('request_id', '')}
- Fecha Programada: {delivery.get('scheduled_date', '')}
- Hora Estimada: {delivery.get('estimated_time', 'No especificada')}

Punto de Venta:
- Nombre: {delivery.get('sales_point_name', '')}
- Dirección: {delivery.get('delivery_address', '')}

Conductor:
- Nombre: {delivery.get('driver_name', '')}
- Teléfono: {delivery.get('driver_phone', '')}
- Vehículo: {delivery.get('vehicle_info', '')}

Detalles Financieros:
- Valor Total: ${delivery.get('total_amount', 0):.2f}

Instrucciones Especiales:
{delivery.get('special_instructions', 'Ninguna')}

Notas:
{delivery.get('notes', 'Ninguna')}

Fechas Importantes:
- Creada: {delivery.get('created_date', '')}
- Actualizada: {delivery.get('status_updated_date', '')}
- Entregada: {delivery.get('delivered_date', 'Pendiente')}
"""
            
            details_text.insert(tk.END, details)
            details_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando detalles: {str(e)}")
    
    def view_request_details(self):
        """View details of selected request"""
        if not self.requests_tree:
            return
            
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
            ttk.Label(info_frame, text=f"Total: ${request.get('total_amount', 0):.2f}").pack(anchor='w')
            
            # Products
            products_frame = ttk.LabelFrame(main_frame, text="Productos Solicitados", padding=10)
            products_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            products_tree = ttk.Treeview(products_frame, columns=('Producto', 'Cantidad', 'Precio', 'Total'), 
                                       show='headings', height=6)
            
            for col in ['Producto', 'Cantidad', 'Precio', 'Total']:
                products_tree.heading(col, text=col)
                products_tree.column(col, width=120)
            
            for item in request.get('products', []):
                products_tree.insert('', 'end', values=(
                    item.get('product_name', ''),
                    f"{item.get('quantity', 0):.1f}",
                    f"${item.get('unit_price', 0):.2f}",
                    f"${item.get('total_price', 0):.2f}"
                ))
            
            products_tree.pack(fill='both', expand=True)
            
            # Close button
            ttk.Button(main_frame, text="Cerrar", command=details_window.destroy).pack(pady=(15, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando detalles: {str(e)}")
    
    def filter_deliveries(self, *args):
        """Filter deliveries based on criteria"""
        self.refresh_deliveries()