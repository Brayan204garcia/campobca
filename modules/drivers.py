import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

class DriversModule:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.frame = None
        
        # Variables for form
        self.form_vars = {}
        self.selected_driver_id = None
        
    def show(self):
        """Show the drivers module"""
        if self.frame:
            self.frame.pack(fill='both', expand=True)
        else:
            self.create_drivers_interface()
    
    def hide(self):
        """Hide the drivers module"""
        if self.frame:
            self.frame.pack_forget()
    
    def create_drivers_interface(self):
        """Create the drivers management interface"""
        # Main container frame
        self.frame = ttk.Frame(self.parent, style='Main.TFrame')
        self.frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(20, 0))
        
        # Title and subtitle
        title_label = ttk.Label(header_frame, text="Gestión de Conductores", 
                               style='Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Administra la información de conductores y vehículos", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Add driver button
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(anchor='e', side='right')
        
        add_btn = ttk.Button(button_frame, text="➕ Nuevo Conductor", 
                           style='Primary.TButton',
                           command=self.show_driver_form)
        add_btn.pack()
        
        # Content frame
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        # Drivers list
        list_frame = ttk.LabelFrame(content_frame, text="Lista de Conductores", padding=10)
        list_frame.pack(fill='both', expand=True)
        
        # Search and filter frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        # Search
        ttk.Label(search_frame, text="Buscar:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_drivers)
        ttk.Entry(search_frame, textvariable=self.search_var, 
                 style='Custom.TEntry', width=20).pack(side='left', padx=(5, 10))
        
        # Action buttons
        action_frame = ttk.Frame(search_frame)
        action_frame.pack(side='right')
        
        self.edit_btn = ttk.Button(action_frame, text="✏️ Editar", 
                                 style='Secondary.TButton',
                                 command=self.edit_selected_driver, state='disabled')
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        self.deactivate_btn = ttk.Button(action_frame, text="🚫 Desactivar", 
                                       style='Danger.TButton',
                                       command=self.deactivate_driver, state='disabled')
        self.deactivate_btn.pack(side='left')
        
        # Treeview container
        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill='both', expand=True)
        
        # Drivers treeview
        columns = ('ID', 'Nombre', 'Teléfono', 'Licencia', 'Tipo de Vehículo', 'Placa', 'Capacidad')
        self.drivers_tree = ttk.Treeview(tree_container, columns=columns, show='headings', 
                                       style='Custom.Treeview', height=15)
        
        for col in columns:
            self.drivers_tree.heading(col, text=col)
            if col == 'ID':
                self.drivers_tree.column(col, width=50, anchor='center')
            elif col == 'Nombre':
                self.drivers_tree.column(col, width=150, anchor='w')
            elif col == 'Teléfono':
                self.drivers_tree.column(col, width=120, anchor='center')
            elif col == 'Licencia':
                self.drivers_tree.column(col, width=120, anchor='center')
            elif col == 'Tipo de Vehículo':
                self.drivers_tree.column(col, width=120, anchor='center')
            elif col == 'Placa':
                self.drivers_tree.column(col, width=100, anchor='center')
            elif col == 'Capacidad':
                self.drivers_tree.column(col, width=100, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.drivers_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient='horizontal', command=self.drivers_tree.xview)
        
        self.drivers_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.drivers_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.drivers_tree.bind('<<TreeviewSelect>>', self.on_driver_select)
        
        # Load data
        self.refresh_drivers()
    
    def show_driver_form(self, driver_data=None):
        """Show driver form dialog"""
        # Create modal window
        modal = tk.Toplevel(self.parent)
        modal.title("Nuevo Conductor" if not driver_data else "Editar Conductor")
        modal.geometry("500x600")
        modal.resizable(False, False)
        modal.transient(self.parent)
        modal.grab_set()
        
        # Center the modal
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (modal.winfo_width() // 2)
        y = (modal.winfo_screenheight() // 2) - (modal.winfo_height() // 2)
        modal.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(modal, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="Nuevo Conductor" if not driver_data else "Editar Conductor",
                               style='Heading.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill='both', expand=True)
        
        # Variables
        name_var = tk.StringVar()
        phone_var = tk.StringVar()
        email_var = tk.StringVar()
        license_var = tk.StringVar()
        vehicle_type_var = tk.StringVar()
        vehicle_plate_var = tk.StringVar()
        vehicle_capacity_var = tk.StringVar()
        
        # Name
        name_frame = ttk.Frame(fields_frame)
        name_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(name_frame, text="Nombre *:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        name_entry = ttk.Entry(name_frame, textvariable=name_var, style='Custom.TEntry')
        name_entry.pack(fill='x', ipady=5)
        
        # Phone and Email
        contact_frame = ttk.Frame(fields_frame)
        contact_frame.pack(fill='x', pady=(0, 15))
        
        phone_frame = ttk.Frame(contact_frame)
        phone_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(phone_frame, text="Teléfono *:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        phone_entry = ttk.Entry(phone_frame, textvariable=phone_var, style='Custom.TEntry')
        phone_entry.pack(fill='x', ipady=5)
        
        email_frame = ttk.Frame(contact_frame)
        email_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(email_frame, text="Email:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        email_entry = ttk.Entry(email_frame, textvariable=email_var, style='Custom.TEntry')
        email_entry.pack(fill='x', ipady=5)
        
        # License Number
        license_frame = ttk.Frame(fields_frame)
        license_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(license_frame, text="Número de Licencia *:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        license_entry = ttk.Entry(license_frame, textvariable=license_var, style='Custom.TEntry')
        license_entry.pack(fill='x', ipady=5)
        
        # Vehicle Type and Plate
        vehicle_frame = ttk.Frame(fields_frame)
        vehicle_frame.pack(fill='x', pady=(0, 15))
        
        type_frame = ttk.Frame(vehicle_frame)
        type_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(type_frame, text="Tipo de Vehículo *:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        type_combo = ttk.Combobox(type_frame, textvariable=vehicle_type_var, style='Custom.TCombobox')
        type_combo['values'] = ['Camión', 'Camioneta', 'Furgón', 'Motocicleta', 'Automóvil']
        type_combo.pack(fill='x', ipady=5)
        
        plate_frame = ttk.Frame(vehicle_frame)
        plate_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(plate_frame, text="Placa *:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        plate_entry = ttk.Entry(plate_frame, textvariable=vehicle_plate_var, style='Custom.TEntry')
        plate_entry.pack(fill='x', ipady=5)
        
        # Vehicle Capacity
        capacity_frame = ttk.Frame(fields_frame)
        capacity_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(capacity_frame, text="Capacidad del Vehículo (kg):", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        capacity_entry = ttk.Entry(capacity_frame, textvariable=vehicle_capacity_var, style='Custom.TEntry')
        capacity_entry.pack(fill='x', ipady=5)
        
        # Fill form if editing
        if driver_data:
            name_var.set(driver_data.get('name', ''))
            phone_var.set(driver_data.get('phone', ''))
            email_var.set(driver_data.get('email', ''))
            license_var.set(driver_data.get('license_number', ''))
            vehicle_type_var.set(driver_data.get('vehicle_type', ''))
            vehicle_plate_var.set(driver_data.get('vehicle_plate', ''))
            vehicle_capacity_var.set(driver_data.get('vehicle_capacity', ''))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        def save_and_close():
            """Save driver and close modal"""
            # Validate required fields
            if not all([name_var.get().strip(), phone_var.get().strip(), 
                       license_var.get().strip(), vehicle_type_var.get().strip(),
                       vehicle_plate_var.get().strip()]):
                messagebox.showerror("Error", "Por favor complete todos los campos obligatorios (*)")
                return
            
            try:
                driver_info = {
                    'name': name_var.get().strip(),
                    'phone': phone_var.get().strip(),
                    'email': email_var.get().strip() if email_var.get().strip() else None,
                    'license_number': license_var.get().strip(),
                    'vehicle_type': vehicle_type_var.get().strip(),
                    'vehicle_plate': vehicle_plate_var.get().strip(),
                    'vehicle_capacity': vehicle_capacity_var.get().strip() if vehicle_capacity_var.get().strip() else None
                }
                
                if driver_data:
                    # Update existing driver
                    self.db.update_driver(driver_data['id'], driver_info)
                    messagebox.showinfo("Éxito", "Conductor actualizado correctamente")
                else:
                    # Add new driver
                    self.db.add_driver(driver_info)
                    messagebox.showinfo("Éxito", "Conductor agregado correctamente")
                
                self.refresh_drivers()
                modal.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar conductor: {str(e)}")
        
        def cancel_and_close():
            """Cancel and close modal"""
            modal.destroy()
        
        # Action buttons
        ttk.Button(buttons_frame, text="Cancelar", style='Secondary.TButton',
                  command=cancel_and_close).pack(side='right', padx=(10, 0))
        
        ttk.Button(buttons_frame, text="Guardar", style='Primary.TButton',
                  command=save_and_close).pack(side='right')
        
        # Focus on first field
        name_entry.focus()
    
    def edit_selected_driver(self):
        """Edit the selected driver"""
        if not self.selected_driver_id:
            return
        
        try:
            drivers = self.db.get_drivers(active_only=False)
            driver = next((d for d in drivers if d['id'] == self.selected_driver_id), None)
            
            if driver:
                self.show_driver_form(driver)
            else:
                messagebox.showerror("Error", "Conductor no encontrado")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar conductor: {str(e)}")
    
    def deactivate_driver(self):
        """Deactivate selected driver"""
        if not self.selected_driver_id:
            return
        
        result = messagebox.askyesno("Confirmar", 
                                   "¿Está seguro de que desea desactivar este conductor?")
        if result:
            try:
                self.db.update_driver(self.selected_driver_id, {'active': False})
                messagebox.showinfo("Éxito", "Conductor desactivado correctamente")
                self.refresh_drivers()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al desactivar conductor: {str(e)}")
    
    def refresh_drivers(self):
        """Refresh drivers list"""
        try:
            # Clear current items
            for item in self.drivers_tree.get_children():
                self.drivers_tree.delete(item)
            
            # Load drivers
            drivers = self.db.get_drivers(active_only=True)
            
            for driver in drivers:
                self.drivers_tree.insert('', 'end', values=(
                    driver['id'],
                    driver['name'],
                    driver['phone'],
                    driver['license_number'],
                    driver['vehicle_type'],
                    driver['vehicle_plate'],
                    driver.get('vehicle_capacity', 'N/A')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar conductores: {str(e)}")
    
    def on_driver_select(self, event):
        """Handle driver selection"""
        selection = self.drivers_tree.selection()
        if selection:
            item = self.drivers_tree.item(selection[0])
            self.selected_driver_id = int(item['values'][0])
            
            # Enable action buttons
            self.edit_btn.config(state='normal')
            self.deactivate_btn.config(state='normal')
        else:
            self.selected_driver_id = None
            self.edit_btn.config(state='disabled')
            self.deactivate_btn.config(state='disabled')
    
    def filter_drivers(self, *args):
        """Filter drivers based on search"""
        search_term = self.search_var.get().lower()
        
        try:
            # Clear current items
            for item in self.drivers_tree.get_children():
                self.drivers_tree.delete(item)
            
            # Load and filter drivers
            drivers = self.db.get_drivers(active_only=True)
            
            for driver in drivers:
                # Check if search term matches any field
                if (search_term in driver['name'].lower() or
                    search_term in driver['phone'].lower() or
                    search_term in driver['license_number'].lower() or
                    search_term in driver['vehicle_type'].lower() or
                    search_term in driver['vehicle_plate'].lower()):
                    
                    self.drivers_tree.insert('', 'end', values=(
                        driver['id'],
                        driver['name'],
                        driver['phone'],
                        driver['license_number'],
                        driver['vehicle_type'],
                        driver['vehicle_plate'],
                        driver.get('vehicle_capacity', 'N/A')
                    ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar conductores: {str(e)}")