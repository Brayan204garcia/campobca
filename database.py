import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, data_dir: str = "data"):
        """Initialize JSON database manager"""
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # JSON file paths
        self.farmers_file = os.path.join(self.data_dir, "farmers.json")
        self.products_file = os.path.join(self.data_dir, "products.json")
        self.sales_points_file = os.path.join(self.data_dir, "sales_points.json")
        self.distribution_requests_file = os.path.join(self.data_dir, "distribution_requests.json")
        self.distribution_assignments_file = os.path.join(self.data_dir, "distribution_assignments.json")
        
        # Initialize JSON files
        self.initialize_json_files()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def initialize_json_files(self):
        """Initialize JSON files if they don't exist"""
        files_to_init = [
            (self.farmers_file, []),
            (self.products_file, []),
            (self.sales_points_file, []),
            (self.distribution_requests_file, []),
            (self.distribution_assignments_file, [])
        ]
        
        for file_path, initial_data in files_to_init:
            if not os.path.exists(file_path):
                self.save_json(file_path, initial_data)
    
    def load_json(self, file_path: str) -> List[Dict]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_json(self, file_path: str, data: List[Dict]):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Error guardando archivo JSON: {str(e)}")
    
    def get_next_id(self, data: List[Dict]) -> int:
        """Get next available ID"""
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1
    
    def close(self):
        """Compatibility method - no action needed for JSON files"""
        pass
    
    def initialize_database(self):
        """Compatibility method - JSON files are initialized in constructor"""
        pass
    
    # Farmer operations
    def add_farmer(self, farmer_data: Dict) -> int:
        """Add a new farmer"""
        try:
            farmers = self.load_json(self.farmers_file)
            farmer_id = self.get_next_id(farmers)
            
            new_farmer = {
                'id': farmer_id,
                'name': farmer_data['name'],
                'email': farmer_data.get('email'),
                'phone': farmer_data.get('phone'),
                'address': farmer_data.get('address'),
                'registration_date': datetime.now().isoformat(),
                'active': True
            }
            
            farmers.append(new_farmer)
            self.save_json(self.farmers_file, farmers)
            return farmer_id
            
        except Exception as e:
            raise Exception(f"Error agregando agricultor: {str(e)}")
    
    def get_farmers(self, active_only: bool = True) -> List[Dict]:
        """Get all farmers"""
        try:
            farmers = self.load_json(self.farmers_file)
            
            if active_only:
                farmers = [f for f in farmers if f.get('active', True)]
            
            # Sort by name
            farmers.sort(key=lambda x: x.get('name', ''))
            return farmers
            
        except Exception as e:
            raise Exception(f"Error obteniendo agricultores: {str(e)}")
    
    def update_farmer(self, farmer_id: int, farmer_data: Dict):
        """Update farmer information"""
        try:
            farmers = self.load_json(self.farmers_file)
            
            for farmer in farmers:
                if farmer['id'] == farmer_id:
                    farmer.update({
                        'name': farmer_data['name'],
                        'email': farmer_data.get('email'),
                        'phone': farmer_data.get('phone'),
                        'address': farmer_data.get('address')
                    })
                    break
            
            self.save_json(self.farmers_file, farmers)
            
        except Exception as e:
            raise Exception(f"Error actualizando agricultor: {str(e)}")
    
    # Product operations
    def add_product(self, product_data: Dict) -> int:
        """Add a new product"""
        try:
            products = self.load_json(self.products_file)
            product_id = self.get_next_id(products)
            
            new_product = {
                'id': product_id,
                'farmer_id': product_data['farmer_id'],
                'name': product_data['name'],
                'category': product_data['category'],
                'quantity': product_data['quantity'],
                'unit': product_data['unit'],
                'price_per_unit': product_data['price_per_unit'],
                'harvest_date': product_data.get('harvest_date'),
                'expiry_date': product_data.get('expiry_date'),
                'quality_grade': product_data.get('quality_grade'),
                'description': product_data.get('description'),
                'available': True,
                'created_date': datetime.now().isoformat()
            }
            
            products.append(new_product)
            self.save_json(self.products_file, products)
            return product_id
            
        except Exception as e:
            raise Exception(f"Error agregando producto: {str(e)}")
    
    def get_products(self, available_only: bool = True, farmer_id: Optional[int] = None) -> List[Dict]:
        """Get products with farmer information"""
        try:
            products = self.load_json(self.products_file)
            farmers = self.load_json(self.farmers_file)
            
            # Create farmer lookup dict
            farmer_lookup = {f['id']: f['name'] for f in farmers}
            
            # Filter products
            filtered_products = []
            for product in products:
                if available_only and not product.get('available', True):
                    continue
                if farmer_id and product.get('farmer_id') != farmer_id:
                    continue
                
                # Add farmer name
                product['farmer_name'] = farmer_lookup.get(product.get('farmer_id'), 'Desconocido')
                filtered_products.append(product)
            
            # Sort by expiry date, then by created date
            filtered_products.sort(key=lambda x: (
                x.get('expiry_date') or '9999-12-31',
                x.get('created_date') or ''
            ), reverse=False)
            
            return filtered_products
            
        except Exception as e:
            raise Exception(f"Error obteniendo productos: {str(e)}")
    
    # Sales point operations
    def add_sales_point(self, sales_point_data: Dict) -> int:
        """Add a new sales point"""
        try:
            sales_points = self.load_json(self.sales_points_file)
            sales_point_id = self.get_next_id(sales_points)
            
            new_sales_point = {
                'id': sales_point_id,
                'name': sales_point_data['name'],
                'type': sales_point_data['type'],
                'contact_person': sales_point_data.get('contact_person'),
                'email': sales_point_data.get('email'),
                'phone': sales_point_data.get('phone'),
                'address': sales_point_data['address'],
                'capacity_info': sales_point_data.get('capacity_info'),
                'active': True,
                'registration_date': datetime.now().isoformat()
            }
            
            sales_points.append(new_sales_point)
            self.save_json(self.sales_points_file, sales_points)
            return sales_point_id
            
        except Exception as e:
            raise Exception(f"Error agregando punto de venta: {str(e)}")
    
    def get_sales_points(self, active_only: bool = True) -> List[Dict]:
        """Get all sales points"""
        try:
            sales_points = self.load_json(self.sales_points_file)
            
            if active_only:
                sales_points = [sp for sp in sales_points if sp.get('active', True)]
            
            # Sort by name
            sales_points.sort(key=lambda x: x.get('name', ''))
            return sales_points
            
        except Exception as e:
            raise Exception(f"Error obteniendo puntos de venta: {str(e)}")
    
    # Distribution operations
    def add_distribution_request(self, request_data: Dict) -> int:
        """Add a new distribution request"""
        try:
            requests = self.load_json(self.distribution_requests_file)
            request_id = self.get_next_id(requests)
            
            new_request = {
                'id': request_id,
                'sales_point_id': request_data['sales_point_id'],
                'product_category': request_data['product_category'],
                'quantity_requested': request_data['quantity_requested'],
                'unit': request_data['unit'],
                'max_price': request_data.get('max_price'),
                'required_date': request_data.get('required_date'),
                'priority': request_data.get('priority', 'medium'),
                'status': 'pending',
                'notes': request_data.get('notes'),
                'created_date': datetime.now().isoformat()
            }
            
            requests.append(new_request)
            self.save_json(self.distribution_requests_file, requests)
            return request_id
            
        except Exception as e:
            raise Exception(f"Error agregando solicitud de distribución: {str(e)}")
    
    def get_distribution_requests(self, status: Optional[str] = None) -> List[Dict]:
        """Get distribution requests with sales point information"""
        try:
            requests = self.load_json(self.distribution_requests_file)
            sales_points = self.load_json(self.sales_points_file)
            
            # Create sales point lookup dict
            sp_lookup = {sp['id']: sp['name'] for sp in sales_points}
            
            # Filter requests by status
            filtered_requests = []
            for request in requests:
                if status and request.get('status') != status:
                    continue
                
                # Add sales point name
                request['sales_point_name'] = sp_lookup.get(request.get('sales_point_id'), 'Desconocido')
                filtered_requests.append(request)
            
            return filtered_requests
            
        except Exception as e:
            raise Exception(f"Error obteniendo solicitudes de distribución: {str(e)}")
    
    def get_dashboard_stats(self) -> Dict:
        """Get statistics for dashboard"""
        try:
            farmers = self.load_json(self.farmers_file)
            products = self.load_json(self.products_file)
            sales_points = self.load_json(self.sales_points_file)
            requests = self.load_json(self.distribution_requests_file)
            
            stats = {}
            
            # Total farmers
            stats['total_farmers'] = len([f for f in farmers if f.get('active', True)])
            
            # Total products available
            stats['total_products'] = len([p for p in products if p.get('available', True)])
            
            # Total sales points
            stats['total_sales_points'] = len([sp for sp in sales_points if sp.get('active', True)])
            
            # Pending requests
            stats['pending_requests'] = len([r for r in requests if r.get('status') == 'pending'])
            
            # Products expiring soon (within 7 days)
            from datetime import datetime, timedelta
            future_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            expiring_count = 0
            for product in products:
                if not product.get('available', True):
                    continue
                expiry_date = product.get('expiry_date')
                if expiry_date and expiry_date <= future_date:
                    expiring_count += 1
            
            stats['expiring_soon'] = expiring_count
            
            return stats
            
        except Exception as e:
            raise Exception(f"Error obteniendo estadísticas: {str(e)}")
