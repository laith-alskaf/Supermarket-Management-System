import tkinter as tk
from tkinter import ttk, messagebox

class CategoriesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        self.load_categories()
        
    def setup_ui(self):
        """إعداد واجهة إدارة الفئات"""
        # العنوان
        title = ttk.Label(
            self.parent,
            text="إدارة الفئات",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار النموذج
        form_frame = ttk.LabelFrame(self.parent, text="إضافة/تعديل فئة", padding=20)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # اسم الفئة
        ttk.Label(form_frame, text="اسم الفئة:", font=('Arial', 11)).grid(row=0, column=1, padx=10, pady=10, sticky='e')
        self.name_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.name_entry.grid(row=0, column=0, padx=10, pady=10)
        
        # الوصف
        ttk.Label(form_frame, text="الوصف:", font=('Arial', 11)).grid(row=1, column=1, padx=10, pady=10, sticky='e')
        self.desc_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.desc_entry.grid(row=1, column=0, padx=10, pady=10)
        
        # الأزرار
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            buttons_frame,
            text="إضافة",
            command=self.add_category,
            style='success.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="تحديث",
            command=self.update_category,
            style='info.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="حذف",
            command=self.delete_category,
            style='danger.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="مسح الحقول",
            command=self.clear_fields,
            style='secondary.TButton'
        ).pack(side='right', padx=5)
        
        # جدول الفئات
        table_frame = ttk.LabelFrame(self.parent, text="قائمة الفئات", padding=10)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # إنشاء الجدول
        columns = ('id', 'name', 'description', 'created_at')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # تعريف الأعمدة
        self.tree.heading('id', text='الرقم')
        self.tree.heading('name', text='اسم الفئة')
        self.tree.heading('description', text='الوصف')
        self.tree.heading('created_at', text='تاريخ الإنشاء')
        
        # عرض الأعمدة
        self.tree.column('id', width=80, anchor='center')
        self.tree.column('name', width=200, anchor='center')
        self.tree.column('description', width=300, anchor='center')
        self.tree.column('created_at', width=150, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='right', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # ربط حدث النقر
        self.tree.bind('<ButtonRelease-1>', self.on_select)
        
    def load_categories(self):
        """تحميل الفئات"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # جلب البيانات
        categories = self.db.fetch_all("SELECT * FROM categories ORDER BY id DESC")
        
        # إضافة البيانات للجدول
        for category in categories:
            self.tree.insert('', 'end', values=category)
    
    def add_category(self):
        """إضافة فئة جديدة"""
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم الفئة")
            return
        
        # إضافة للقاعدة
        if self.db.execute_query(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (name, description)
        ):
            messagebox.showinfo("نجاح", "تمت إضافة الفئة بنجاح")
            self.clear_fields()
            self.load_categories()
        else:
            messagebox.showerror("خطأ", "فشل في إضافة الفئة")
    
    def update_category(self):
        """تحديث فئة"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار فئة للتحديث")
            return
        
        category_id = self.tree.item(selected[0])['values'][0]
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم الفئة")
            return
        
        # تحديث في القاعدة
        if self.db.execute_query(
            "UPDATE categories SET name = ?, description = ? WHERE id = ?",
            (name, description, category_id)
        ):
            messagebox.showinfo("نجاح", "تم تحديث الفئة بنجاح")
            self.clear_fields()
            self.load_categories()
        else:
            messagebox.showerror("خطأ", "فشل في تحديث الفئة")
    
    def delete_category(self):
        """حذف فئة"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار فئة للحذف")
            return
        
        category_id = self.tree.item(selected[0])['values'][0]
        
        # تأكيد الحذف
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذه الفئة؟"):
            if self.db.execute_query("DELETE FROM categories WHERE id = ?", (category_id,)):
                messagebox.showinfo("نجاح", "تم حذف الفئة بنجاح")
                self.clear_fields()
                self.load_categories()
            else:
                messagebox.showerror("خطأ", "فشل في حذف الفئة")
    
    def on_select(self, event):
        """عند اختيار فئة من الجدول"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            
            self.name_entry.delete(0, 'end')
            self.name_entry.insert(0, values[1])
            
            self.desc_entry.delete(0, 'end')
            self.desc_entry.insert(0, values[2] if values[2] else '')
    
    def clear_fields(self):
        """مسح الحقول"""
        self.name_entry.delete(0, 'end')
        self.desc_entry.delete(0, 'end')
        # إلغاء التحديد
        for item in self.tree.selection():
            self.tree.selection_remove(item)
