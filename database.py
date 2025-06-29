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
        self.drivers_file = os.path.join(self.data_dir, "drivers.json")
        self.deliveries_file = os.path.join(self.data_dir, "deliveries.json")
        
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
            (self.drivers_file, []),
            (self.deliveries_file, [])
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
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
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
                'contact_person': farmer_data.get('contact_person'),
                'email': farmer_data.get('email'),
                'phone': farmer_data.get('phone'),
                'address': farmer_data.get('address'),
                'farm_size': farmer_data.get('farm_size'),
                'specialization': farmer_data.get('specialization'),
                'certification': farmer_data.get('certification'),
                'active': True,
                'registration_date': datetime.now().isoformat()
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
                    farmer.update(farmer_data)
                    farmer['updated_date'] = datetime.now().isoformat()
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
                'name': product_data['name'],
                'category': product_data['category'],
                'farmer_id': product_data['farmer_id'],
                'quantity': product_data['quantity'],
                'unit': product_data['unit'],
                'price_per_unit': product_data['price_per_unit'],
                'quality_grade': product_data.get('quality_grade'),
                'harvest_date': product_data.get('harvest_date'),
                'expiry_date': product_data.get('expiry_date'),
                'storage_conditions': product_data.get('storage_conditions'),
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
    
    def update_sales_point(self, sales_point_id: int, sales_point_data: Dict):
        """Update sales point information"""
        try:
            sales_points = self.load_json(self.sales_points_file)
            
            for sales_point in sales_points:
                if sales_point['id'] == sales_point_id:
                    sales_point.update(sales_point_data)
                    sales_point['updated_date'] = datetime.now().isoformat()
                    break
            
            self.save_json(self.sales_points_file, sales_points)
            
        except Exception as e:
            raise Exception(f"Error actualizando punto de venta: {str(e)}")
    
    # Driver operations
    def add_driver(self, driver_data: Dict) -> int:
        """Add a new driver"""
        try:
            drivers = self.load_json(self.drivers_file)
            driver_id = self.get_next_id(drivers)
            
            new_driver = {
                'id': driver_id,
                'name': driver_data['name'],
                'phone': driver_data['phone'],
                'email': driver_data.get('email'),
                'license_number': driver_data['license_number'],
                'vehicle_type': driver_data['vehicle_type'],
                'vehicle_plate': driver_data['vehicle_plate'],
                'vehicle_capacity': driver_data.get('vehicle_capacity'),
                'active': True,
                'registration_date': datetime.now().isoformat()
            }
            
            drivers.append(new_driver)
            self.save_json(self.drivers_file, drivers)
            return driver_id
            
        except Exception as e:
            raise Exception(f"Error agregando conductor: {str(e)}")
    
    def get_drivers(self, active_only: bool = True) -> List[Dict]:
        """Get all drivers"""
        try:
            drivers = self.load_json(self.drivers_file)
            
            if active_only:
                drivers = [d for d in drivers if d.get('active', True)]
            
            # Sort by name
            drivers.sort(key=lambda x: x.get('name', ''))
            return drivers
            
        except Exception as e:
            raise Exception(f"Error obteniendo conductores: {str(e)}")
    
    def update_driver(self, driver_id: int, driver_data: Dict):
        """Update driver information"""
        try:
            drivers = self.load_json(self.drivers_file)
            
            for driver in drivers:
                if driver['id'] == driver_id:
                    driver.update(driver_data)
                    driver['updated_date'] = datetime.now().isoformat()
                    break
            
            self.save_json(self.drivers_file, drivers)
            
        except Exception as e:
            raise Exception(f"Error actualizando conductor: {str(e)}")
    
    # Distribution request operations
    def add_distribution_request(self, request_data: Dict) -> int:
        """Add a new distribution request"""
        try:
            requests = self.load_json(self.distribution_requests_file)
            request_id = self.get_next_id(requests)
            
            new_request = {
                'id': request_id,
                'sales_point_id': request_data['sales_point_id'],
                'product_ids': request_data['product_ids'],
                'quantities': request_data['quantities'],
                'requested_date': request_data['requested_date'],
                'priority': request_data.get('priority', 'normal'),
                'special_instructions': request_data.get('special_instructions'),
                'status': 'pendiente',
                'total_amount': request_data.get('total_amount', 0),
                'created_date': datetime.now().isoformat()
            }
            
            requests.append(new_request)
            self.save_json(self.distribution_requests_file, requests)
            return request_id
            
        except Exception as e:
            raise Exception(f"Error agregando solicitud de distribución: {str(e)}")
    
    def add_distribution_request_with_auto_assignment(self, request_data: Dict) -> int:
        """Add a new distribution request and update inventory"""
        try:
            # Create the distribution request
            request_id = self.add_distribution_request(request_data)
            
            # Get product information
            products = self.load_json(self.products_file)
            
            # Update inventory automatically
            for i, product_id in enumerate(request_data['product_ids']):
                quantity_requested = request_data['quantities'][i]
                
                # Find the product
                product = next((p for p in products if p['id'] == product_id), None)
                if not product:
                    continue
                
                # Check if enough quantity is available
                if product['quantity'] < quantity_requested:
                    raise Exception(f"Cantidad insuficiente para {product['name']}. Disponible: {product['quantity']}, Solicitado: {quantity_requested}")
                
                # Update product inventory
                product['quantity'] -= quantity_requested
                if product['quantity'] == 0:
                    product['available'] = False
            
            # Update request status to confirmed
            requests = self.load_json(self.distribution_requests_file)
            for request in requests:
                if request['id'] == request_id:
                    request['status'] = 'confirmado'
                    break
            
            # Save all changes
            self.save_json(self.products_file, products)
            self.save_json(self.distribution_requests_file, requests)
            
            return request_id
            
        except Exception as e:
            raise Exception(f"Error creando solicitud con asignación automática: {str(e)}")
    
    def cancel_distribution_request(self, request_id: int):
        """Cancel a distribution request and restore inventory"""
        try:
            # Get request details
            requests = self.load_json(self.distribution_requests_file)
            request = next((r for r in requests if r['id'] == request_id), None)
            if not request:
                raise Exception("Solicitud no encontrada")
            
            if request['status'] == 'cancelado':
                raise Exception("La solicitud ya está cancelada")
            
            if request['status'] in ['entregado', 'en_transito']:
                raise Exception("No se puede cancelar una solicitud entregada o en tránsito")
            
            # Restore inventory if it was already confirmed
            if request['status'] == 'confirmado':
                products = self.load_json(self.products_file)
                
                for i, product_id in enumerate(request['product_ids']):
                    quantity_to_restore = request['quantities'][i]
                    
                    # Find the product and restore quantity
                    product = next((p for p in products if p['id'] == product_id), None)
                    if product:
                        product['quantity'] += quantity_to_restore
                        product['available'] = True
                
                self.save_json(self.products_file, products)
            
            # Update request status
            request['status'] = 'cancelado'
            request['cancelled_date'] = datetime.now().isoformat()
            
            self.save_json(self.distribution_requests_file, requests)
            
        except Exception as e:
            raise Exception(f"Error cancelando solicitud: {str(e)}")
    
    def update_distribution_request(self, request_id: int, request_data: Dict):
        """Update a distribution request"""
        try:
            requests = self.load_json(self.distribution_requests_file)
            
            for request in requests:
                if request['id'] == request_id:
                    request.update(request_data)
                    request['updated_date'] = datetime.now().isoformat()
                    break
            
            self.save_json(self.distribution_requests_file, requests)
            
        except Exception as e:
            raise Exception(f"Error actualizando solicitud: {str(e)}")
    
    def get_distribution_requests(self, status: Optional[str] = None) -> List[Dict]:
        """Get distribution requests with sales point and product information"""
        try:
            requests = self.load_json(self.distribution_requests_file)
            sales_points = self.load_json(self.sales_points_file)
            products = self.load_json(self.products_file)
            
            # Create lookup dictionaries
            sales_point_lookup = {sp['id']: sp for sp in sales_points}
            product_lookup = {p['id']: p for p in products}
            
            # Filter and enrich requests
            filtered_requests = []
            for request in requests:
                if status and request.get('status') != status:
                    continue
                
                # Add sales point information
                sales_point = sales_point_lookup.get(request.get('sales_point_id'))
                if sales_point:
                    request['sales_point_name'] = sales_point['name']
                    request['sales_point_address'] = sales_point.get('address', '')
                
                # Add product information
                product_details = []
                total_amount = 0
                for i, product_id in enumerate(request.get('product_ids', [])):
                    product = product_lookup.get(product_id)
                    if product:
                        quantity = request['quantities'][i] if i < len(request.get('quantities', [])) else 0
                        line_total = product['price_per_unit'] * quantity
                        total_amount += line_total
                        
                        product_details.append({
                            'product_name': product['name'],
                            'quantity': quantity,
                            'unit': product['unit'],
                            'price_per_unit': product['price_per_unit'],
                            'line_total': line_total
                        })
                
                request['product_details'] = product_details
                request['total_amount'] = total_amount
                
                filtered_requests.append(request)
            
            # Sort by created date (newest first)
            filtered_requests.sort(key=lambda x: x.get('created_date', ''), reverse=True)
            
            return filtered_requests
            
        except Exception as e:
            raise Exception(f"Error obteniendo solicitudes de distribución: {str(e)}")
    
    def update_request_status(self, request_id: int, new_status: str):
        """Update distribution request status"""
        try:
            requests = self.load_json(self.distribution_requests_file)
            
            for request in requests:
                if request['id'] == request_id:
                    request['status'] = new_status
                    request['status_updated_date'] = datetime.now().isoformat()
                    break
            
            self.save_json(self.distribution_requests_file, requests)
            
        except Exception as e:
            raise Exception(f"Error actualizando estado de solicitud: {str(e)}")
    
    # Delivery operations
    def add_delivery(self, delivery_data: Dict) -> int:
        """Add a new delivery"""
        try:
            deliveries = self.load_json(self.deliveries_file)
            delivery_id = self.get_next_id(deliveries)
            
            new_delivery = {
                'id': delivery_id,
                'request_id': delivery_data['request_id'],
                'driver_id': delivery_data['driver_id'],
                'scheduled_date': delivery_data['scheduled_date'],
                'delivery_address': delivery_data['delivery_address'],
                'estimated_time': delivery_data.get('estimated_time'),
                'special_instructions': delivery_data.get('special_instructions'),
                'status': 'programado',
                'created_date': datetime.now().isoformat()
            }
            
            deliveries.append(new_delivery)
            self.save_json(self.deliveries_file, deliveries)
            
            # Update request status to en_transito
            self.update_request_status(delivery_data['request_id'], 'en_transito')
            
            return delivery_id
            
        except Exception as e:
            raise Exception(f"Error agregando entrega: {str(e)}")
    
    def get_deliveries(self, status: Optional[str] = None) -> List[Dict]:
        """Get deliveries with detailed information"""
        try:
            deliveries = self.load_json(self.deliveries_file)
            requests = self.load_json(self.distribution_requests_file)
            drivers = self.load_json(self.drivers_file)
            sales_points = self.load_json(self.sales_points_file)
            
            # Create lookup dictionaries
            request_lookup = {r['id']: r for r in requests}
            driver_lookup = {d['id']: d for d in drivers}
            sales_point_lookup = {sp['id']: sp for sp in sales_points}
            
            # Filter and enrich deliveries
            filtered_deliveries = []
            for delivery in deliveries:
                if status and delivery.get('status') != status:
                    continue
                
                # Add request information
                request = request_lookup.get(delivery.get('request_id'))
                if request:
                    sales_point = sales_point_lookup.get(request.get('sales_point_id'))
                    if sales_point:
                        delivery['sales_point_name'] = sales_point['name']
                    delivery['total_amount'] = request.get('total_amount', 0)
                
                # Add driver information
                driver = driver_lookup.get(delivery.get('driver_id'))
                if driver:
                    delivery['driver_name'] = driver['name']
                    delivery['driver_phone'] = driver['phone']
                    delivery['vehicle_info'] = f"{driver['vehicle_type']} - {driver['vehicle_plate']}"
                
                filtered_deliveries.append(delivery)
            
            # Sort by scheduled date
            filtered_deliveries.sort(key=lambda x: x.get('scheduled_date', ''))
            
            return filtered_deliveries
            
        except Exception as e:
            raise Exception(f"Error obteniendo entregas: {str(e)}")
    
    def update_delivery_status(self, delivery_id: int, new_status: str, notes: Optional[str] = None):
        """Update delivery status and sync with request status"""
        try:
            deliveries = self.load_json(self.deliveries_file)
            
            delivery = None
            for d in deliveries:
                if d['id'] == delivery_id:
                    delivery = d
                    break
            
            if not delivery:
                raise Exception("Entrega no encontrada")
            
            # Update delivery status
            delivery['status'] = new_status
            delivery['status_updated_date'] = datetime.now().isoformat()
            
            if notes:
                delivery['notes'] = notes
            
            # Update delivery completion date if delivered
            if new_status == 'entregado':
                delivery['delivered_date'] = datetime.now().isoformat()
                # Update request status to delivered
                self.update_request_status(delivery['request_id'], 'entregado')
            elif new_status == 'cancelado':
                delivery['cancelled_date'] = datetime.now().isoformat()
                # Update request status to cancelled
                self.update_request_status(delivery['request_id'], 'cancelado')
            
            self.save_json(self.deliveries_file, deliveries)
            
        except Exception as e:
            raise Exception(f"Error actualizando estado de entrega: {str(e)}")
    
    def get_dashboard_stats(self) -> Dict:
        """Get statistics for dashboard"""
        try:
            farmers = self.load_json(self.farmers_file)
            products = self.load_json(self.products_file)
            sales_points = self.load_json(self.sales_points_file)
            requests = self.load_json(self.distribution_requests_file)
            deliveries = self.load_json(self.deliveries_file)
            
            # Calculate statistics
            stats = {
                'total_farmers': len([f for f in farmers if f.get('active', True)]),
                'total_products': len([p for p in products if p.get('available', True)]),
                'total_sales_points': len([sp for sp in sales_points if sp.get('active', True)]),
                'pending_requests': len([r for r in requests if r.get('status') == 'pendiente']),
                'confirmed_requests': len([r for r in requests if r.get('status') == 'confirmado']),
                'in_transit_requests': len([r for r in requests if r.get('status') == 'en_transito']),
                'delivered_requests': len([r for r in requests if r.get('status') == 'entregado']),
                'pending_deliveries': len([d for d in deliveries if d.get('status') in ['programado', 'en_camino']]),
                'completed_deliveries': len([d for d in deliveries if d.get('status') == 'entregado'])
            }
            
            return stats
            
        except Exception as e:
            raise Exception(f"Error obteniendo estadísticas: {str(e)}")