from arabic_reshaper import reshape
from bidi.algorithm import get_display

def prepare_arabic_text(text):
    """تحضير النص العربي للعرض الصحيح"""
    if text:
        reshaped_text = reshape(text)
        return get_display(reshaped_text)
    return text

def format_currency(amount, currency='ل.س'):
    """تنسيق المبلغ المالي"""
    return f"{amount:,.2f} {currency}"

def format_number(number):
    """تنسيق الأرقام"""
    return f"{number:,.2f}"
