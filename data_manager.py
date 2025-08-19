import json
import os
from typing import Dict, Any

class DataManager:
    def __init__(self):
        self.users_file = "data/users.json"
        self.stock_file = "data/stock.json"
        self.pending_file = "data/pending_purchases.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize data files with default content if they don't exist"""
        
        # Initialize users.json
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f, indent=2)
        
        # Initialize stock.json with empty stock
        if not os.path.exists(self.stock_file):
            default_stock = {}  # Empty stock - add items using /addstock command
            with open(self.stock_file, 'w') as f:
                json.dump(default_stock, f, indent=2)
        
        # Initialize pending_purchases.json
        if not os.path.exists(self.pending_file):
            with open(self.pending_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, file_path: str, data: Dict[str, Any]):
        """Save JSON data to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_balance(self, user_id: int) -> int:
        """Get user's point balance"""
        users = self._load_json(self.users_file)
        return users.get(str(user_id), {}).get('balance', 0)
    
    def add_points(self, user_id: int, amount: int) -> int:
        """Add points to user's balance and return new balance"""
        users = self._load_json(self.users_file)
        user_str = str(user_id)
        
        if user_str not in users:
            users[user_str] = {'balance': 0}
        
        users[user_str]['balance'] += amount
        self._save_json(self.users_file, users)
        
        return users[user_str]['balance']
    
    def deduct_points(self, user_id: int, amount: int) -> int:
        """Deduct points from user's balance and return new balance"""
        users = self._load_json(self.users_file)
        user_str = str(user_id)
        
        if user_str not in users:
            users[user_str] = {'balance': 0}
        
        users[user_str]['balance'] = max(0, users[user_str]['balance'] - amount)
        self._save_json(self.users_file, users)
        
        return users[user_str]['balance']
    
    def set_balance(self, user_id: int, amount: int) -> int:
        """Set user's balance to a specific amount and return new balance"""
        users = self._load_json(self.users_file)
        user_str = str(user_id)
        
        if user_str not in users:
            users[user_str] = {'balance': 0}
        
        users[user_str]['balance'] = max(0, amount)
        self._save_json(self.users_file, users)
        
        return users[user_str]['balance']
    
    def get_stock(self) -> Dict[str, Any]:
        """Get all stock items"""
        return self._load_json(self.stock_file)
    
    def add_pending_purchase(self, user_id: int, item_name: str, cost: int):
        """Add a pending purchase"""
        pending = self._load_json(self.pending_file)
        user_str = str(user_id)
        
        if user_str not in pending:
            pending[user_str] = []
        
        purchase = {
            'item': item_name,
            'cost': cost,
            'timestamp': str(int(__import__('time').time()))
        }
        
        pending[user_str].append(purchase)
        self._save_json(self.pending_file, pending)
    
    def remove_pending_purchase(self, user_id: int, item_name: str):
        """Remove a pending purchase"""
        pending = self._load_json(self.pending_file)
        user_str = str(user_id)
        
        if user_str in pending:
            # Remove the first matching item
            for i, purchase in enumerate(pending[user_str]):
                if purchase['item'] == item_name:
                    pending[user_str].pop(i)
                    break
            
            # Remove user entry if no pending purchases
            if not pending[user_str]:
                del pending[user_str]
            
            self._save_json(self.pending_file, pending)
    
    def get_pending_purchases(self, user_id: int) -> list:
        """Get all pending purchases for a user"""
        pending = self._load_json(self.pending_file)
        return pending.get(str(user_id), [])
    
    def add_stock_item(self, item_name: str, cost: int, description: str = ""):
        """Add an item to stock"""
        stock = self._load_json(self.stock_file)
        stock[item_name] = {
            'cost': cost,
            'description': description
        }
        self._save_json(self.stock_file, stock)
    
    def remove_stock_item(self, item_name: str):
        """Remove an item from stock"""
        stock = self._load_json(self.stock_file)
        if item_name in stock:
            del stock[item_name]
            self._save_json(self.stock_file, stock)
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        balance = self.get_balance(user_id)
        pending = self.get_pending_purchases(user_id)
        
        return {
            'balance': balance,
            'pending_purchases': len(pending),
            'pending_value': sum(p['cost'] for p in pending)
        }
