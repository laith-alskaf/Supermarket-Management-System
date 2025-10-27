import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pytz

class ExpensesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        self.load_expenses()
        
    def setup_ui(self):
        """إعداد واجهة إدارة المصروفات"""
        # العنوان
        title = ttk.Label(
            self.parent,
            text="إدارة المصروفات",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار النموذج
        form_frame = ttk.LabelFrame(self.parent, text="إضافة مصروف جديد", padding=20)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # فئة المصروف
        ttk.Label(form_frame, text="فئة المصروف:", font=('Arial', 11)).grid(row=0, column=1, padx=10, pady=10, sticky='e')
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, font=('Arial', 11), width=28)
        category_combo['values'] = ['رواتب', 'إيجار', 'كهرباء', 'ماء', 'صيانة', 'مواصلات', 'اتصالات', 'تسويق', 'أخرى']
        category_combo.grid(row=0, column=0, padx=10, pady=10)
        
        # الوصف
        ttk.Label(form_frame, text="الوصف:", font=('Arial', 11)).grid(row=1, column=1, padx=10, pady=10, sticky='e')
        self.desc_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.desc_entry.grid(row=1, column=0, padx=10, pady=10)
        
        # المبلغ بالليرة
        ttk.Label(form_frame, text="المبلغ (ل.س):", font=('Arial', 11)).grid(row=2, column=1, padx=10, pady=10, sticky='e')
        self.amount_syp_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.amount_syp_entry.insert(0, '0')
        self.amount_syp_entry.grid(row=2, column=0, padx=10, pady=10)
        
        # المبلغ بالدولار
        ttk.Label(form_frame, text="المبلغ ($):", font=('Arial', 11)).grid(row=3, column=1, padx=10, pady=10, sticky='e')
        self.amount_usd_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.amount_usd_entry.insert(0, '0')
        self.amount_usd_entry.grid(row=3, column=0, padx=10, pady=10)
        
        # التاريخ
        ttk.Label(form_frame, text="التاريخ:", font=('Arial', 11)).grid(row=4, column=1, padx=10, pady=10, sticky='e')
        self.date_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        # استخدام التوقيت السوري
        syria_time = datetime.now(self.syria_tz)
        self.date_entry.insert(0, syria_time.strftime('%Y-%m-%d %H:%M:%S'))
        self.date_entry.grid(row=4, column=0, padx=10, pady=10)
        
        # الأزرار
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            buttons_frame,
            text="إضافة",
            command=self.add_expense,
            style='success.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="مسح الحقول",
            command=self.clear_fields,
            style='secondary.TButton'
        ).pack(side='right', padx=5)
        
        # جدول المصروفات
        table_frame = ttk.LabelFrame(self.parent, text="سجل المصروفات", padding=10)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # إنشاء الجدول
        columns = ('id', 'category', 'description', 'amount_syp', 'amount_usd', 'date')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # تعريف الأعمدة
        self.tree.heading('id', text='الرقم')
        self.tree.heading('category', text='الفئة')
        self.tree.heading('description', text='الوصف')
        self.tree.heading('amount_syp', text='المبلغ (ل.س)')
        self.tree.heading('amount_usd', text='المبلغ ($)')
        self.tree.heading('date', text='التاريخ')
        
        # عرض الأعمدة
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('category', width=120, anchor='center')
        self.tree.column('description', width=250, anchor='center')
        self.tree.column('amount_syp', width=120, anchor='center')
        self.tree.column('amount_usd', width=120, anchor='center')
        self.tree.column('date', width=150, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='right', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # قائمة النقر بالزر الأيمن
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="حذف", command=self.delete_expense)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # الإجماليات
        totals_frame = ttk.Frame(self.parent)
        totals_frame.pack(fill='x', padx=20, pady=10)
        
        self.total_syp_label = ttk.Label(totals_frame, text="إجمالي المصروفات (ل.س): 0.00", 
                                         font=('Arial', 13, 'bold'), foreground='red')
        self.total_syp_label.pack(side='right', padx=20)
        
        self.total_usd_label = ttk.Label(totals_frame, text="إجمالي المصروفات ($): 0.00", 
                                         font=('Arial', 13, 'bold'), foreground='red')
        self.total_usd_label.pack(side='left', padx=20)
        
    def load_expenses(self):
        """تحميل المصروفات"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # جلب البيانات
        expenses = self.db.fetch_all("SELECT * FROM expenses ORDER BY id DESC")
        
        total_syp = 0
        total_usd = 0
        
        # إضافة البيانات للجدول
        for expense in expenses:
            self.tree.insert('', 'end', values=expense)
            total_syp += expense[3]
            total_usd += expense[4]
        
        # تحديث الإجماليات
        self.total_syp_label.config(text=f"إجمالي المصروفات (ل.س): {total_syp:,.2f}")
        self.total_usd_label.config(text=f"إجمالي المصروفات ($): {total_usd:,.2f}")
    
    def add_expense(self):
        """إضافة مصروف جديد"""
        category = self.category_var.get().strip()
        description = self.desc_entry.get().strip()
        date = self.date_entry.get().strip()
        
        try:
            amount_syp = float(self.amount_syp_entry.get() or 0)
            amount_usd = float(self.amount_usd_entry.get() or 0)
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح")
            return
        
        if not category:
            messagebox.showerror("خطأ", "يرجى اختيار فئة المصروف")
            return
        
        if not description:
            messagebox.showerror("خطأ", "يرجى إدخال وصف المصروف")
            return
        
        if amount_syp <= 0 and amount_usd <= 0:
            messagebox.showerror("خطأ", "يرجى إدخال مبلغ أكبر من صفر")
            return
        
        # إضافة للقاعدة
        if self.db.execute_query(
            "INSERT INTO expenses (category, description, amount_syp, amount_usd, expense_date) VALUES (?, ?, ?, ?, ?)",
            (category, description, amount_syp, amount_usd, date)
        ):
            messagebox.showinfo("نجاح", "تمت إضافة المصروف بنجاح")
            self.clear_fields()
            self.load_expenses()
        else:
            messagebox.showerror("خطأ", "فشل في إضافة المصروف")
    
    def delete_expense(self):
        """حذف مصروف"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار مصروف للحذف")
            return
        
        expense_id = self.tree.item(selected[0])['values'][0]
        
        # تأكيد الحذف
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا المصروف؟"):
            if self.db.execute_query("DELETE FROM expenses WHERE id = ?", (expense_id,)):
                messagebox.showinfo("نجاح", "تم حذف المصروف بنجاح")
                self.load_expenses()
            else:
                messagebox.showerror("خطأ", "فشل في حذف المصروف")
    
    def show_context_menu(self, event):
        """عرض قائمة النقر بالزر الأيمن"""
        self.context_menu.post(event.x_root, event.y_root)
    
    def clear_fields(self):
        """مسح الحقول"""
        self.category_var.set('')
        self.desc_entry.delete(0, 'end')
        self.amount_syp_entry.delete(0, 'end')
        self.amount_syp_entry.insert(0, '0')
        self.amount_usd_entry.delete(0, 'end')
        self.amount_usd_entry.insert(0, '0')
        self.date_entry.delete(0, 'end')
        syria_time = datetime.now(self.syria_tz)
        self.date_entry.insert(0, syria_time.strftime('%Y-%m-%d %H:%M:%S'))
