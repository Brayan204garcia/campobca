import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "agricultural_coop.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            return self.connection
        except sqlite3.Error as e:
            raise Exception(f"Error conectando a la base de datos: {str(e)}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self):
        """Create all necessary tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Farmers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS farmers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    address TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farmer_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    price_per_unit REAL NOT NULL,
                    harvest_date DATE,
                    expiry_date DATE,
                    quality_grade TEXT,
                    description TEXT,
                    available BOOLEAN DEFAULT 1,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farmer_id) REFERENCES farmers (id)
                )
            ''')
            
            # Sales points table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT NOT NULL,
                    capacity_info TEXT,
                    active BOOLEAN DEFAULT 1,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Distribution requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS distribution_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sales_point_id INTEGER NOT NULL,
                    product_category TEXT NOT NULL,
                    quantity_requested REAL NOT NULL,
                    unit TEXT NOT NULL,
                    max_price REAL,
                    required_date DATE,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sales_point_id) REFERENCES sales_points (id)
                )
            ''')
            
            # Distribution assignments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS distribution_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity_assigned REAL NOT NULL,
                    price_agreed REAL NOT NULL,
                    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_date DATE,
                    status TEXT DEFAULT 'assigned',
                    notes TEXT,
                    FOREIGN KEY (request_id) REFERENCES distribution_requests (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            conn.commit()
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Error inicializando la base de datos: {str(e)}")
        finally:
            conn.close()
    
    # Farmer operations
    def add_farmer(self, farmer_data: Dict) -> int:
        """Add a new farmer"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO farmers (name, email, phone, address)
                VALUES (?, ?, ?, ?)
            ''', (farmer_data['name'], farmer_data['email'], 
                  farmer_data['phone'], farmer_data['address']))
            
            farmer_id = cursor.lastrowid
            conn.commit()
            return farmer_id
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Error agregando agricultor: {str(e)}")
        finally:
            conn.close()
    
    def get_farmers(self, active_only: bool = True) -> List[Dict]:
        """Get all farmers"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM farmers"
            if active_only:
                query += " WHERE active = 1"
            query += " ORDER BY name"
            
            cursor.execute(query)
            farmers = [dict(row) for row in cursor.fetchall()]
            return farmers
            
        except sqlite3.Error as e:
            raise Exception(f"Error obteniendo agricultores: {str(e)}")
        finally:
            conn.close()
    
    def update_farmer(self, farmer_id: int, farmer_data: Dict):
        """Update farmer information"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE farmers 
                SET name = ?, email = ?, phone = ?, address = ?
                WHERE id = ?
            ''', (farmer_data['name'], farmer_data['email'], 
                  farmer_data['phone'], farmer_data['address'], farmer_id))
            
            conn.commit()
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Error actualizando agricultor: {str(e)}")
        finally:
            conn.close()
    
    # Product operations
    def add_product(self, product_data: Dict) -> int:
        """Add a new product"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO products (farmer_id, name, category, quantity, unit, 
                                    price_per_unit, harvest_date, expiry_date, 
                                    quality_grade, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (product_data['farmer_id'], product_data['name'], 
                  product_data['category'], product_data['quantity'],
                  product_data['unit'], product_data['price_per_unit'],
                  product_data['harvest_date'], product_data['expiry_date'],
                  product_data['quality_grade'], product_data['description']))
            
            product_id = cursor.lastrowid
            conn.commit()
            return product_id
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Error agregando producto: {str(e)}")
        finally:
            conn.close()
    
    def get_products(self, available_only: bool = True, farmer_id: Optional[int] = None) -> List[Dict]:
        """Get products with farmer information"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT p.*, f.name as farmer_name
                FROM products p
                JOIN farmers f ON p.farmer_id = f.id
            '''
            params = []
            conditions = []
            
            if available_only:
                conditions.append("p.available = 1")
            
            if farmer_id:
                conditions.append("p.farmer_id = ?")
                params.append(farmer_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.expiry_date ASC, p.created_date DESC"
            
            cursor.execute(query, params)
            products = [dict(row) for row in cursor.fetchall()]
            return products
            
        except sqlite3.Error as e:
            raise Exception(f"Error obteniendo productos: {str(e)}")
        finally:
            conn.close()
    
    # Sales point operations
    def add_sales_point(self, sales_point_data: Dict) -> int:
        """Add a new sales point"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sales_points (name, type, contact_person, email, 
                                        phone, address, capacity_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sales_point_data['name'], sales_point_data['type'],
                  sales_point_data['contact_person'], sales_point_data['email'],
                  sales_point_data['phone'], sales_point_data['address'],
                  sales_point_data['capacity_info']))
            
            sales_point_id = cursor.lastrowid
            conn.commit()
            return sales_point_id
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Error agregando punto de venta: {str(e)}")
        finally:
            conn.close()
    
    def get_sales_points(self, active_only: bool = True) -> List[Dict]:
        """Get all sales points"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM sales_points"
            if active_only:
                query += " WHERE active = 1"
            query += " ORDER BY name"
            
            cursor.execute(query)
            sales_points = [dict(row) for row in cursor.fetchall()]
            return sales_points
            
        except sqlite3.Error as e:
            raise Exception(f"Error obteniendo puntos de venta: {str(e)}")
        finally:
            conn.close()
    
    # Distribution operations
    def add_distribution_request(self, request_data: Dict) -> int:
        """Add a new distribution request"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO distribution_requests (sales_point_id, product_category,
                                                 quantity_requested, unit, max_price,
                                                 required_date, priority, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (request_data['sales_point_id'], request_data['product_category'],
                  request_data['quantity_requested'], request_data['unit'],
                  request_data['max_price'], request_data['required_date'],
                  request_data['priority'], request_data['notes']))
            
            request_id = cursor.lastrowid
            conn.commit()
            return request_id
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Error agregando solicitud de distribución: {str(e)}")
        finally:
            conn.close()
    
    def get_distribution_requests(self, status: Optional[str] = None) -> List[Dict]:
        """Get distribution requests with sales point information"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT dr.*, sp.name as sales_point_name
                FROM distribution_requests dr
                JOIN sales_points sp ON dr.sales_point_id = sp.id
            '''
            
            if status:
                query += " WHERE dr.status = ?"
                cursor.execute(query, (status,))
            else:
                cursor.execute(query)
            
            requests = [dict(row) for row in cursor.fetchall()]
            return requests
            
        except sqlite3.Error as e:
            raise Exception(f"Error obteniendo solicitudes de distribución: {str(e)}")
        finally:
            conn.close()
    
    def get_dashboard_stats(self) -> Dict:
        """Get statistics for dashboard"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total farmers
            cursor.execute("SELECT COUNT(*) as count FROM farmers WHERE active = 1")
            stats['total_farmers'] = cursor.fetchone()['count']
            
            # Total products available
            cursor.execute("SELECT COUNT(*) as count FROM products WHERE available = 1")
            stats['total_products'] = cursor.fetchone()['count']
            
            # Total sales points
            cursor.execute("SELECT COUNT(*) as count FROM sales_points WHERE active = 1")
            stats['total_sales_points'] = cursor.fetchone()['count']
            
            # Pending requests
            cursor.execute("SELECT COUNT(*) as count FROM distribution_requests WHERE status = 'pending'")
            stats['pending_requests'] = cursor.fetchone()['count']
            
            # Products expiring soon (within 7 days)
            cursor.execute('''
                SELECT COUNT(*) as count FROM products 
                WHERE available = 1 AND expiry_date <= date('now', '+7 days')
            ''')
            stats['expiring_soon'] = cursor.fetchone()['count']
            
            return stats
            
        except sqlite3.Error as e:
            raise Exception(f"Error obteniendo estadísticas: {str(e)}")
        finally:
            conn.close()
