import os

class Config:
    # Bot configuration
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    
    # Channel IDs (replace with your actual channel IDs)
    APPROVAL_CHANNEL_ID = int(os.getenv("APPROVAL_CHANNEL_ID", "0"))
    
    # Role IDs (replace with your actual role IDs)
    APPROVAL_ROLE_ID = int(os.getenv("APPROVAL_ROLE_ID", "0")) if os.getenv("APPROVAL_ROLE_ID") else None
    
    # Admin roles (these role names will have admin permissions)
    ADMIN_ROLES = ['admin', 'administrator', 'owner']
    
    # Staff roles (these roles can approve purchases and give points)
    # You can customize these role names to match your Discord server
    STAFF_ROLES = ['admin', 'administrator', 'moderator', 'staff', 'owner', 'manager', 'helper']
    
    # Points system settings
    DEFAULT_BALANCE = 0
    MAX_POINTS_PER_TRANSACTION = 10000
    
    # File paths
    DATA_DIR = "data"
    USERS_FILE = f"{DATA_DIR}/users.json"
    STOCK_FILE = f"{DATA_DIR}/stock.json"
    PENDING_FILE = f"{DATA_DIR}/pending_purchases.json"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("DISCORD_BOT_TOKEN environment variable is required")
        
        if cls.APPROVAL_CHANNEL_ID == 0:
            errors.append("APPROVAL_CHANNEL_ID environment variable should be set to a valid channel ID")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def get_env_template(cls):
        """Return a template for environment variables"""
        return """
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token_here

# Channel Configuration (replace with actual channel IDs)
APPROVAL_CHANNEL_ID=123456789012345678

# Role Configuration (replace with actual role IDs)
APPROVAL_ROLE_ID=123456789012345678
"""
