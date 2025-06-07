import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import sqlite3

class ReportsModule:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.frame = None
        
    def show(self):
        """Show the reports module"""
        if self.frame:
            self.frame.destroy()
        
        self.frame = ttk.Frame(self.parent, style='Card.TFrame')
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_reports_interface()
        
    def hide(self):
        """Hide the reports module"""
        if self.frame:
            self.frame.destroy()
            self.frame = None
    
    def create_reports_interface(self):
        """Create the reports and analytics interface"""
        # Create notebook for different report types
        notebook = ttk.Notebook(self.frame, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Inventory report tab
        inventory_tab = ttk.Frame(notebook)
        notebook.add(inventory_tab, text="Inventario y Stock")
        
        # Sales activity tab
        activity_tab = ttk.Frame(notebook)
        notebook.add(activity_tab, text="Actividad de Ventas")
        
        # Waste analysis tab
        waste_tab = ttk.Frame(notebook)
        notebook.add(waste_tab, text="Análisis de Desperdicios")
        
        # Financial summary tab
        financial_tab = ttk.Frame(notebook)
        notebook.add(financial_tab, text="Resumen Financiero")
        
        # Create report interfaces
        self.create_inventory_report(inventory_tab)
        self.create_activity_report(activity_tab)
        self.create_waste_analysis(waste_tab)
        self.create_financial_summary(financial_tab)
    
    def create_inventory_report(self, parent):
        """Create inventory and stock report interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Reporte de Inventario y Stock", style='Heading.TLabel').pack(side='left')
        
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_inventory_report).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="📊 Exportar", 
                  style='Primary.TButton',
                  command=self.export_inventory_report).pack(side='left')
        
        # Filter frame
        filter_frame = ttk.LabelFrame(parent, text="Filtros", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Category filter
        ttk.Label(filter_frame, text="Categoría:").pack(side='left')
        self.inv_category_var = tk.StringVar()
        category_combo = ttk.Combobox(filter_frame, textvariable=self.inv_category_var, 
                                    style='Custom.TCombobox', state='readonly', width=15)
        category_combo['values'] = ['Todas', 'Verduras', 'Frutas', 'Granos', 'Legumbres', 'Hierbas', 'Otros']
        category_combo.set('Todas')
        category_combo.pack(side='left', padx=(5, 15))
        
        # Stock level filter
        ttk.Label(filter_frame, text="Nivel de Stock:").pack(side='left')
        self.stock_level_var = tk.StringVar()
        stock_combo = ttk.Combobox(filter_frame, textvariable=self.stock_level_var, 
                                 style='Custom.TCombobox', state='readonly', width=15)
        stock_combo['values'] = ['Todos', 'Stock Alto', 'Stock Medio', 'Stock Bajo', 'Sin Stock']
        stock_combo.set('Todos')
        stock_combo.pack(side='left', padx=(5, 15))
        
        # Update button for filters
        ttk.Button(filter_frame, text="Aplicar Filtros", 
                  style='Secondary.TButton',
                  command=self.apply_inventory_filters).pack(side='left', padx=(15, 0))
        
        # Summary statistics
        stats_frame = ttk.LabelFrame(parent, text="Estadísticas de Inventario", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.inventory_stats_frame = ttk.Frame(stats_frame)
        self.inventory_stats_frame.pack(fill='x')
        
        # Inventory details table
        details_frame = ttk.LabelFrame(parent, text="Detalles de Inventario", padding=10)
        details_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Inventory treeview
        inv_columns = ('Producto', 'Categoría', 'Agricultor', 'Cantidad', 'Unidad', 'Precio/Unidad', 'Valor Total', 'Vencimiento', 'Estado')
        self.inventory_tree = ttk.Treeview(details_frame, columns=inv_columns, show='headings', 
                                         style='Custom.Treeview', height=12)
        
        for col in inv_columns:
            self.inventory_tree.heading(col, text=col)
            if col in ['Producto', 'Agricultor']:
                self.inventory_tree.column(col, width=120, minwidth=100)
            elif col == 'Categoría':
                self.inventory_tree.column(col, width=100, minwidth=80)
            elif col in ['Cantidad', 'Unidad', 'Estado']:
                self.inventory_tree.column(col, width=80, minwidth=70)
            else:
                self.inventory_tree.column(col, width=100, minwidth=90)
        
        # Scrollbars
        inv_scrollbar_y = ttk.Scrollbar(details_frame, orient='vertical', command=self.inventory_tree.yview)
        inv_scrollbar_x = ttk.Scrollbar(details_frame, orient='horizontal', command=self.inventory_tree.xview)
        self.inventory_tree.configure(yscrollcommand=inv_scrollbar_y.set, xscrollcommand=inv_scrollbar_x.set)
        
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        inv_scrollbar_y.pack(side='right', fill='y')
        inv_scrollbar_x.pack(side='bottom', fill='x')
        
        # Load initial data
        self.refresh_inventory_report()
    
    def create_activity_report(self, parent):
        """Create sales activity report interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Reporte de Actividad de Ventas", style='Heading.TLabel').pack(side='left')
        
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_activity_report).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="📊 Exportar", 
                  style='Primary.TButton',
                  command=self.export_activity_report).pack(side='left')
        
        # Date range filter
        date_frame = ttk.LabelFrame(parent, text="Rango de Fechas", padding=10)
        date_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(date_frame, text="Desde:").pack(side='left')
        self.start_date_var = tk.StringVar()
        self.start_date_var.set((datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        ttk.Entry(date_frame, textvariable=self.start_date_var, 
                 style='Custom.TEntry', width=12).pack(side='left', padx=(5, 15))
        
        ttk.Label(date_frame, text="Hasta:").pack(side='left')
        self.end_date_var = tk.StringVar()
        self.end_date_var.set(datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(date_frame, textvariable=self.end_date_var, 
                 style='Custom.TEntry', width=12).pack(side='left', padx=(5, 15))
        
        ttk.Button(date_frame, text="Aplicar Rango", 
                  style='Secondary.TButton',
                  command=self.apply_date_range).pack(side='left', padx=(15, 0))
        
        # Activity summary
        summary_frame = ttk.LabelFrame(parent, text="Resumen de Actividad", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.activity_summary_frame = ttk.Frame(summary_frame)
        self.activity_summary_frame.pack(fill='x')
        
        # Recent transactions
        transactions_frame = ttk.LabelFrame(parent, text="Transacciones Recientes", padding=10)
        transactions_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Transactions treeview
        trans_columns = ('Fecha', 'Tipo', 'Producto', 'Agricultor', 'Punto de Venta', 'Cantidad', 'Valor')
        self.transactions_tree = ttk.Treeview(transactions_frame, columns=trans_columns, show='headings', 
                                            style='Custom.Treeview', height=12)
        
        for col in trans_columns:
            self.transactions_tree.heading(col, text=col)
            if col == 'Fecha':
                self.transactions_tree.column(col, width=100, minwidth=90)
            elif col in ['Producto', 'Agricultor', 'Punto de Venta']:
                self.transactions_tree.column(col, width=120, minwidth=100)
            else:
                self.transactions_tree.column(col, width=80, minwidth=70)
        
        # Scrollbars
        trans_scrollbar_y = ttk.Scrollbar(transactions_frame, orient='vertical', command=self.transactions_tree.yview)
        trans_scrollbar_x = ttk.Scrollbar(transactions_frame, orient='horizontal', command=self.transactions_tree.xview)
        self.transactions_tree.configure(yscrollcommand=trans_scrollbar_y.set, xscrollcommand=trans_scrollbar_x.set)
        
        self.transactions_tree.pack(side='left', fill='both', expand=True)
        trans_scrollbar_y.pack(side='right', fill='y')
        trans_scrollbar_x.pack(side='bottom', fill='x')
        
        # Load initial data
        self.refresh_activity_report()
    
    def create_waste_analysis(self, parent):
        """Create waste analysis report interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Análisis de Desperdicios", style='Heading.TLabel').pack(side='left')
        
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_waste_analysis).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="📊 Exportar", 
                  style='Primary.TButton',
                  command=self.export_waste_analysis).pack(side='left')
        
        # Waste metrics
        metrics_frame = ttk.LabelFrame(parent, text="Métricas de Desperdicios", padding=10)
        metrics_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.waste_metrics_frame = ttk.Frame(metrics_frame)
        self.waste_metrics_frame.pack(fill='x')
        
        # Products at risk
        risk_frame = ttk.LabelFrame(parent, text="Productos en Riesgo", padding=10)
        risk_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Risk products treeview
        risk_columns = ('Producto', 'Agricultor', 'Cantidad', 'Vencimiento', 'Días Restantes', 'Riesgo')
        self.risk_tree = ttk.Treeview(risk_frame, columns=risk_columns, show='headings', 
                                    style='Custom.Treeview', height=10)
        
        for col in risk_columns:
            self.risk_tree.heading(col, text=col)
            if col in ['Producto', 'Agricultor']:
                self.risk_tree.column(col, width=120, minwidth=100)
            elif col == 'Vencimiento':
                self.risk_tree.column(col, width=100, minwidth=90)
            else:
                self.risk_tree.column(col, width=80, minwidth=70)
        
        # Scrollbars
        risk_scrollbar_y = ttk.Scrollbar(risk_frame, orient='vertical', command=self.risk_tree.yview)
        self.risk_tree.configure(yscrollcommand=risk_scrollbar_y.set)
        
        self.risk_tree.pack(side='left', fill='both', expand=True)
        risk_scrollbar_y.pack(side='right', fill='y')
        
        # Recommendations
        recommendations_frame = ttk.LabelFrame(parent, text="Recomendaciones", padding=10)
        recommendations_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.recommendations_text = tk.Text(recommendations_frame, height=6, font=('Segoe UI', 10), wrap=tk.WORD)
        self.recommendations_text.pack(fill='x')
        
        # Load initial data
        self.refresh_waste_analysis()
    
    def create_financial_summary(self, parent):
        """Create financial summary report interface"""
        # Title and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Resumen Financiero", style='Heading.TLabel').pack(side='left')
        
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  style='Secondary.TButton',
                  command=self.refresh_financial_summary).pack(side='left', padx=(0, 5))
        
        ttk.Button(controls_frame, text="📊 Exportar", 
                  style='Primary.TButton',
                  command=self.export_financial_summary).pack(side='left')
        
        # Financial metrics
        financial_frame = ttk.LabelFrame(parent, text="Métricas Financieras", padding=10)
        financial_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.financial_metrics_frame = ttk.Frame(financial_frame)
        self.financial_metrics_frame.pack(fill='x')
        
        # Revenue by category
        category_frame = ttk.LabelFrame(parent, text="Ingresos por Categoría", padding=10)
        category_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Category revenue treeview
        cat_columns = ('Categoría', 'Productos Vendidos', 'Cantidad Total', 'Ingresos Totales', 'Precio Promedio')
        self.category_tree = ttk.Treeview(category_frame, columns=cat_columns, show='headings', 
                                        style='Custom.Treeview', height=8)
        
        for col in cat_columns:
            self.category_tree.heading(col, text=col)
            if col == 'Categoría':
                self.category_tree.column(col, width=120, minwidth=100)
            else:
                self.category_tree.column(col, width=120, minwidth=100)
        
        # Scrollbars
        cat_scrollbar_y = ttk.Scrollbar(category_frame, orient='vertical', command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=cat_scrollbar_y.set)
        
        self.category_tree.pack(side='left', fill='both', expand=True)
        cat_scrollbar_y.pack(side='right', fill='y')
        
        # Top performers
        performers_frame = ttk.LabelFrame(parent, text="Mejores Rendimientos", padding=10)
        performers_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.performers_text = tk.Text(performers_frame, height=6, font=('Segoe UI', 10), wrap=tk.WORD)
        self.performers_text.pack(fill='x')
        
        # Load initial data
        self.refresh_financial_summary()
    
    def refresh_inventory_report(self):
        """Refresh inventory report data"""
        try:
            # Clear existing data
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
            
            # Clear stats frame
            for widget in self.inventory_stats_frame.winfo_children():
                widget.destroy()
            
            # Get products data
            products = self.db.get_products(available_only=True)
            
            # Calculate statistics
            total_products = len(products)
            total_value = sum(p['quantity'] * p['price_per_unit'] for p in products)
            categories = set(p['category'] for p in products)
            
            # Create stats cards
            stats_data = [
                ("📦", "Total Productos", total_products),
                ("💰", "Valor Total", f"${total_value:.2f}"),
                ("📂", "Categorías", len(categories)),
                ("⚠️", "Por Vencer", self.count_expiring_products(products))
            ]
            
            for i, (icon, label, value) in enumerate(stats_data):
                card = ttk.Frame(self.inventory_stats_frame, style='Card.TFrame', relief='raised', borderwidth=1)
                card.pack(side='left', fill='both', expand=True, padx=(0, 10) if i < len(stats_data)-1 else (0, 0))
                
                icon_frame = ttk.Frame(card)
                icon_frame.pack(pady=10)
                
                ttk.Label(icon_frame, text=icon, font=('Segoe UI', 16)).pack()
                ttk.Label(icon_frame, text=str(value), style='StatValue.TLabel').pack()
                ttk.Label(icon_frame, text=label, style='StatLabel.TLabel').pack()
            
            # Populate inventory tree
            for product in products:
                # Determine status based on expiry date
                status = self.get_product_status(product)
                total_value = product['quantity'] * product['price_per_unit']
                
                self.inventory_tree.insert('', 'end', values=(
                    product['name'],
                    product['category'],
                    product['farmer_name'],
                    f"{product['quantity']:.2f}",
                    product['unit'],
                    f"${product['price_per_unit']:.2f}",
                    f"${total_value:.2f}",
                    product['expiry_date'] or 'N/A',
                    status
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando reporte de inventario: {str(e)}")
    
    def refresh_activity_report(self):
        """Refresh activity report data"""
        try:
            # Clear existing data
            for item in self.transactions_tree.get_children():
                self.transactions_tree.delete(item)
            
            # Clear summary frame
            for widget in self.activity_summary_frame.winfo_children():
                widget.destroy()
            
            # Get activity data (simulated for now)
            # In a real implementation, this would come from distribution_assignments table
            
            # Create summary stats
            summary_data = [
                ("📋", "Solicitudes Activas", 0),
                ("✅", "Completadas", 0),
                ("🚚", "En Tránsito", 0),
                ("💸", "Valor Movido", "$0.00")
            ]
            
            for i, (icon, label, value) in enumerate(summary_data):
                card = ttk.Frame(self.activity_summary_frame, style='Card.TFrame', relief='raised', borderwidth=1)
                card.pack(side='left', fill='both', expand=True, padx=(0, 10) if i < len(summary_data)-1 else (0, 0))
                
                icon_frame = ttk.Frame(card)
                icon_frame.pack(pady=10)
                
                ttk.Label(icon_frame, text=icon, font=('Segoe UI', 16)).pack()
                ttk.Label(icon_frame, text=str(value), style='StatValue.TLabel').pack()
                ttk.Label(icon_frame, text=label, style='StatLabel.TLabel').pack()
            
            # Add sample transaction (in real implementation, this would come from database)
            self.transactions_tree.insert('', 'end', values=(
                datetime.now().strftime('%Y-%m-%d'),
                'Producto Agregado',
                'Ejemplo',
                'Sin datos',
                'Sin datos',
                'N/A',
                'N/A'
            ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando reporte de actividad: {str(e)}")
    
    def refresh_waste_analysis(self):
        """Refresh waste analysis data"""
        try:
            # Clear existing data
            for item in self.risk_tree.get_children():
                self.risk_tree.delete(item)
            
            # Clear metrics frame
            for widget in self.waste_metrics_frame.winfo_children():
                widget.destroy()
            
            # Get products at risk
            products = self.db.get_products(available_only=True)
            risk_products = []
            
            for product in products:
                if product['expiry_date']:
                    try:
                        expiry_date = datetime.strptime(product['expiry_date'], '%Y-%m-%d')
                        days_remaining = (expiry_date - datetime.now()).days
                        
                        if days_remaining <= 7:  # Products expiring within 7 days
                            risk_level = "🔴 Alto" if days_remaining <= 2 else "🟡 Medio"
                            risk_products.append({
                                'product': product,
                                'days_remaining': days_remaining,
                                'risk_level': risk_level
                            })
                    except ValueError:
                        continue
            
            # Calculate metrics
            total_at_risk = len(risk_products)
            high_risk = len([p for p in risk_products if "Alto" in p['risk_level']])
            estimated_loss = sum(p['product']['quantity'] * p['product']['price_per_unit'] 
                               for p in risk_products if p['days_remaining'] <= 2)
            
            # Create metrics cards
            metrics_data = [
                ("⚠️", "Productos en Riesgo", total_at_risk),
                ("🔴", "Riesgo Alto", high_risk),
                ("💸", "Pérdida Estimada", f"${estimated_loss:.2f}"),
                ("📊", "Tasa de Riesgo", f"{(total_at_risk/len(products)*100):.1f}%" if products else "0%")
            ]
            
            for i, (icon, label, value) in enumerate(metrics_data):
                card = ttk.Frame(self.waste_metrics_frame, style='Card.TFrame', relief='raised', borderwidth=1)
                card.pack(side='left', fill='both', expand=True, padx=(0, 10) if i < len(metrics_data)-1 else (0, 0))
                
                icon_frame = ttk.Frame(card)
                icon_frame.pack(pady=10)
                
                ttk.Label(icon_frame, text=icon, font=('Segoe UI', 16)).pack()
                ttk.Label(icon_frame, text=str(value), style='StatValue.TLabel').pack()
                ttk.Label(icon_frame, text=label, style='StatLabel.TLabel').pack()
            
            # Populate risk tree
            for risk_item in sorted(risk_products, key=lambda x: x['days_remaining']):
                product = risk_item['product']
                self.risk_tree.insert('', 'end', values=(
                    product['name'],
                    product['farmer_name'],
                    f"{product['quantity']:.2f} {product['unit']}",
                    product['expiry_date'],
                    risk_item['days_remaining'],
                    risk_item['risk_level']
                ))
            
            # Generate recommendations
            self.recommendations_text.delete(1.0, tk.END)
            
            if risk_products:
                self.recommendations_text.insert('end', "🎯 RECOMENDACIONES PARA REDUCIR DESPERDICIOS:\n\n", 'header')
                
                if high_risk > 0:
                    self.recommendations_text.insert('end', f"• URGENTE: {high_risk} productos requieren acción inmediata\n")
                    self.recommendations_text.insert('end', "• Considere ofertas especiales o descuentos para productos próximos a vencer\n")
                
                self.recommendations_text.insert('end', "• Priorice la distribución de productos con fechas de vencimiento próximas\n")
                self.recommendations_text.insert('end', "• Contacte puntos de venta que acepten productos con descuento\n")
                self.recommendations_text.insert('end', "• Evalúe donaciones a organizaciones benéficas\n")
            else:
                self.recommendations_text.insert('end', "✅ Excelente gestión de inventario.\n", 'success')
                self.recommendations_text.insert('end', "No hay productos en riesgo inmediato de desperdicio.")
            
            # Configure text tags
            self.recommendations_text.tag_configure('header', font=('Segoe UI', 11, 'bold'), foreground='#2E7D32')
            self.recommendations_text.tag_configure('success', font=('Segoe UI', 11, 'bold'), foreground='#4CAF50')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando análisis de desperdicios: {str(e)}")
    
    def refresh_financial_summary(self):
        """Refresh financial summary data"""
        try:
            # Clear existing data
            for item in self.category_tree.get_children():
                self.category_tree.delete(item)
            
            # Clear metrics frame
            for widget in self.financial_metrics_frame.winfo_children():
                widget.destroy()
            
            # Get financial data
            products = self.db.get_products(available_only=True)
            
            # Calculate category-wise data
            category_data = {}
            for product in products:
                category = product['category']
                if category not in category_data:
                    category_data[category] = {
                        'count': 0,
                        'total_quantity': 0,
                        'total_value': 0,
                        'prices': []
                    }
                
                category_data[category]['count'] += 1
                category_data[category]['total_quantity'] += product['quantity']
                category_data[category]['total_value'] += product['quantity'] * product['price_per_unit']
                category_data[category]['prices'].append(product['price_per_unit'])
            
            # Calculate overall metrics
            total_inventory_value = sum(data['total_value'] for data in category_data.values())
            total_products = sum(data['count'] for data in category_data.values())
            avg_price = sum(p['price_per_unit'] for p in products) / len(products) if products else 0
            
            # Create financial metrics cards
            financial_data = [
                ("💰", "Valor Inventario", f"${total_inventory_value:.2f}"),
                ("📦", "Total Productos", total_products),
                ("📊", "Precio Promedio", f"${avg_price:.2f}"),
                ("📂", "Categorías Activas", len(category_data))
            ]
            
            for i, (icon, label, value) in enumerate(financial_data):
                card = ttk.Frame(self.financial_metrics_frame, style='Card.TFrame', relief='raised', borderwidth=1)
                card.pack(side='left', fill='both', expand=True, padx=(0, 10) if i < len(financial_data)-1 else (0, 0))
                
                icon_frame = ttk.Frame(card)
                icon_frame.pack(pady=10)
                
                ttk.Label(icon_frame, text=icon, font=('Segoe UI', 16)).pack()
                ttk.Label(icon_frame, text=str(value), style='StatValue.TLabel').pack()
                ttk.Label(icon_frame, text=label, style='StatLabel.TLabel').pack()
            
            # Populate category tree
            for category, data in sorted(category_data.items(), key=lambda x: x[1]['total_value'], reverse=True):
                avg_category_price = sum(data['prices']) / len(data['prices']) if data['prices'] else 0
                
                self.category_tree.insert('', 'end', values=(
                    category,
                    data['count'],
                    f"{data['total_quantity']:.2f}",
                    f"${data['total_value']:.2f}",
                    f"${avg_category_price:.2f}"
                ))
            
            # Generate top performers analysis
            self.performers_text.delete(1.0, tk.END)
            
            if category_data:
                self.performers_text.insert('end', "🏆 ANÁLISIS DE RENDIMIENTO:\n\n", 'header')
                
                # Top category by value
                top_category = max(category_data.items(), key=lambda x: x[1]['total_value'])
                self.performers_text.insert('end', f"• Categoría más valiosa: {top_category[0]} (${top_category[1]['total_value']:.2f})\n")
                
                # Most diverse category
                most_products = max(category_data.items(), key=lambda x: x[1]['count'])
                self.performers_text.insert('end', f"• Mayor diversidad: {most_products[0]} ({most_products[1]['count']} productos)\n")
                
                # Highest average price
                highest_avg = max(category_data.items(), 
                                key=lambda x: sum(x[1]['prices'])/len(x[1]['prices']) if x[1]['prices'] else 0)
                avg_price_value = sum(highest_avg[1]['prices'])/len(highest_avg[1]['prices']) if highest_avg[1]['prices'] else 0
                self.performers_text.insert('end', f"• Precio promedio más alto: {highest_avg[0]} (${avg_price_value:.2f})\n")
                
                self.performers_text.insert('end', "\n💡 OPORTUNIDADES:\n")
                self.performers_text.insert('end', "• Considere expandir las categorías más exitosas\n")
                self.performers_text.insert('end', "• Evalúe estrategias de precio para categorías de menor valor\n")
            else:
                self.performers_text.insert('end', "No hay datos suficientes para análisis de rendimiento.")
            
            # Configure text tags
            self.performers_text.tag_configure('header', font=('Segoe UI', 11, 'bold'), foreground='#2E7D32')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando resumen financiero: {str(e)}")
    
    def count_expiring_products(self, products):
        """Count products expiring within 7 days"""
        count = 0
        for product in products:
            if product['expiry_date']:
                try:
                    expiry_date = datetime.strptime(product['expiry_date'], '%Y-%m-%d')
                    days_remaining = (expiry_date - datetime.now()).days
                    if days_remaining <= 7:
                        count += 1
                except ValueError:
                    continue
        return count
    
    def get_product_status(self, product):
        """Get product status based on expiry date"""
        if not product['expiry_date']:
            return "🟢 Bueno"
        
        try:
            expiry_date = datetime.strptime(product['expiry_date'], '%Y-%m-%d')
            days_remaining = (expiry_date - datetime.now()).days
            
            if days_remaining <= 0:
                return "🔴 Vencido"
            elif days_remaining <= 2:
                return "🔴 Crítico"
            elif days_remaining <= 7:
                return "🟡 Alerta"
            else:
                return "🟢 Bueno"
        except ValueError:
            return "❓ Desconocido"
    
    def apply_inventory_filters(self):
        """Apply filters to inventory report"""
        self.refresh_inventory_report()
    
    def apply_date_range(self):
        """Apply date range filter to activity report"""
        self.refresh_activity_report()
    
    def export_inventory_report(self):
        """Export inventory report to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar Reporte de Inventario"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("REPORTE DE INVENTARIO\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    # Export inventory data
                    products = self.db.get_products(available_only=True)
                    for product in products:
                        f.write(f"Producto: {product['name']}\n")
                        f.write(f"Categoría: {product['category']}\n")
                        f.write(f"Agricultor: {product['farmer_name']}\n")
                        f.write(f"Cantidad: {product['quantity']} {product['unit']}\n")
                        f.write(f"Precio: ${product['price_per_unit']:.2f}\n")
                        f.write(f"Vencimiento: {product['expiry_date'] or 'N/A'}\n")
                        f.write("-" * 30 + "\n")
                
                messagebox.showinfo("Éxito", f"Reporte exportado a: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando reporte: {str(e)}")
    
    def export_activity_report(self):
        """Export activity report to file"""
        messagebox.showinfo("Información", "Funcionalidad de exportación en desarrollo")
    
    def export_waste_analysis(self):
        """Export waste analysis to file"""
        messagebox.showinfo("Información", "Funcionalidad de exportación en desarrollo")
    
    def export_financial_summary(self):
        """Export financial summary to file"""
        messagebox.showinfo("Información", "Funcionalidad de exportación en desarrollo")
