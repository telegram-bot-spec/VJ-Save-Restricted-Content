import motor.motor_asyncio
from config import DB_NAME, DB_URI
from datetime import datetime, timedelta

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
            api_id = None,
            api_hash = None,
            is_premium = False,
            premium_expiry = None,
            premium_plan = None,
            daily_downloads = 0,
            last_download_reset = datetime.now(),
            user_channel = None  # NEW: Store user's custom channel
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session')

    async def set_api_id(self, id, api_id):
        await self.col.update_one({'id': int(id)}, {'$set': {'api_id': api_id}})

    async def get_api_id(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('api_id')

    async def set_api_hash(self, id, api_hash):
        await self.col.update_one({'id': int(id)}, {'$set': {'api_hash': api_hash}})

    async def get_api_hash(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('api_hash')

    # ==================== PREMIUM FUNCTIONS ====================
    
    async def add_premium(self, user_id, days, plan_name):
        """Add premium to a user - supports fractional days (hours)"""
        # Convert days to timedelta (supports decimal for hours)
        if days < 1:
            # For hours (e.g., 0.125 days = 3 hours)
            duration = timedelta(hours=days * 24)
        else:
            # For days
            duration = timedelta(days=days)
        
        expiry_date = datetime.now() + duration
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {
                'is_premium': True,
                'premium_expiry': expiry_date,
                'premium_plan': plan_name
            }}
        )
    
    async def remove_premium(self, user_id):
        """Remove premium from a user"""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {
                'is_premium': False,
                'premium_expiry': None,
                'premium_plan': None
            }}
        )
    
    async def check_premium(self, user_id):
        """Check if user is premium and not expired"""
        user = await self.col.find_one({'id': int(user_id)})
        if not user:
            return False
        
        # Check if user has premium
        if not user.get('is_premium', False):
            return False
        
        # Check if premium is expired
        expiry = user.get('premium_expiry')
        if expiry and datetime.now() > expiry:
            # Premium expired, remove it
            await self.remove_premium(user_id)
            return False
        
        return True
    
    async def get_premium_expiry(self, user_id):
        """Get premium expiry date"""
        user = await self.col.find_one({'id': int(user_id)})
        if user:
            return user.get('premium_expiry')
        return None
    
    async def get_premium_plan(self, user_id):
        """Get premium plan name"""
        user = await self.col.find_one({'id': int(user_id)})
        if user:
            return user.get('premium_plan')
        return None
    
    async def get_all_premium_users(self):
        """Get all active premium users"""
        return self.col.find({'is_premium': True})
    
    async def total_premium_users(self):
        """Count total premium users"""
        count = await self.col.count_documents({'is_premium': True})
        return count
    
    # ==================== DAILY DOWNLOAD LIMIT FUNCTIONS ====================
    
    async def check_daily_limit(self, user_id, limit):
        """Check if user has exceeded daily download limit"""
        user = await self.col.find_one({'id': int(user_id)})
        if not user:
            return False
        
        # Reset counter if it's a new day
        last_reset = user.get('last_download_reset', datetime.now())
        if datetime.now().date() > last_reset.date():
            await self.reset_daily_downloads(user_id)
            return True
        
        # Check limit
        downloads = user.get('daily_downloads', 0)
        return downloads < limit
    
    async def increment_daily_downloads(self, user_id):
        """Increment daily download counter"""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$inc': {'daily_downloads': 1}}
        )
    
    async def reset_daily_downloads(self, user_id):
        """Reset daily download counter"""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {
                'daily_downloads': 0,
                'last_download_reset': datetime.now()
            }}
        )
    
    async def get_daily_downloads(self, user_id):
        """Get current daily download count"""
        user = await self.col.find_one({'id': int(user_id)})
        if user:
            # Reset if new day
            last_reset = user.get('last_download_reset', datetime.now())
            if datetime.now().date() > last_reset.date():
                await self.reset_daily_downloads(user_id)
                return 0
            return user.get('daily_downloads', 0)
        return 0
    
    # ==================== USER CHANNEL FUNCTIONS (Premium Feature) ====================
    
    async def set_user_channel(self, user_id, channel_id):
        """Set user's custom channel for downloads"""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {'user_channel': str(channel_id)}}
        )
    
    async def get_user_channel(self, user_id):
        """Get user's custom channel"""
        user = await self.col.find_one({'id': int(user_id)})
        if user:
            return user.get('user_channel')
        return None
    
    async def remove_user_channel(self, user_id):
        """Remove user's custom channel"""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {'user_channel': None}}
        )

db = Database(DB_URI, "TechVJDemoBot")
