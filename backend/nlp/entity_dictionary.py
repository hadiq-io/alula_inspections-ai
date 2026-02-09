"""
Entity Dictionary - Bilingual entity cache for NL parsing
==========================================================
Auto-populates from database and provides bilingual lookup
for neighborhoods, activities, inspectors, statuses, etc.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import threading


class EntityDictionary:
    """
    Bilingual entity cache with auto-population from database.
    Designed with Redis-ready interface for Phase 3 cloud migration.
    """
    
    def __init__(self, db=None):
        self.db = db
        self._cache: Dict[str, Dict] = {}
        self._last_refresh: Optional[datetime] = None
        self._lock = threading.Lock()
        
        # Initialize with static data, then populate from DB if available
        self._init_static_data()
        
        if db:
            self.refresh()
    
    def _init_static_data(self):
        """Initialize with known static entities"""
        
        # Neighborhoods (will be enriched from DB)
        self._cache['neighborhoods'] = {
            'العزيزية': {'en': 'Al-Aziziyah', 'id': None},
            'الأندلس': {'en': 'Al-Andalus', 'id': None},
            'الروضة': {'en': 'Al-Rawdah', 'id': None},
            'الشفا': {'en': 'Al-Shafa', 'id': None},
            'النسيم': {'en': 'Al-Naseem', 'id': None},
            'الورود': {'en': 'Al-Wurud', 'id': None},
            'الملك فهد': {'en': 'King Fahd', 'id': None},
            'السليمانية': {'en': 'Al-Sulaimaniyah', 'id': None},
            'العليا': {'en': 'Al-Olaya', 'id': None},
            'المروج': {'en': 'Al-Muruj', 'id': None},
        }
        
        # Activity types
        self._cache['activities'] = {
            'المطاعم': {'en': 'Restaurants', 'code': 'REST', 'id': None},
            'الحلاقة': {'en': 'Barbershops', 'code': 'BARB', 'id': None},
            'المخابز': {'en': 'Bakeries', 'code': 'BAKE', 'id': None},
            'البقالات': {'en': 'Grocery Stores', 'code': 'GROC', 'id': None},
            'الصيدليات': {'en': 'Pharmacies', 'code': 'PHAR', 'id': None},
            'المقاهي': {'en': 'Cafes', 'code': 'CAFE', 'id': None},
            'الفنادق': {'en': 'Hotels', 'code': 'HOTL', 'id': None},
            'المحلات التجارية': {'en': 'Retail Stores', 'code': 'RETL', 'id': None},
            'محلات اللحوم': {'en': 'Butcher Shops', 'code': 'MEAT', 'id': None},
            'محلات الخضار': {'en': 'Vegetable Shops', 'code': 'VEGE', 'id': None},
        }
        
        # Event types (from EventType table)
        self._cache['event_types'] = {
            'تفتيش مجدول': {'en': 'Scheduled Inspection', 'id': 5},
            'تفتيش طارئ': {'en': 'Emergency Inspection', 'id': 1},
            'متابعة': {'en': 'Follow-up', 'id': 2},
            'شكوى': {'en': 'Complaint', 'id': 3},
            'بلاغ': {'en': 'Report', 'id': 4},
        }
        
        # Status values (from EventStatus table)
        self._cache['statuses'] = {
            'مفتوح': {'en': 'Open', 'code': 'open', 'id': 0},
            'مغلق': {'en': 'Closed', 'code': 'closed', 'id': 1},
            'معلق': {'en': 'Pending', 'code': 'pending', 'id': 2},
            'ملغى': {'en': 'Cancelled', 'code': 'cancelled', 'id': 3},
            'مكتمل': {'en': 'Completed', 'code': 'completed', 'id': 1},
        }
        
        # Severity levels
        self._cache['severity'] = {
            'بسيط': {'en': 'Minor', 'level': 1},
            'متوسط': {'en': 'Moderate', 'level': 2},
            'خطير': {'en': 'Serious', 'level': 3},
            'حرج': {'en': 'Critical', 'level': 4},
            'شديد': {'en': 'Severe', 'level': 5},
        }
        
        # Time period mappings
        self._cache['months'] = {
            'يناير': {'en': 'January', 'num': 1},
            'فبراير': {'en': 'February', 'num': 2},
            'مارس': {'en': 'March', 'num': 3},
            'أبريل': {'en': 'April', 'num': 4},
            'مايو': {'en': 'May', 'num': 5},
            'يونيو': {'en': 'June', 'num': 6},
            'يوليو': {'en': 'July', 'num': 7},
            'أغسطس': {'en': 'August', 'num': 8},
            'سبتمبر': {'en': 'September', 'num': 9},
            'أكتوبر': {'en': 'October', 'num': 10},
            'نوفمبر': {'en': 'November', 'num': 11},
            'ديسمبر': {'en': 'December', 'num': 12},
        }
        
        # Metrics vocabulary
        self._cache['metrics'] = {
            'المخالفات': {'en': 'violations', 'table': 'EventViolation'},
            'الامتثال': {'en': 'compliance', 'field': 'Score'},
            'التفتيش': {'en': 'inspections', 'table': 'Event'},
            'الفحوصات': {'en': 'inspections', 'table': 'Event'},
            'البلاغات': {'en': 'reports', 'table': 'Event'},
            'الأداء': {'en': 'performance', 'table': 'ML_Inspector_Performance'},
            'المخاطر': {'en': 'risk', 'table': 'ML_Location_Risk'},
        }
        
        # Inspectors (will be populated from DB)
        self._cache['inspectors'] = {}
        
    def refresh(self) -> bool:
        """
        Refresh entity cache from database.
        Returns True if successful.
        """
        if not self.db:
            print("⚠️ No database connection for entity refresh")
            return False
            
        with self._lock:
            try:
                # Populate neighborhoods from Locations table
                self._populate_neighborhoods()
                
                # Populate activity types from LocationType table
                self._populate_activities()
                
                # Populate inspectors from Event.ReporterID
                self._populate_inspectors()
                
                # Populate event types
                self._populate_event_types()
                
                self._last_refresh = datetime.now()
                print(f"✅ Entity cache refreshed at {self._last_refresh}")
                return True
                
            except Exception as e:
                print(f"❌ Entity refresh error: {e}")
                return False
    
    def _populate_neighborhoods(self):
        """Load locations from Locations table (using Name instead of NeighborhoodName)"""
        query = """
            SELECT DISTINCT TOP 100
                l.Id as id,
                COALESCE(l.NameAr, l.Name) as name_ar,
                l.Name as name_en
            FROM Locations l
            WHERE l.Isdeleted = 0 AND l.Name IS NOT NULL
        """
        try:
            df = self.db.execute_query(query)
            if not df.empty:
                for _, row in df.iterrows():
                    name_ar = row.get('name_ar', '')
                    if name_ar:
                        self._cache['neighborhoods'][name_ar] = {
                            'en': row.get('name_en', name_ar),
                            'id': row.get('id')
                        }
                print(f"  📍 Loaded {len(df)} neighborhoods")
        except Exception as e:
            print(f"  ⚠️ Could not load neighborhoods: {e}")
    
    def _populate_activities(self):
        """Load activity types from LocationType table"""
        query = """
            SELECT 
                Id as id,
                Name as name_en,
                NameAr as name_ar
            FROM LocationType
            WHERE IsDeleted = 0
        """
        try:
            df = self.db.execute_query(query)
            if not df.empty:
                for _, row in df.iterrows():
                    name_ar = row.get('name_ar', '')
                    if name_ar:
                        self._cache['activities'][name_ar] = {
                            'en': row.get('name_en', name_ar),
                            'id': row.get('id')
                        }
                print(f"  🏪 Loaded {len(df)} activity types")
        except Exception as e:
            print(f"  ⚠️ Could not load activities: {e}")
    
    def _populate_inspectors(self):
        """Load inspectors from Event table (using ReporterID only)"""
        query = """
            SELECT DISTINCT TOP 50
                e.ReporterID as id,
                CAST(e.ReporterID AS VARCHAR(20)) as name_en,
                CAST(e.ReporterID AS VARCHAR(20)) as name_ar
            FROM Event e
            WHERE e.ReporterID IS NOT NULL
            AND e.IsDeleted = 0
        """
        try:
            df = self.db.execute_query(query)
            if not df.empty:
                for _, row in df.iterrows():
                    name_ar = row.get('name_ar') or row.get('name_en', '')
                    name_en = row.get('name_en') or name_ar
                    if name_ar:
                        self._cache['inspectors'][name_ar] = {
                            'en': name_en,
                            'id': row.get('id')
                        }
                    if name_en and name_en != name_ar:
                        self._cache['inspectors'][name_en] = {
                            'ar': name_ar,
                            'id': row.get('id')
                        }
                print(f"  👤 Loaded {len(df)} inspectors")
        except Exception as e:
            print(f"  ⚠️ Could not load inspectors: {e}")
    
    def _populate_event_types(self):
        """Load event types from EventType table"""
        query = """
            SELECT 
                Id as id,
                NameEn as name_en,
                NameAr as name_ar
            FROM EventType
            WHERE IsDeleted = 0
        """
        try:
            df = self.db.execute_query(query)
            if not df.empty:
                for _, row in df.iterrows():
                    name_ar = row.get('name_ar', '')
                    if name_ar:
                        self._cache['event_types'][name_ar] = {
                            'en': row.get('name_en', name_ar),
                            'id': row.get('id')
                        }
                print(f"  📋 Loaded {len(df)} event types")
        except Exception as e:
            print(f"  ⚠️ Could not load event types: {e}")
    
    def get(self, category: str, key: str) -> Optional[Dict]:
        """
        Look up an entity by category and key.
        Supports both Arabic and English lookups.
        """
        if category not in self._cache:
            return None
        
        # Direct lookup
        if key in self._cache[category]:
            return self._cache[category][key]
        
        # Reverse lookup (search by English name)
        for ar_key, value in self._cache[category].items():
            if value.get('en', '').lower() == key.lower():
                return {'ar': ar_key, **value}
        
        return None
    
    def get_id(self, category: str, key: str) -> Optional[int]:
        """Get the database ID for an entity"""
        entity = self.get(category, key)
        return entity.get('id') if entity else None
    
    def translate(self, category: str, key: str, to_lang: str = 'en') -> str:
        """Translate an entity name between Arabic and English"""
        entity = self.get(category, key)
        if not entity:
            return key
        
        if to_lang == 'en':
            return entity.get('en', key)
        else:
            return entity.get('ar', key)
    
    def search(self, category: str, query: str) -> List[Dict]:
        """
        Fuzzy search for entities matching a query.
        Returns list of matching entities.
        """
        if category not in self._cache:
            return []
        
        query_lower = query.lower()
        results = []
        
        for key, value in self._cache[category].items():
            if query_lower in key.lower() or query_lower in value.get('en', '').lower():
                results.append({
                    'key': key,
                    'en': value.get('en'),
                    'id': value.get('id')
                })
        
        return results
    
    def get_all(self, category: str) -> Dict:
        """Get all entities in a category"""
        return self._cache.get(category, {})
    
    def add_entity(self, category: str, key_ar: str, key_en: str, entity_id: int = None) -> None:
        """Add an entity to the cache."""
        if category not in self._cache:
            self._cache[category] = {}
        self._cache[category][key_ar] = {
            'en': key_en,
            'id': entity_id
        }
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            category: len(items) 
            for category, items in self._cache.items()
        }
