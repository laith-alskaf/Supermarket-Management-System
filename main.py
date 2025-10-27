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
from ui.about_ui import AboutUI

class SupermarketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة السوبر ماركت")
        self.root.geometry("1400x800")
        self.root.state('zoomed')  # تكبير النافذة
        
        # إنشاء قاعدة البيانات
        self.db = DatabaseManager()
        
        # متغيرات التحكم
        self.sidebar_expanded = True
        self.current_theme = "cosmo"
        
        # إعداد الواجهة
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد الواجهة الرئيسية"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # شريط الأدوات العلوي
        self.setup_top_bar(main_frame)
        
        # منطقة المحتوى
        self.setup_content_area(main_frame)

        # القائمة الجانبية
        self.setup_sidebar(main_frame)
        
        # عرض لوحة التحكم افتراضياً
        self.show_dashboard()
    
    def setup_top_bar(self, parent):
        """إعداد شريط الأدوات العلوي"""
        top_bar = ttk.Frame(parent, style='primary.TFrame', height=50)
        top_bar.pack(side='top', fill='x', padx=2, pady=2)
        top_bar.pack_propagate(False)
        
        # عنوان التطبيق
        title_label = ttk.Label(
            top_bar, 
            text="🏪 نظام إدارة السوبر ماركت",
            font=('Arial', 18, 'bold'),
            style='primary.TLabel'
        )
        title_label.pack(side='left', padx=20, pady=10)
        
        # أزرار التحكم
        control_frame = ttk.Frame(top_bar, style='primary.TFrame')
        control_frame.pack(side='right', padx=20, pady=10)
        
        # زر طي/فتح القائمة الجانبية
        self.toggle_btn = ttk.Button(
            control_frame,
            text="☰",
            command=self.toggle_sidebar,
            style='primary.TButton',
            width=3
        )
        self.toggle_btn.pack(side='left', padx=5)
        
        # زر تغيير السمة
        theme_btn = ttk.Button(
            control_frame,
            text="🎨",
            command=self.change_theme,
            style='primary.TButton',
            width=3
        )
        theme_btn.pack(side='left', padx=5)
        
        # زر تحديث
        refresh_btn = ttk.Button(
            control_frame,
            text="🔄",
            command=self.refresh_app,
            style='primary.TButton',
            width=3
        )
        refresh_btn.pack(side='left', padx=5)
    
    def setup_sidebar(self, parent):
        """إعداد القائمة الجانبية القابلة للطي"""
        # إطار القائمة الجانبية
        self.sidebar = ttk.Frame(parent, width=250, style='secondary.TFrame')
        self.sidebar.pack(side='left', fill='y', padx=2, pady=2)
        self.sidebar.pack_propagate(False)
        
        # عنوان القائمة
        self.sidebar_title = ttk.Label(
            self.sidebar, 
            text="نظام السوبر ماركت",
            font=('Arial', 14, 'bold'),
            style='secondary.TLabel'
        )
        self.sidebar_title.pack(pady=20, padx=10)
        
        # قائمة الأزرار
        self.buttons_frame = ttk.Frame(self.sidebar, style='secondary.TFrame')
        self.buttons_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # تعريف الأزرار
        self.menu_buttons = [
            ("🏠", "لوحة التحكم", self.show_dashboard),
            ("📊", "الفئات", self.show_categories),
            ("📦", "المنتجات", self.show_products),
            ("🏪", "الموردين", self.show_suppliers),
            ("💰", "نقطة البيع", self.show_sales),
            ("📥", "المشتريات", self.show_purchases),
            ("💸", "المصروفات", self.show_expenses),
            ("📦", "المخزون", self.show_inventory),
            ("📈", "التقارير", self.show_reports),
            ("ℹ️", "حول البرنامج", self.show_about),
        ]
        
        # إنشاء الأزرار
        self.create_menu_buttons()
    
    def create_menu_buttons(self):
        """إنشاء أزرار القائمة"""
        # مسح الأزرار الحالية
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        for icon, text, command in self.menu_buttons:
            btn_frame = ttk.Frame(self.buttons_frame, style='secondary.TFrame')
            btn_frame.pack(fill='x', pady=3)
            
            if self.sidebar_expanded:
                # الوضع الموسع
                btn = ttk.Button(
                    btn_frame,
                    text=f"{icon} {text}",
                    command=command,
                    style='secondary.TButton',
                    width=20
                )
                btn.pack(fill='x')
            else:
                # الوضع المطوي
                btn = ttk.Button(
                    btn_frame,
                    text=icon,
                    command=command,
                    style='secondary.TButton',
                    width=4
                )
                btn.pack()
                
                # تلميحة للأيقونة
                self.create_tooltip(btn, text)
    
    def create_tooltip(self, widget, text):
        """إنشاء تلميحة للأيقونة"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="#ffffe0", 
                            relief='solid', borderwidth=1, padding=5)
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def setup_content_area(self, parent):
        """إعداد منطقة المحتوى"""
        self.content_frame = ttk.Frame(parent, style='light.TFrame')
        self.content_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
    
    def toggle_sidebar(self):
        """طي أو فتح القائمة الجانبية"""
        self.sidebar_expanded = not self.sidebar_expanded
        
        if self.sidebar_expanded:
            # فتح القائمة
            self.sidebar.config(width=250)
            self.sidebar_title.config(text="نظام السوبر ماركت")
            self.toggle_btn.config(text="☰")
        else:
            # طي القائمة
            self.sidebar.config(width=60)
            self.sidebar_title.config(text="🏪")
            self.toggle_btn.config(text="☰")
        
        # إعادة إنشاء الأزرار
        self.create_menu_buttons()
    
    def change_theme(self):
        """تغيير سمة الواجهة"""
        themes = ['cosmo', 'flatly', 'journal', 'litera', 'lumen', 'minty', 
                 'pulse', 'sandstone', 'united', 'yeti', 'darkly', 'superhero']
        
        current_index = themes.index(self.current_theme)
        next_index = (current_index + 1) % len(themes)
        self.current_theme = themes[next_index]
        
        # تغيير السمة
        self.root.style.theme_use(self.current_theme)
        
        messagebox.showinfo("تغيير السمة", f"تم تغيير السمة إلى: {self.current_theme}")
    
    def refresh_app(self):
        """تحديث التطبيق"""
        current_method = getattr(self, 'current_method', None)
        if current_method:
            current_method()
        messagebox.showinfo("تحديث", "تم تحديث البيانات بنجاح")
    
    def clear_content(self):
        """مسح المحتوى الحالي"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """عرض لوحة التحكم"""
        self.clear_content()
        self.current_method = self.show_dashboard
        DashboardUI(self.content_frame, self.db)
    
    def show_categories(self):
        """عرض إدارة الفئات"""
        self.clear_content()
        self.current_method = self.show_categories
        CategoriesUI(self.content_frame, self.db)
    
    def show_products(self):
        """عرض إدارة المنتجات"""
        self.clear_content()
        self.current_method = self.show_products
        ProductsUI(self.content_frame, self.db)
    
    def show_suppliers(self):
        """عرض إدارة الموردين"""
        self.clear_content()
        self.current_method = self.show_suppliers
        SuppliersUI(self.content_frame, self.db)
    
    def show_sales(self):
        """عرض نقطة البيع"""
        self.clear_content()
        self.current_method = self.show_sales
        SalesUI(self.content_frame, self.db)
    
    def show_purchases(self):
        """عرض إدارة المشتريات"""
        self.clear_content()
        self.current_method = self.show_purchases
        PurchasesUI(self.content_frame, self.db)
    
    def show_expenses(self):
        """عرض إدارة المصروفات"""
        self.clear_content()
        self.current_method = self.show_expenses
        ExpensesUI(self.content_frame, self.db)
    
    def show_inventory(self):
        """عرض المخزون"""
        self.clear_content()
        self.current_method = self.show_inventory
        InventoryUI(self.content_frame, self.db)
    
    def show_reports(self):
        """عرض التقارير"""
        self.clear_content()
        self.current_method = self.show_reports
        ReportsUI(self.content_frame, self.db)
    
    def show_about(self):
        """عرض حول البرنامج"""
        self.clear_content()
        self.current_method = self.show_about
        AboutUI(self.content_frame, self.db)
    
    def run(self):
        """تشغيل التطبيق"""
        self.root.mainloop()

if __name__ == "__main__":
    root = ttkb.Window(themename="cosmo")
    
    # تفعيل دعم RTL (من اليمين إلى اليسار) للغة العربية
    root.option_add('*TButton*justify', 'right')
    root.option_add('*TLabel*justify', 'right')
    root.option_add('*TEntry*justify', 'right')
    
    app = SupermarketApp(root)
    app.run()
