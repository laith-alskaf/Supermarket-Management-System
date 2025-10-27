import tkinter as tk
from tkinter import ttk

class AboutUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة حول البرنامج"""
        # إنشاء Canvas و Scrollbar للسكرول
        main_canvas = tk.Canvas(self.parent)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # تفعيل السكرول بالماوس
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # المحتوى الرئيسي
        content_frame = ttk.Frame(scrollable_frame)
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # العنوان الرئيسي
        title = ttk.Label(
            content_frame,
            text="🏪 نظام إدارة السوبر ماركت",
            font=('Arial', 24, 'bold'),
            foreground='#2c3e50'
        )
        title.pack(pady=(0, 30))
        
        # وصف البرنامج
        description_frame = ttk.LabelFrame(content_frame, text="نبذة عن البرنامج", padding=20)
        description_frame.pack(fill='x', pady=15)
        
        description_text = """نظام إدارة شامل ومتكامل للسوبر ماركت يساعدك على:
        
• إدارة المخزون والمنتجات بكفاءة عالية
• تتبع المبيعات والمشتريات بدقة
• إصدار تقارير تفصيلية ورسوم بيانية
• إدارة الموردين والعملاء
• نظام نقطة بيع سريع وسهل الاستخدام
• دعم العملات المتعددة (ليرة سورية ودولار)
• واجهة عربية سهلة الاستخدام
"""
        
        desc_label = ttk.Label(
            description_frame,
            text=description_text,
            font=('Arial', 11),
            justify='right',
            wraplength=700
        )
        desc_label.pack(anchor='e')
        
        # معلومات النسخة
        version_frame = ttk.LabelFrame(content_frame, text="معلومات النسخة", padding=20)
        version_frame.pack(fill='x', pady=15)
        
        version_info = [
            ("📦 النسخة:", "1.0.0"),
            ("📅 تاريخ الإصدار:", "2025"),
            ("🔧 بيئة التطوير:", "Python 3.x + Tkinter"),
            ("🗄️ قاعدة البيانات:", "SQLite")
        ]
        
        for label, value in version_info:
            row_frame = ttk.Frame(version_frame)
            row_frame.pack(fill='x', pady=5)
            
            ttk.Label(
                row_frame,
                text=value,
                font=('Arial', 11)
            ).pack(side='left', padx=10)
            
            ttk.Label(
                row_frame,
                text=label,
                font=('Arial', 11, 'bold')
            ).pack(side='right', padx=10)
        
        # معلومات المطور
        developer_frame = ttk.LabelFrame(content_frame, text="معلومات المطور", padding=20)
        developer_frame.pack(fill='x', pady=15)
        
        # اسم المطور
        dev_name_frame = ttk.Frame(developer_frame)
        dev_name_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            dev_name_frame,
            text="المهندس ليث السكاف",
            font=('Arial', 16, 'bold'),
            foreground='#2980b9'
        ).pack(side='right', padx=10)
        
        ttk.Label(
            dev_name_frame,
            text="👨‍💻 المطور:",
            font=('Arial', 14, 'bold')
        ).pack(side='right', padx=10)
        
        # خط فاصل
        separator = ttk.Separator(developer_frame, orient='horizontal')
        separator.pack(fill='x', pady=15)
        
        # معلومات الاتصال
        contact_title = ttk.Label(
            developer_frame,
            text="📞 للتواصل والاقتراحات:",
            font=('Arial', 12, 'bold'),
            foreground='#16a085'
        )
        contact_title.pack(anchor='e', pady=(10, 15))
        
        contact_info = [
            ("📱 رقم الهاتف:", "+963982055788", "#27ae60"),
            ("📧 البريد الإلكتروني:", "laithalskaf@gmail.com", "#e74c3c")
        ]
        
        for label, value, color in contact_info:
            contact_row = ttk.Frame(developer_frame)
            contact_row.pack(fill='x', pady=8)
            
            # القيمة (قابلة للنسخ)
            value_label = tk.Label(
                contact_row,
                text=value,
                font=('Arial', 12),
                foreground=color,
                cursor="hand2",
                bg='#ecf0f1',
                padx=10,
                pady=5,
                relief='ridge'
            )
            value_label.pack(side='left', padx=10)
            
            # نسخ عند النقر
            def copy_to_clipboard(text):
                self.parent.clipboard_clear()
                self.parent.clipboard_append(text)
                
            value_label.bind('<Button-1>', lambda e, t=value: copy_to_clipboard(t))
            
            ttk.Label(
                contact_row,
                text=label,
                font=('Arial', 12, 'bold')
            ).pack(side='right', padx=10)
        
        # رسالة للتطوير والاقتراحات
        suggestion_frame = ttk.Frame(developer_frame)
        suggestion_frame.pack(fill='x', pady=20)
        
        suggestion_text = "💡 نرحب بجميع الاقتراحات والملاحظات لتطوير البرنامج"
        ttk.Label(
            suggestion_frame,
            text=suggestion_text,
            font=('Arial', 11, 'italic'),
            foreground='#7f8c8d'
        ).pack()
        
        # حقوق النشر
        copyright_frame = ttk.Frame(content_frame)
        copyright_frame.pack(fill='x', pady=30)
        
        copyright_text = "© 2025 جميع الحقوق محفوظة\nتم التطوير بـ ❤️ في سوريا 🇸🇾"
        ttk.Label(
            copyright_frame,
            text=copyright_text,
            font=('Arial', 10),
            foreground='#95a5a6',
            justify='center'
        ).pack()
        
        # عرض Canvas و Scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
