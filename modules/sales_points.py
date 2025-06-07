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
                  command=self.show_sales_point_modal).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_sales_points).pack(side='left')
        
        # Main content frame - now full width for the list
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Sales points list (now takes full width)
        list_frame = ttk.LabelFrame(content_frame, text="Lista de Puntos de Venta", padding=10)
        list_frame.pack(fill='both', expand=True)
        
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
        type_combo.pack(side='left', padx=(5, 10))
        
        # Action buttons for selected items
        action_frame = ttk.Frame(search_frame)
        action_frame.pack(side='right')
        
        self.edit_btn = ttk.Button(action_frame, text="✏️ Editar", 
                                 style='Secondary.TButton',
                                 command=self.edit_selected_sales_point, state='disabled')
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        self.delete_btn = ttk.Button(action_frame, text="🗑️ Eliminar", 
                                   style='Danger.TButton',
                                   command=self.delete_sales_point, state='disabled')
        self.delete_btn.pack(side='left')
        
        # Treeview container frame
        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill='both', expand=True)
        
        # Sales points treeview
        columns = ('ID', 'Nombre', 'Tipo', 'Contacto', 'Teléfono', 'Email', 'Dirección')
        self.sales_points_tree = ttk.Treeview(tree_container, columns=columns, show='headings', 
                                            style='Custom.Treeview', height=20)
        
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
        scrollbar_y = ttk.Scrollbar(tree_container, orient='vertical', command=self.sales_points_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_container, orient='horizontal', command=self.sales_points_tree.xview)
        self.sales_points_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Grid layout for tree and scrollbars
        self.sales_points_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.sales_points_tree.bind('<<TreeviewSelect>>', self.on_sales_point_select)
        self.sales_points_tree.bind('<Double-1>', self.on_double_click)
        
        # Load sales points
        self.refresh_sales_points()
    
    def show_sales_point_modal(self, sales_point_data=None):
        """Show modal dialog for creating/editing sales point"""
        # Create modal window
        modal = tk.Toplevel(self.parent)
        modal.title("Nuevo Punto de Venta" if not sales_point_data else "Editar Punto de Venta")
        modal.geometry("600x650")
        modal.resizable(False, False)
        modal.transient(self.parent)
        modal.grab_set()
        
        # Center the modal
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (modal.winfo_width() // 2)
        y = (modal.winfo_screenheight() // 2) - (modal.winfo_height() // 2)
        modal.geometry(f"+{x}+{y}")
        
        # Configure modal styling
        modal.configure(bg='#f0f0f0')
        
        # Main frame with padding
        main_frame = ttk.Frame(modal, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="Nuevo Punto de Venta" if not sales_point_data else "Editar Punto de Venta",
                               style='Heading.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Form fields frame (no scroll needed now)
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Variables for form fields
        name_var = tk.StringVar()
        type_var = tk.StringVar()
        contact_person_var = tk.StringVar()
        email_var = tk.StringVar()
        phone_var = tk.StringVar()
        
        # Row 1: Name field (full width)
        name_frame = ttk.Frame(fields_frame)
        name_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(name_frame, text="Nombre *:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        name_entry = ttk.Entry(name_frame, textvariable=name_var, 
                              style='Custom.TEntry', font=('Segoe UI', 10))
        name_entry.pack(fill='x', ipady=5)
        
        # Row 2: Type and Contact Person (side by side)
        row2_frame = ttk.Frame(fields_frame)
        row2_frame.pack(fill='x', pady=(0, 15))
        
        # Type (left side)
        type_frame = ttk.Frame(row2_frame)
        type_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(type_frame, text="Tipo *:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, 
                                style='Custom.TCombobox', font=('Segoe UI', 10))
        type_combo['values'] = ['Supermercado', 'Tienda Local', 'Restaurante', 'Mercado', 'Distribuidor', 'Otro']
        type_combo.pack(fill='x', ipady=5)
        
        # Contact Person (right side)
        contact_frame = ttk.Frame(row2_frame)
        contact_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(contact_frame, text="Persona de Contacto:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        contact_entry = ttk.Entry(contact_frame, textvariable=contact_person_var, 
                                 style='Custom.TEntry', font=('Segoe UI', 10))
        contact_entry.pack(fill='x', ipady=5)
        
        # Row 3: Email and Phone (side by side)
        row3_frame = ttk.Frame(fields_frame)
        row3_frame.pack(fill='x', pady=(0, 15))
        
        # Email (left side)
        email_frame = ttk.Frame(row3_frame)
        email_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Label(email_frame, text="Email:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        email_entry = ttk.Entry(email_frame, textvariable=email_var, 
                               style='Custom.TEntry', font=('Segoe UI', 10))
        email_entry.pack(fill='x', ipady=5)
        
        # Phone (right side)
        phone_frame = ttk.Frame(row3_frame)
        phone_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(phone_frame, text="Teléfono:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        phone_entry = ttk.Entry(phone_frame, textvariable=phone_var, 
                               style='Custom.TEntry', font=('Segoe UI', 10))
        phone_entry.pack(fill='x', ipady=5)
        
        # Row 4: Address (full width)
        address_main_frame = ttk.Frame(fields_frame)
        address_main_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(address_main_frame, text="Dirección *:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        address_frame = ttk.Frame(address_main_frame)
        address_frame.pack(fill='x')
        
        address_text = tk.Text(address_frame, height=4, font=('Segoe UI', 10), 
                              wrap=tk.WORD, relief='solid', borderwidth=1)
        address_scrollbar = ttk.Scrollbar(address_frame, orient='vertical', command=address_text.yview)
        address_text.configure(yscrollcommand=address_scrollbar.set)
        
        address_text.pack(side='left', fill='both', expand=True)
        address_scrollbar.pack(side='right', fill='y')
        
        # Row 5: Capacity info (full width)
        capacity_main_frame = ttk.Frame(fields_frame)
        capacity_main_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(capacity_main_frame, text="Información de Capacidad:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        capacity_frame = ttk.Frame(capacity_main_frame)
        capacity_frame.pack(fill='x')
        
        capacity_text = tk.Text(capacity_frame, height=3, font=('Segoe UI', 10), 
                               wrap=tk.WORD, relief='solid', borderwidth=1)
        capacity_scrollbar = ttk.Scrollbar(capacity_frame, orient='vertical', command=capacity_text.yview)
        capacity_text.configure(yscrollcommand=capacity_scrollbar.set)
        
        capacity_text.pack(side='left', fill='both', expand=True)
        capacity_scrollbar.pack(side='right', fill='y')
        
        # Load existing data if editing
        if sales_point_data:
            name_var.set(sales_point_data['name'])
            type_var.set(sales_point_data['type'])
            contact_person_var.set(sales_point_data['contact_person'] or '')
            email_var.set(sales_point_data['email'] or '')
            phone_var.set(sales_point_data['phone'] or '')
            address_text.insert(1.0, sales_point_data['address'])
            if sales_point_data['capacity_info']:
                capacity_text.insert(1.0, sales_point_data['capacity_info'])
        
        # Buttons frame at the bottom
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        def save_and_close():
            """Save sales point and close modal"""
            try:
                # Validate required fields
                if not name_var.get().strip():
                    messagebox.showerror("Error", "El nombre es obligatorio", parent=modal)
                    name_entry.focus()
                    return
                
                if not type_var.get().strip():
                    messagebox.showerror("Error", "El tipo es obligatorio", parent=modal)
                    type_combo.focus()
                    return
                
                address = address_text.get(1.0, tk.END).strip()
                if not address:
                    messagebox.showerror("Error", "La dirección es obligatoria", parent=modal)
                    address_text.focus()
                    return
                
                # Validate email if provided
                email = email_var.get().strip()
                if email and not Validator.is_valid_email(email):
                    messagebox.showerror("Error", "El formato del email no es válido", parent=modal)
                    email_entry.focus()
                    return
                
                # Prepare sales point data
                sp_data = {
                    'name': name_var.get().strip(),
                    'type': type_var.get().strip(),
                    'contact_person': contact_person_var.get().strip() if contact_person_var.get().strip() else None,
                    'email': email if email else None,
                    'phone': phone_var.get().strip() if phone_var.get().strip() else None,
                    'address': address,
                    'capacity_info': capacity_text.get(1.0, tk.END).strip() if capacity_text.get(1.0, tk.END).strip() else None
                }
                
                if sales_point_data:
                    # Update existing sales point
                    self.db.update_sales_point(sales_point_data['id'], sp_data)
                    messagebox.showinfo("Éxito", "Punto de venta actualizado correctamente", parent=modal)
                else:
                    # Add new sales point
                    sales_point_id = self.db.add_sales_point(sp_data)
                    messagebox.showinfo("Éxito", f"Punto de venta agregado con ID: {sales_point_id}", parent=modal)
                
                self.refresh_sales_points()
                modal.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando punto de venta: {str(e)}", parent=modal)
        
        def cancel_and_close():
            """Cancel and close modal"""
            modal.destroy()
        
        # Cancel button (left)
        cancel_btn = ttk.Button(buttons_frame, text="❌ Cancelar", 
                               style='Secondary.TButton',
                               command=cancel_and_close)
        cancel_btn.pack(side='left')
        
        # Save button (right)
        save_btn = ttk.Button(buttons_frame, text="💾 Guardar", 
                             style='Primary.TButton',
                             command=save_and_close)
        save_btn.pack(side='right')
        
        # Focus on first field
        name_entry.focus()
        
        # Handle window close
        modal.protocol("WM_DELETE_WINDOW", cancel_and_close)
        
        # Bind Enter key to save (when not in text widgets)
        def on_enter(event):
            if event.widget not in [address_text, capacity_text]:
                save_and_close()
        
        # Bind Tab key for better navigation
        def on_tab(event):
            event.widget.tk_focusNext().focus()
            return "break"
        
        modal.bind('<Return>', on_enter)
        modal.bind('<Escape>', lambda e: cancel_and_close())
        
        # Set tab order for better navigation
        name_entry.bind('<Tab>', on_tab)
        type_combo.bind('<Tab>', on_tab)
        contact_entry.bind('<Tab>', on_tab)
        email_entry.bind('<Tab>', on_tab)
        phone_entry.bind('<Tab>', on_tab)
    
    def edit_selected_sales_point(self):
        """Edit the selected sales point"""
        selection = self.sales_points_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un punto de venta para editar")
            return
        
        item = self.sales_points_tree.item(selection[0])
        sales_point_id = item['values'][0]
        
        # Get full sales point data
        try:
            sales_points = self.db.get_sales_points()
            selected_sp = next((sp for sp in sales_points if sp['id'] == sales_point_id), None)
            
            if selected_sp:
                self.show_sales_point_modal(selected_sp)
            else:
                messagebox.showerror("Error", "No se pudo cargar la información del punto de venta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos del punto de venta: {str(e)}")
    
    def on_double_click(self, event):
        """Handle double click on tree item"""
        self.edit_selected_sales_point()
    
    def delete_sales_point(self):
        """Delete selected sales point"""
        selection = self.sales_points_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un punto de venta para eliminar")
            return
        
        item = self.sales_points_tree.item(selection[0])
        sales_point_id = item['values'][0]
        sales_point_name = item['values'][1]
        
        # Confirm deletion
        result = messagebox.askyesno("Confirmar", 
                                   f"¿Está seguro de que desea eliminar el punto de venta:\n\n"
                                   f"'{sales_point_name}'?\n\n"
                                   "Esta acción no se puede deshacer.")
        
        if result:
            try:
                self.db.delete_sales_point(sales_point_id)
                messagebox.showinfo("Éxito", "Punto de venta eliminado correctamente")
                self.refresh_sales_points()
                self.edit_btn.configure(state='disabled')
                self.delete_btn.configure(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando punto de venta: {str(e)}")
    
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
                    sp['email'] or '',
                    sp['address']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando puntos de venta: {str(e)}")
    
    def on_sales_point_select(self, event):
        """Handle sales point selection"""
        selection = self.sales_points_tree.selection()
        if selection:
            self.edit_btn.configure(state='normal')
            self.delete_btn.configure(state='normal')
        else:
            self.edit_btn.configure(state='disabled')
            self.delete_btn.configure(state='disabled')
    
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
                    searchable_text = f"{sp['name']} {sp['type']} {sp['contact_person'] or ''} {sp['address']} {sp['email'] or ''}".lower()
                    if search_term not in searchable_text:
                        continue
                
                self.sales_points_tree.insert('', 'end', values=(
                    sp['id'],
                    sp['name'],
                    sp['type'],
                    sp['contact_person'] or '',
                    sp['phone'] or '',
                    sp['email'] or '',
                    sp['address']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error filtrando puntos de venta: {str(e)}")