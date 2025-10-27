import tkinter as tk
from tkinter import ttk
import webbrowser

class AboutUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة "حول البرنامج" بتصميم احترافي"""
        # إعداد الإطار الرئيسي القابل للتمرير
        main_canvas = tk.Canvas(self.parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # الإطار الداخلي للمحتوى
        content_frame = ttk.Frame(scrollable_frame, padding="30 40")
        content_frame.pack(fill='both', expand=True)
        content_frame.columnconfigure(0, weight=3) # Column for info
        content_frame.columnconfigure(1, weight=2) # Column for developer

        # --- العنوان الرئيسي ---
        title_frame = ttk.Frame(content_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 30), sticky='ew')
        ttk.Label(title_frame, text="🏪", font=('Arial', 30)).pack(side='right', padx=(0, 15))
        ttk.Label(title_frame, text="نظام إدارة السوبر ماركت", font=('Arial', 26, 'bold'), foreground='#2c3e50').pack(side='right')

        # --- العمود الأيمن: معلومات البرنامج ---
        info_column = ttk.Frame(content_frame)
        info_column.grid(row=1, column=0, sticky='nsew', padx=(0, 20))

        # نبذة عن البرنامج
        self.create_info_card(info_column, "📝 نبذة عن البرنامج", 
            """نظام شامل لإدارة السوبر ماركت، مصمم لتبسيط عملياتك اليومية من إدارة المخزون والمبيعات إلى تتبع الأرباح والمصروفات. يتميز بواجهة عربية سهلة الاستخدام ودعم متعدد للعملات.""")

        # معلومات النسخة
        version_details = [
            ("📦 النسخة:", "1.0.0"),
            ("📅 تاريخ الإصدار:", "2025"),
            ("🔧 بيئة التطوير:", "Python 3.x, Tkinter"),
            ("🗄️ قاعدة البيانات:", "SQLite")
        ]
        self.create_details_card(info_column, "ℹ️ معلومات النسخة", version_details)

        # --- العمود الأيسر: معلومات المطور ---
        dev_column = ttk.Frame(content_frame)
        dev_column.grid(row=1, column=1, sticky='nsew')

        # معلومات المطور
        self.create_developer_card(dev_column)

        # --- التذييل ---
        footer_frame = ttk.Frame(content_frame)
        footer_frame.grid(row=2, column=0, columnspan=2, pady=(40, 0), sticky='ew')
        copyright_text = "© 2025 جميع الحقوق محفوظة | تم التطوير بـ ❤️ في سوريا 🇸🇾"
        ttk.Label(footer_frame, text=copyright_text, font=('Arial', 10), foreground='#95a5a6', justify='center').pack()

    def create_info_card(self, parent, title, text):
        card = ttk.LabelFrame(parent, text=title, padding=20)
        card.pack(fill='x', pady=(0, 20))
        ttk.Label(card, text=text, font=('Arial', 11), justify='right', wraplength=450).pack(anchor='e')

    def create_details_card(self, parent, title, details):
        card = ttk.LabelFrame(parent, text=title, padding=20)
        card.pack(fill='x', pady=(0, 20))
        for label, value in details:
            row = ttk.Frame(card)
            row.pack(fill='x', pady=4)
            ttk.Label(row, text=value, font=('Arial', 11)).pack(side='left', padx=10)
            ttk.Label(row, text=label, font=('Arial', 11, 'bold')).pack(side='right', padx=10)

    def create_developer_card(self, parent):
        card = ttk.LabelFrame(parent, text="👨‍💻 المطور", padding=20)
        card.pack(fill='both', expand=True)

        # الاسم
        ttk.Label(card, text="المهندس ليث السكاف", font=('Arial', 18, 'bold'), foreground='#2980b9').pack(anchor='e', pady=(0, 15))
        
        # روابط التواصل
        self.create_contact_link(card, "📧 البريد الإلكتروني", "laithalskaf@gmail.com", self.copy_to_clipboard)
        self.create_contact_link(card, "📱 واتساب", "+963982055788", self.copy_to_clipboard)

        # رسالة ترحيب
        ttk.Separator(card, orient='horizontal').pack(fill='x', pady=(20, 15))
        suggestion_text = "💡 نرحب بجميع الاقتراحات والملاحظات لتطوير البرنامج."
        ttk.Label(card, text=suggestion_text, font=('Arial', 11, 'italic'), foreground='#7f8c8d', justify='right').pack(anchor='e')

    def create_contact_link(self, parent, label, value, command):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=6)
        
        link = tk.Label(row, text=value, font=('Arial', 11, 'underline'), fg="blue", cursor="hand2")
        link.pack(side='left', padx=10)
        link.bind("<Button-1>", lambda e, v=value: command(v))
        
        ttk.Label(row, text=label + ":", font=('Arial', 11, 'bold')).pack(side='right')

    def copy_to_clipboard(self, text):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        messagebox.showinfo("تم النسخ", f"تم نسخ '{text}' إلى الحافظة.", parent=self.parent)

    def open_link(self, url):
        webbrowser.open_new(url)
