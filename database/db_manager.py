import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="supermarket.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """إنشاء اتصال بقاعدة البيانات"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            # تفعيل دعم المفاتيح الخارجية
            self.cursor.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception as e:
            print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            return False
    
    def create_tables(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            # جدول الفئات
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول المنتجات
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    purchase_price_syp REAL DEFAULT 0,
                    purchase_price_usd REAL DEFAULT 0,
                    selling_price_syp REAL DEFAULT 0,
                    selling_price_usd REAL DEFAULT 0,
                    quantity REAL DEFAULT 0,
                    min_quantity REAL DEFAULT 0,
                    unit TEXT DEFAULT 'قطعة',
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            ''')
            
            # جدول الموردين
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    address TEXT,
                    notes TEXT,
                    debt_syp REAL DEFAULT 0,
                    debt_usd REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول المبيعات
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_syp REAL DEFAULT 0,
                    total_usd REAL DEFAULT 0,
                    payment_method TEXT DEFAULT 'نقدي',
                    discount_syp REAL DEFAULT 0,
                    discount_usd REAL DEFAULT 0,
                    notes TEXT,
                    sale_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول عناصر المبيعات
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    product_name TEXT,
                    quantity REAL NOT NULL,
                    unit_price_syp REAL DEFAULT 0,
                    unit_price_usd REAL DEFAULT 0,
                    subtotal_syp REAL DEFAULT 0,
                    subtotal_usd REAL DEFAULT 0,
                    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            
            # جدول المشتريات
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER,
                    total_syp REAL DEFAULT 0,
                    total_usd REAL DEFAULT 0,
                    payment_method TEXT DEFAULT 'نقدي',
                    paid_amount_syp REAL DEFAULT 0,
                    paid_amount_usd REAL DEFAULT 0,
                    notes TEXT,
                    purchase_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                )
            ''')
            
            # جدول عناصر المشتريات
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchase_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    product_name TEXT,
                    quantity REAL NOT NULL,
                    unit_price_syp REAL DEFAULT 0,
                    unit_price_usd REAL DEFAULT 0,
                    subtotal_syp REAL DEFAULT 0,
                    subtotal_usd REAL DEFAULT 0,
                    FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            
            # جدول المصروفات
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount_syp REAL DEFAULT 0,
                    amount_usd REAL DEFAULT 0,
                    expense_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول حركة المخزون
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    movement_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    reason TEXT,
                    movement_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"خطأ في إنشاء الجداول: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """تنفيذ استعلام وإرجاع النتائج"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"خطأ في تنفيذ الاستعلام: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query, params=None):
        """جلب جميع النتائج"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"خطأ في جلب البيانات: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """جلب نتيجة واحدة"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"خطأ في جلب البيانات: {e}")
            return None
    
    def close(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        if self.connection:
            self.connection.close()
