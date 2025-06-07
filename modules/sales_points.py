import tkinter as tk
from tkinter import ttk, messagebox
from utils.validators import Validator

class SalesPointsModule:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.frame = None
        self.current_sales_point_id = None
        
    def show(self):
        """Show the sales points module"""
        if self.frame:
            self.frame.destroy()
        
        self.frame = ttk.Frame(self.parent, style='Card.TFrame')
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_sales_points_interface()
        
    def hide(self):
        """Hide the sales points module"""
        if self.frame:
            self.frame.destroy()
            self.frame = None
    
    def create_sales_points_interface(self):
        """Create the sales points management interface"""
        # Title and controls
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header_frame, text="Gestión de Puntos de Venta", style='Heading.TLabel').pack(side='left')
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="➕ Nuevo Punto de Venta", 
                  style='Primary.TButton',
                  command=self.show_sales_point_form).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_sales_points).pack(side='left')
        
        # Main content frame
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Sales points list (left side)
        list_frame = ttk.LabelFrame(content_frame, text="Lista de Puntos de Venta", padding=10)
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Search and filter frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        # Search
        ttk.Label(search_frame, text="Buscar:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_sales_points)
        ttk.Entry(search_frame, textvariable=self.search_var, 
                 style='Custom.TEntry', width=20).pack(side='left', padx=(5, 10))
        
        # Type filter
        ttk.Label(search_frame, text="Tipo:").pack(side='left')
        self.type_filter_var = tk.StringVar()
        self.type_filter_var.trace('w', self.filter_sales_points)
        type_combo = ttk.Combobox(search_frame, textvariable=self.type_filter_var, 
                                 style='Custom.TCombobox', state='readonly', width=15)
        type_combo['values'] = ['Todos', 'Supermercado', 'Tienda Local', 'Restaurante', 'Mercado', 'Distribuidor', 'Otro']
        type_combo.set('Todos')
        type_combo.pack(side='left', padx=(5, 0))
        
        # Sales points treeview
        columns = ('ID', 'Nombre', 'Tipo', 'Contacto', 'Teléfono', 'Dirección')
        self.sales_points_tree = ttk.Treeview(list_frame, columns=columns, show='headings', 
                                            style='Custom.Treeview', height=15)
        
        for col in columns:
            self.sales_points_tree.heading(col, text=col)
            if col == 'ID':
                self.sales_points_tree.column(col, width=50, minwidth=50)
            elif col in ['Nombre', 'Dirección']:
                self.sales_points_tree.column(col, width=200, minwidth=150)
            elif col == 'Tipo':
                self.sales_points_tree.column(col, width=120, minwidth=100)
            else:
                self.sales_points_tree.column(col, width=150, minwidth=120)
        
        # Scrollbars for sales points tree
        scrollbar_y = ttk.Scrollbar(list_frame, orient='vertical', command=self.sales_points_tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient='horizontal', command=self.sales_points_tree.xview)
        self.sales_points_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.sales_points_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.sales_points_tree.bind('<<TreeviewSelect>>', self.on_sales_point_select)
        
        # Form frame (right side)
        self.form_frame = ttk.LabelFrame(content_frame, text="Información del Punto de Venta", padding=10)
        self.form_frame.pack(side='right', fill='y')
        
        self.create_sales_point_form()
        
        # Load sales points
        self.refresh_sales_points()
    
    def create_sales_point_form(self):
        """Create sales point form"""
        # Form fields
        fields_frame = ttk.Frame(self.form_frame)
        fields_frame.pack(fill='both', expand=True)
        
        # Name
        ttk.Label(fields_frame, text="Nombre *:").pack(anchor='w', pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.name_var, 
                 style='Custom.TEntry', width=35).pack(fill='x', pady=(0, 10))
        
        # Type
        ttk.Label(fields_frame, text="Tipo *:").pack(anchor='w', pady=(0, 5))
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(fields_frame, textvariable=self.type_var, 
                                style='Custom.TCombobox', width=35)
        type_combo['values'] = ['Supermercado', 'Tienda Local', 'Restaurante', 'Mercado', 'Distribuidor', 'Otro']
        type_combo.pack(fill='x', pady=(0, 10))
        
        # Contact person
        ttk.Label(fields_frame, text="Persona de Contacto:").pack(anchor='w', pady=(0, 5))
        self.contact_person_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.contact_person_var, 
                 style='Custom.TEntry', width=35).pack(fill='x', pady=(0, 10))
        
        # Email
        ttk.Label(fields_frame, text="Email:").pack(anchor='w', pady=(0, 5))
        self.email_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.email_var, 
                 style='Custom.TEntry', width=35).pack(fill='x', pady=(0, 10))
        
        # Phone
        ttk.Label(fields_frame, text="Teléfono:").pack(anchor='w', pady=(0, 5))
        self.phone_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.phone_var, 
                 style='Custom.TEntry', width=35).pack(fill='x', pady=(0, 10))
        
        # Address
        ttk.Label(fields_frame, text="Dirección *:").pack(anchor='w', pady=(0, 5))
        self.address_text = tk.Text(fields_frame, height=4, width=35, 
                                  font=('Segoe UI', 10), wrap=tk.WORD)
        self.address_text.pack(fill='x', pady=(0, 10))
        
        # Capacity info
        ttk.Label(fields_frame, text="Información de Capacidad:").pack(anchor='w', pady=(0, 5))
        self.capacity_text = tk.Text(fields_frame, height=3, width=35, 
                                   font=('Segoe UI', 10), wrap=tk.WORD)
        self.capacity_text.pack(fill='x', pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(fields_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        self.save_btn = ttk.Button(buttons_frame, text="💾 Guardar", 
                                 style='Primary.TButton',
                                 command=self.save_sales_point)
        self.save_btn.pack(side='left', padx=(0, 5))
        
        self.edit_btn = ttk.Button(buttons_frame, text="✏️ Editar", 
                                 style='Secondary.TButton',
                                 command=self.edit_sales_point, state='disabled')
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        ttk.Button(buttons_frame, text="🗑️ Limpiar", 
                  style='Secondary.TButton',
                  command=self.clear_form).pack(side='left')
    
    def show_sales_point_form(self):
        """Show form for new sales point entry"""
        self.clear_form()
        self.current_sales_point_id = None
        self.save_btn.configure(text="💾 Guardar")
        self.edit_btn.configure(state='disabled')
    
    def save_sales_point(self):
        """Save sales point data"""
        try:
            # Validate required fields
            if not self.name_var.get().strip():
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            if not self.type_var.get().strip():
                messagebox.showerror("Error", "El tipo es obligatorio")
                return
            
            address = self.address_text.get(1.0, tk.END).strip()
            if not address:
                messagebox.showerror("Error", "La dirección es obligatoria")
                return
            
            # Validate email if provided
            email = self.email_var.get().strip()
            if email and not Validator.is_valid_email(email):
                messagebox.showerror("Error", "El formato del email no es válido")
                return
            
            # Prepare sales point data
            sales_point_data = {
                'name': self.name_var.get().strip(),
                'type': self.type_var.get().strip(),
                'contact_person': self.contact_person_var.get().strip() if self.contact_person_var.get().strip() else None,
                'email': email if email else None,
                'phone': self.phone_var.get().strip() if self.phone_var.get().strip() else None,
                'address': address,
                'capacity_info': self.capacity_text.get(1.0, tk.END).strip() if self.capacity_text.get(1.0, tk.END).strip() else None
            }
            
            if self.current_sales_point_id:
                # Update existing sales point
                self.db.update_sales_point(self.current_sales_point_id, sales_point_data)
                messagebox.showinfo("Éxito", "Punto de venta actualizado correctamente")
            else:
                # Add new sales point
                sales_point_id = self.db.add_sales_point(sales_point_data)
                messagebox.showinfo("Éxito", f"Punto de venta agregado con ID: {sales_point_id}")
            
            self.refresh_sales_points()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando punto de venta: {str(e)}")
    
    def refresh_sales_points(self):
        """Refresh sales points list"""
        try:
            # Clear tree
            for item in self.sales_points_tree.get_children():
                self.sales_points_tree.delete(item)
            
            # Load sales points
            sales_points = self.db.get_sales_points()
            for sp in sales_points:
                self.sales_points_tree.insert('', 'end', values=(
                    sp['id'],
                    sp['name'],
                    sp['type'],
                    sp['contact_person'] or '',
                    sp['phone'] or '',
                    sp['address']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando puntos de venta: {str(e)}")
    
    def on_sales_point_select(self, event):
        """Handle sales point selection"""
        selection = self.sales_points_tree.selection()
        if selection:
            item = self.sales_points_tree.item(selection[0])
            sales_point_data = item['values']
            
            if sales_point_data:
                self.current_sales_point_id = sales_point_data[0]
                
                # Load full sales point data
                try:
                    sales_points = self.db.get_sales_points()
                    selected_sp = next((sp for sp in sales_points if sp['id'] == self.current_sales_point_id), None)
                    
                    if selected_sp:
                        self.name_var.set(selected_sp['name'])
                        self.type_var.set(selected_sp['type'])
                        self.contact_person_var.set(selected_sp['contact_person'] or '')
                        self.email_var.set(selected_sp['email'] or '')
                        self.phone_var.set(selected_sp['phone'] or '')
                        
                        self.address_text.delete(1.0, tk.END)
                        self.address_text.insert(1.0, selected_sp['address'])
                        
                        self.capacity_text.delete(1.0, tk.END)
                        if selected_sp['capacity_info']:
                            self.capacity_text.insert(1.0, selected_sp['capacity_info'])
                        
                        self.save_btn.configure(text="💾 Actualizar")
                        self.edit_btn.configure(state='normal')
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error cargando datos del punto de venta: {str(e)}")
    
    def edit_sales_point(self):
        """Enable sales point editing"""
        if self.current_sales_point_id:
            self.save_btn.configure(text="💾 Actualizar")
    
    def clear_form(self):
        """Clear sales point form"""
        self.current_sales_point_id = None
        self.name_var.set('')
        self.type_var.set('')
        self.contact_person_var.set('')
        self.email_var.set('')
        self.phone_var.set('')
        self.address_text.delete(1.0, tk.END)
        self.capacity_text.delete(1.0, tk.END)
        self.save_btn.configure(text="💾 Guardar")
        self.edit_btn.configure(state='disabled')
    
    def filter_sales_points(self, *args):
        """Filter sales points based on search and type"""
        search_term = self.search_var.get().lower()
        type_filter = self.type_filter_var.get()
        
        # Clear current items
        for item in self.sales_points_tree.get_children():
            self.sales_points_tree.delete(item)
        
        try:
            sales_points = self.db.get_sales_points()
            for sp in sales_points:
                # Apply type filter
                if type_filter and type_filter != 'Todos' and sp['type'] != type_filter:
                    continue
                
                # Apply search filter
                if search_term:
                    searchable_text = f"{sp['name']} {sp['type']} {sp['contact_person'] or ''} {sp['address']}".lower()
                    if search_term not in searchable_text:
                        continue
                
                self.sales_points_tree.insert('', 'end', values=(
                    sp['id'],
                    sp['name'],
                    sp['type'],
                    sp['contact_person'] or '',
                    sp['phone'] or '',
                    sp['address']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error filtrando puntos de venta: {str(e)}")
