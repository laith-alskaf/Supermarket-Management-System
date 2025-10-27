import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from database.db_manager import DatabaseManager
from ui.dashboard_ui import DashboardUI
from ui.categories_ui import CategoriesUI
from ui.products_ui import ProductsUI
from ui.suppliers_ui import SuppliersUI
from ui.sales_ui import SalesUI
from ui.purchases_ui import PurchasesUI
from ui.expenses_ui import ExpensesUI
from ui.inventory_ui import InventoryUI
from ui.reports_ui import ReportsUI

class SupermarketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة السوبر ماركت")
        self.root.geometry("1400x800")
        self.root.state('zoomed')  # تكبير النافذة
        
        # إنشاء قاعدة البيانات
        self.db = DatabaseManager()
        
        # إعداد الواجهة
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد الواجهة الرئيسية"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # القائمة الجانبية
        sidebar = ttk.Frame(main_frame, width=200, style='primary.TFrame')
        sidebar.pack(side='right', fill='y', padx=2, pady=2)
        sidebar.pack_propagate(False)
        
        # العنوان
        title_label = ttk.Label(
            sidebar, 
            text="نظام السوبر ماركت",
            font=('Arial', 16, 'bold'),
            style='primary.TLabel'
        )
        title_label.pack(pady=20, padx=10)
        
        # الأزرار
        buttons = [
            ("🏠 لوحة التحكم", self.show_dashboard),
            ("📊 الفئات", self.show_categories),
            ("📦 المنتجات", self.show_products),
            ("🏪 الموردين", self.show_suppliers),
            ("💰 نقطة البيع", self.show_sales),
            ("📥 المشتريات", self.show_purchases),
            ("💸 المصروفات", self.show_expenses),
            ("📦 المخزون", self.show_inventory),
            ("📈 التقارير", self.show_reports),
        ]
        
        for text, command in buttons:
            btn = ttk.Button(
                sidebar,
                text=text,
                command=command,
                style='primary.TButton',
                width=25
            )
            btn.pack(pady=5, padx=10, fill='x')
        
        # منطقة المحتوى
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # عرض لوحة التحكم افتراضياً
        self.show_dashboard()
    
    def clear_content(self):
        """مسح المحتوى الحالي"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """عرض لوحة التحكم"""
        self.clear_content()
        DashboardUI(self.content_frame, self.db)
    
    def show_categories(self):
        """عرض إدارة الفئات"""
        self.clear_content()
        CategoriesUI(self.content_frame, self.db)
    
    def show_products(self):
        """عرض إدارة المنتجات"""
        self.clear_content()
        ProductsUI(self.content_frame, self.db)
    
    def show_suppliers(self):
        """عرض إدارة الموردين"""
        self.clear_content()
        SuppliersUI(self.content_frame, self.db)
    
    def show_sales(self):
        """عرض نقطة البيع"""
        self.clear_content()
        SalesUI(self.content_frame, self.db)
    
    def show_purchases(self):
        """عرض إدارة المشتريات"""
        self.clear_content()
        PurchasesUI(self.content_frame, self.db)
    
    def show_expenses(self):
        """عرض إدارة المصروفات"""
        self.clear_content()
        ExpensesUI(self.content_frame, self.db)
    
    def show_inventory(self):
        """عرض المخزون"""
        self.clear_content()
        InventoryUI(self.content_frame, self.db)
    
    def show_reports(self):
        """عرض التقارير"""
        self.clear_content()
        ReportsUI(self.content_frame, self.db)
    
    def run(self):
        """تشغيل التطبيق"""
        self.root.mainloop()

if __name__ == "__main__":
    root = ttkb.Window(themename="cosmo")
    app = SupermarketApp(root)
    app.run()
