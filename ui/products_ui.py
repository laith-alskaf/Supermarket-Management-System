import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ProductsUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        self.load_products()
        
    def setup_ui(self):
        """إعداد واجهة إدارة المنتجات"""
        # العنوان
        title = ttk.Label(
            self.parent,
            text="إدارة المنتجات",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار البحث
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(search_frame, text="بحث:", font=('Arial', 11)).pack(side='right', padx=10)
        self.search_entry = ttk.Entry(search_frame, font=('Arial', 11), width=30)
        self.search_entry.pack(side='right', padx=10)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_products())
        
        ttk.Button(
            search_frame,
            text="إضافة منتج جديد",
            command=self.show_add_dialog,
            style='success.TButton'
        ).pack(side='left', padx=10)
        
        # جدول المنتجات
        table_frame = ttk.LabelFrame(self.parent, text="قائمة المنتجات", padding=10)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # إنشاء الجدول
        columns = ('id', 'name', 'category', 'quantity', 'unit', 'price_syp', 'price_usd')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # تعريف الأعمدة
        self.tree.heading('id', text='الرقم')
        self.tree.heading('name', text='اسم المنتج')
        self.tree.heading('category', text='الفئة')
        self.tree.heading('quantity', text='الكمية')
        self.tree.heading('unit', text='الوحدة')
        self.tree.heading('price_syp', text='السعر (ل.س)')
        self.tree.heading('price_usd', text='السعر ($)')
        
        # عرض الأعمدة
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('name', width=200, anchor='center')
        self.tree.column('category', width=150, anchor='center')
        self.tree.column('quantity', width=100, anchor='center')
        self.tree.column('unit', width=80, anchor='center')
        self.tree.column('price_syp', width=120, anchor='center')
        self.tree.column('price_usd', width=100, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='right', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # ربط النقر المزدوج للتعديل
        self.tree.bind('<Double-1>', self.show_edit_dialog)
        
        # قائمة النقر بالزر الأيمن
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="تعديل", command=self.show_edit_dialog)
        self.context_menu.add_command(label="حذف", command=self.delete_product)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
    def load_products(self):
        """تحميل المنتجات"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # جلب البيانات
        query = """
            SELECT p.id, p.name, 
                   COALESCE(c.name, 'بدون فئة'), 
                   p.quantity, p.unit, 
                   p.selling_price_syp, p.selling_price_usd
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id DESC
        """
        products = self.db.fetch_all(query)
        
        # إضافة البيانات للجدول
        for product in products:
            # تلوين المنتجات القريبة من النفاد
            self.tree.insert('', 'end', values=product)
    
    def search_products(self):
        """البحث عن منتجات"""
        search_term = self.search_entry.get().strip()
        
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # جلب البيانات
        query = """
            SELECT p.id, p.name, 
                   COALESCE(c.name, 'بدون فئة'), 
                   p.quantity, p.unit, 
                   p.selling_price_syp, p.selling_price_usd
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.name LIKE ? OR c.name LIKE ?
            ORDER BY p.id DESC
        """
        products = self.db.fetch_all(query, (f'%{search_term}%', f'%{search_term}%'))
        
        # إضافة البيانات للجدول
        for product in products:
            self.tree.insert('', 'end', values=product)
    
    def show_add_dialog(self, event=None):
        """عرض نافذة إضافة منتج"""
        self.show_product_dialog()
    
    def show_edit_dialog(self, event=None):
        """عرض نافذة تعديل منتج"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار منتج للتعديل")
            return
        
        product_id = self.tree.item(selected[0])['values'][0]
        self.show_product_dialog(product_id)
    
    def show_product_dialog(self, product_id=None):
        """عرض نافذة إضافة/تعديل منتج"""
        # إنشاء نافذة جديدة
        dialog = tk.Toplevel(self.parent)
        dialog.title("إضافة منتج" if product_id is None else "تعديل منتج")
        dialog.geometry("600x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # الحصول على بيانات المنتج إذا كان تعديل
        product_data = None
        if product_id:
            product_data = self.db.fetch_one(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            )
        
        # النموذج
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        row = 0
        
        # اسم المنتج
        ttk.Label(form_frame, text="اسم المنتج:", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        name_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        name_entry.grid(row=row, column=0, padx=10, pady=10)
        if product_data:
            name_entry.insert(0, product_data[1])
        row += 1
        
        # الفئة
        ttk.Label(form_frame, text="الفئة:", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, font=('Arial', 11), width=28, state='readonly')
        
        # جلب الفئات
        categories = self.db.fetch_all("SELECT id, name FROM categories")
        category_dict = {cat[1]: cat[0] for cat in categories}
        category_combo['values'] = list(category_dict.keys())
        category_combo.grid(row=row, column=0, padx=10, pady=10)
        
        if product_data and product_data[2]:
            cat_name = self.db.fetch_one("SELECT name FROM categories WHERE id = ?", (product_data[2],))
            if cat_name:
                category_var.set(cat_name[0])
        row += 1
        
        # سعر الشراء ليرة
        ttk.Label(form_frame, text="سعر الشراء (ل.س):", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        purchase_syp_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        purchase_syp_entry.grid(row=row, column=0, padx=10, pady=10)
        if product_data:
            purchase_syp_entry.insert(0, str(product_data[3]))
        row += 1
        
        # سعر الشراء دولار
        ttk.Label(form_frame, text="سعر الشراء ($):", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        purchase_usd_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        purchase_usd_entry.grid(row=row, column=0, padx=10, pady=10)
        if product_data:
            purchase_usd_entry.insert(0, str(product_data[4]))
        row += 1
        
        # سعر البيع ليرة
        ttk.Label(form_frame, text="سعر البيع (ل.س):", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        selling_syp_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        selling_syp_entry.grid(row=row, column=0, padx=10, pady=10)
        if product_data:
            selling_syp_entry.insert(0, str(product_data[5]))
        row += 1
        
        # سعر البيع دولار
        ttk.Label(form_frame, text="سعر البيع ($):", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        selling_usd_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        selling_usd_entry.grid(row=row, column=0, padx=10, pady=10)
        if product_data:
            selling_usd_entry.insert(0, str(product_data[6]))
        row += 1
        
        # الكمية
        ttk.Label(form_frame, text="الكمية:", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        quantity_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        quantity_entry.grid(row=row, column=0, padx=10, pady=10)
        if product_data:
            quantity_entry.insert(0, str(product_data[7]))
        row += 1
        
        # الحد الأدنى
        ttk.Label(form_frame, text="الحد الأدنى للتنبيه:", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        min_quantity_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        min_quantity_entry.grid(row=row, column=0, padx=10, pady=10)
        if product_data:
            min_quantity_entry.insert(0, str(product_data[8]))
        row += 1
        
        # الوحدة
        ttk.Label(form_frame, text="الوحدة:", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='e')
        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(form_frame, textvariable=unit_var, font=('Arial', 11), width=28)
        unit_combo['values'] = ['قطعة', 'كيلو', 'ليتر', 'علبة', 'كرتونة', 'متر']
        unit_combo.grid(row=row, column=0, padx=10, pady=10)
        if product_data:
            unit_var.set(product_data[9])
        else:
            unit_var.set('قطعة')
        row += 1
        
        # الوصف
        ttk.Label(form_frame, text="الوصف:", font=('Arial', 11)).grid(row=row, column=1, padx=10, pady=10, sticky='ne')
        desc_text = tk.Text(form_frame, font=('Arial', 11), width=30, height=4)
        desc_text.grid(row=row, column=0, padx=10, pady=10)
        if product_data and product_data[10]:
            desc_text.insert('1.0', product_data[10])
        row += 1
        
        # الأزرار
        def save_product():
            name = name_entry.get().strip()
            category_name = category_var.get()
            category_id = category_dict.get(category_name) if category_name else None
            
            try:
                purchase_syp = float(purchase_syp_entry.get() or 0)
                purchase_usd = float(purchase_usd_entry.get() or 0)
                selling_syp = float(selling_syp_entry.get() or 0)
                selling_usd = float(selling_usd_entry.get() or 0)
                quantity = float(quantity_entry.get() or 0)
                min_quantity = float(min_quantity_entry.get() or 0)
            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة")
                return
            
            unit = unit_var.get()
            description = desc_text.get('1.0', 'end-1c').strip()
            
            if not name:
                messagebox.showerror("خطأ", "يرجى إدخال اسم المنتج")
                return
            
            if product_id:
                # تحديث
                query = """
                    UPDATE products SET 
                    name = ?, category_id = ?, 
                    purchase_price_syp = ?, purchase_price_usd = ?,
                    selling_price_syp = ?, selling_price_usd = ?,
                    quantity = ?, min_quantity = ?, unit = ?,
                    description = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                params = (name, category_id, purchase_syp, purchase_usd,
                         selling_syp, selling_usd, quantity, min_quantity,
                         unit, description, product_id)
            else:
                # إضافة
                query = """
                    INSERT INTO products 
                    (name, category_id, purchase_price_syp, purchase_price_usd,
                     selling_price_syp, selling_price_usd, quantity, min_quantity,
                     unit, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (name, category_id, purchase_syp, purchase_usd,
                         selling_syp, selling_usd, quantity, min_quantity,
                         unit, description)
            
            if self.db.execute_query(query, params):
                messagebox.showinfo("نجاح", "تم حفظ المنتج بنجاح")
                dialog.destroy()
                self.load_products()
            else:
                messagebox.showerror("خطأ", "فشل في حفظ المنتج")
        
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            buttons_frame,
            text="حفظ",
            command=save_product,
            style='success.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="إلغاء",
            command=dialog.destroy,
            style='secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_product(self):
        """حذف منتج"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار منتج للحذف")
            return
        
        product_id = self.tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا المنتج؟"):
            if self.db.execute_query("DELETE FROM products WHERE id = ?", (product_id,)):
                messagebox.showinfo("نجاح", "تم حذف المنتج بنجاح")
                self.load_products()
            else:
                messagebox.showerror("خطأ", "فشل في حذف المنتج")
    
    def show_context_menu(self, event):
        """عرض قائمة النقر بالزر الأيمن"""
        self.context_menu.post(event.x_root, event.y_root)
