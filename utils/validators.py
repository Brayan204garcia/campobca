import re
from datetime import datetime
from typing import Optional

class Validator:
    """Utility class for input validation"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if email format is valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Validate phone number format
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            bool: True if phone format is valid, False otherwise
        """
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove common separators and spaces
        clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone.strip())
        
        # Check if contains only digits and has reasonable length
        return clean_phone.isdigit() and 7 <= len(clean_phone) <= 15
    
    @staticmethod
    def is_valid_date(date_string: str, date_format: str = '%Y-%m-%d') -> bool:
        """
        Validate date format
        
        Args:
            date_string (str): Date string to validate
            date_format (str): Expected date format (default: '%Y-%m-%d')
            
        Returns:
            bool: True if date format is valid, False otherwise
        """
        if not date_string or not isinstance(date_string, str):
            return False
        
        try:
            datetime.strptime(date_string.strip(), date_format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_positive_number(value: str) -> bool:
        """
        Validate if string represents a positive number
        
        Args:
            value (str): String to validate
            
        Returns:
            bool: True if value is a positive number, False otherwise
        """
        if not value or not isinstance(value, str):
            return False
        
        try:
            num = float(value.strip())
            return num > 0
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_non_negative_number(value: str) -> bool:
        """
        Validate if string represents a non-negative number
        
        Args:
            value (str): String to validate
            
        Returns:
            bool: True if value is a non-negative number, False otherwise
        """
        if not value or not isinstance(value, str):
            return False
        
        try:
            num = float(value.strip())
            return num >= 0
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_integer(value: str) -> bool:
        """
        Validate if string represents a valid integer
        
        Args:
            value (str): String to validate
            
        Returns:
            bool: True if value is a valid integer, False otherwise
        """
        if not value or not isinstance(value, str):
            return False
        
        try:
            int(value.strip())
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_text_length(text: str, min_length: int = 1, max_length: int = 255) -> bool:
        """
        Validate text length
        
        Args:
            text (str): Text to validate
            min_length (int): Minimum allowed length (default: 1)
            max_length (int): Maximum allowed length (default: 255)
            
        Returns:
            bool: True if text length is within bounds, False otherwise
        """
        if not isinstance(text, str):
            return False
        
        text_length = len(text.strip())
        return min_length <= text_length <= max_length
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text input by removing potentially dangerous characters
        
        Args:
            text (str): Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        if not isinstance(text, str):
            return ""
        
        # Remove or escape potentially dangerous characters
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Remove SQL injection attempts (basic protection)
        dangerous_patterns = [
            r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)',
            r'(--|;|\'|\")',
            r'(\bscript\b|\balert\b|\bonload\b)'
        ]
        
        for pattern in dangerous_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        return clean_text.strip()
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, str]:
        """
        Validate that all required fields are present and not empty
        
        Args:
            data (dict): Dictionary containing field data
            required_fields (list): List of required field names
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == "":
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Los siguientes campos son obligatorios: {', '.join(missing_fields)}"
            return False, error_msg
        
        return True, ""
    
    @staticmethod
    def validate_farmer_data(farmer_data: dict) -> tuple[bool, str]:
        """
        Validate farmer data specifically
        
        Args:
            farmer_data (dict): Dictionary containing farmer data
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check required fields
        is_valid, error_msg = Validator.validate_required_fields(farmer_data, ['name'])
        if not is_valid:
            return is_valid, error_msg
        
        # Validate name length
        if not Validator.is_valid_text_length(farmer_data['name'], min_length=2, max_length=100):
            return False, "El nombre debe tener entre 2 y 100 caracteres"
        
        # Validate email if provided
        if farmer_data.get('email') and not Validator.is_valid_email(farmer_data['email']):
            return False, "El formato del email no es válido"
        
        # Validate phone if provided
        if farmer_data.get('phone') and not Validator.is_valid_phone(farmer_data['phone']):
            return False, "El formato del teléfono no es válido"
        
        return True, ""
    
    @staticmethod
    def validate_product_data(product_data: dict) -> tuple[bool, str]:
        """
        Validate product data specifically
        
        Args:
            product_data (dict): Dictionary containing product data
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['farmer_id', 'name', 'category', 'quantity', 'unit', 'price_per_unit']
        is_valid, error_msg = Validator.validate_required_fields(product_data, required_fields)
        if not is_valid:
            return is_valid, error_msg
        
        # Validate product name length
        if not Validator.is_valid_text_length(product_data['name'], min_length=2, max_length=100):
            return False, "El nombre del producto debe tener entre 2 y 100 caracteres"
        
        # Validate farmer_id is integer
        if not Validator.is_valid_integer(str(product_data['farmer_id'])):
            return False, "ID de agricultor inválido"
        
        # Validate quantity is positive number
        if not Validator.is_valid_positive_number(str(product_data['quantity'])):
            return False, "La cantidad debe ser un número positivo"
        
        # Validate price is positive number
        if not Validator.is_valid_positive_number(str(product_data['price_per_unit'])):
            return False, "El precio debe ser un número positivo"
        
        # Validate dates if provided
        if product_data.get('harvest_date') and not Validator.is_valid_date(product_data['harvest_date']):
            return False, "Formato de fecha de cosecha inválido (use YYYY-MM-DD)"
        
        if product_data.get('expiry_date') and not Validator.is_valid_date(product_data['expiry_date']):
            return False, "Formato de fecha de vencimiento inválido (use YYYY-MM-DD)"
        
        # Validate that expiry date is after harvest date if both provided
        if (product_data.get('harvest_date') and product_data.get('expiry_date')):
            try:
                harvest = datetime.strptime(product_data['harvest_date'], '%Y-%m-%d')
                expiry = datetime.strptime(product_data['expiry_date'], '%Y-%m-%d')
                if expiry <= harvest:
                    return False, "La fecha de vencimiento debe ser posterior a la fecha de cosecha"
            except ValueError:
                return False, "Error en el formato de las fechas"
        
        return True, ""
    
    @staticmethod
    def validate_sales_point_data(sales_point_data: dict) -> tuple[bool, str]:
        """
        Validate sales point data specifically
        
        Args:
            sales_point_data (dict): Dictionary containing sales point data
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['name', 'type', 'address']
        is_valid, error_msg = Validator.validate_required_fields(sales_point_data, required_fields)
        if not is_valid:
            return is_valid, error_msg
        
        # Validate name length
        if not Validator.is_valid_text_length(sales_point_data['name'], min_length=2, max_length=100):
            return False, "El nombre debe tener entre 2 y 100 caracteres"
        
        # Validate address length
        if not Validator.is_valid_text_length(sales_point_data['address'], min_length=5, max_length=255):
            return False, "La dirección debe tener entre 5 y 255 caracteres"
        
        # Validate email if provided
        if sales_point_data.get('email') and not Validator.is_valid_email(sales_point_data['email']):
            return False, "El formato del email no es válido"
        
        # Validate phone if provided
        if sales_point_data.get('phone') and not Validator.is_valid_phone(sales_point_data['phone']):
            return False, "El formato del teléfono no es válido"
        
        return True, ""
    
    @staticmethod
    def validate_distribution_request_data(request_data: dict) -> tuple[bool, str]:
        """
        Validate distribution request data specifically
        
        Args:
            request_data (dict): Dictionary containing distribution request data
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['sales_point_id', 'product_category', 'quantity_requested', 'unit']
        is_valid, error_msg = Validator.validate_required_fields(request_data, required_fields)
        if not is_valid:
            return is_valid, error_msg
        
        # Validate sales_point_id is integer
        if not Validator.is_valid_integer(str(request_data['sales_point_id'])):
            return False, "ID de punto de venta inválido"
        
        # Validate quantity is positive number
        if not Validator.is_valid_positive_number(str(request_data['quantity_requested'])):
            return False, "La cantidad solicitada debe ser un número positivo"
        
        # Validate max_price if provided
        if request_data.get('max_price') and not Validator.is_valid_positive_number(str(request_data['max_price'])):
            return False, "El precio máximo debe ser un número positivo"
        
        # Validate required_date if provided
        if request_data.get('required_date') and not Validator.is_valid_date(request_data['required_date']):
            return False, "Formato de fecha requerida inválido (use YYYY-MM-DD)"
        
        # Validate that required date is not in the past
        if request_data.get('required_date'):
            try:
                required_date = datetime.strptime(request_data['required_date'], '%Y-%m-%d')
                if required_date.date() < datetime.now().date():
                    return False, "La fecha requerida no puede ser en el pasado"
            except ValueError:
                return False, "Error en el formato de la fecha requerida"
        
        # Validate priority if provided
        valid_priorities = ['low', 'medium', 'high']
        if request_data.get('priority') and request_data['priority'] not in valid_priorities:
            return False, f"La prioridad debe ser una de: {', '.join(valid_priorities)}"
        
        return True, ""
    
    @staticmethod
    def format_currency(amount: float, currency_symbol: str = "$") -> str:
        """
        Format amount as currency
        
        Args:
            amount (float): Amount to format
            currency_symbol (str): Currency symbol (default: "$")
            
        Returns:
            str: Formatted currency string
        """
        try:
            return f"{currency_symbol}{amount:.2f}"
        except (ValueError, TypeError):
            return f"{currency_symbol}0.00"
    
    @staticmethod
    def format_date(date_string: str, input_format: str = '%Y-%m-%d', 
                   output_format: str = '%d/%m/%Y') -> str:
        """
        Format date string from one format to another
        
        Args:
            date_string (str): Date string to format
            input_format (str): Input date format (default: '%Y-%m-%d')
            output_format (str): Output date format (default: '%d/%m/%Y')
            
        Returns:
            str: Formatted date string or original string if conversion fails
        """
        try:
            date_obj = datetime.strptime(date_string, input_format)
            return date_obj.strftime(output_format)
        except (ValueError, TypeError):
            return date_string
