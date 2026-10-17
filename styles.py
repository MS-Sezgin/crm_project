"""Shared colour themes and stylesheet template.

Every window uses the same stylesheet template, so the whole app shares one
visual language. Only the accent colours change per page, which lets the user
see which section they are in.
"""

THEMES = {
    "login":             dict(accent="#3F7CAC", hover="#5390BF", pressed="#2F6490", bg="#F5F8FB", sub="#E3EEF7", alt="#FAFCFE"),
    "preferences":       dict(accent="#3E9C7E", hover="#52AD90", pressed="#31826A", bg="#F3FAF7", sub="#DDF2EA", alt="#F9FDFB"),
    "preferences_admin": dict(accent="#B5692E", hover="#C77A3D", pressed="#9A5624", bg="#FDF6F1", sub="#F7E2D3", alt="#FEFAF7"),
    "applications":      dict(accent="#6E5EA8", hover="#8072B8", pressed="#5A4B8E", bg="#F7F6FB", sub="#E6E1F5", alt="#FBFAFD"),
    "mentor_interview":  dict(accent="#3F8FA0", hover="#55A3B3", pressed="#327483", bg="#F2F9FA", sub="#D9EEF2", alt="#F8FCFD"),
    "interviews":        dict(accent="#7D8F45", hover="#8FA255", pressed="#67763A", bg="#F8F9F2", sub="#E6EDCF", alt="#FCFDF8"),
    "admin_menu":        dict(accent="#5A6172", hover="#6E7589", pressed="#474D5C", bg="#F4F5F7", sub="#DDE0E8", alt="#FAFAFB"),
}

BASE = dict(text="#1E2A38", border="#D0D7DF", muted="#66727F", card="#FFFFFF")

DANGER = dict(base="#C8553F", hover="#D9694F", pressed="#AD4531")


def build_stylesheet(theme):
    t = {**BASE, **theme}
    return f"""
#pageRoot {{ background-color: {t['bg']}; }}
QLabel {{ background: transparent; color: {t['text']}; font-size: 13px; }}
QLabel#headerTitle {{ color: #FFFFFF; font-size: 22px; font-weight: 700; }}
QLabel#headerSub {{ color: #FFFFFF; font-size: 12px; }}
#headerBar {{ background-color: {t['accent']}; border-radius: 12px; }}
#card {{ background-color: {t['card']}; border: 1px solid {t['border']}; border-radius: 12px; }}
#card QLabel {{ color: {t['muted']}; font-size: 12px; font-weight: 600; }}
QLabel#labelMuted {{ color: {t['muted']}; font-size: 13px; font-style: italic; font-weight: 400; }}
QLabel#labelWarning {{ color: #B03A2E; font-size: 12px; font-weight: 600; }}
QLabel#labelBadge {{ background-color: {t['accent']}; color: #FFFFFF; border-radius: 10px; padding: 4px 12px; font-size: 11px; font-weight: 700; }}
QLineEdit, QComboBox {{ background-color: #FFFFFF; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 8px 10px; min-height: 20px; }}
QLineEdit:hover, QComboBox:hover {{ border: 1px solid {t['accent']}; }}
QLineEdit:focus, QComboBox:focus {{ border: 2px solid {t['accent']}; }}
QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox QAbstractItemView {{ background-color: #FFFFFF; border: 1px solid {t['border']}; selection-background-color: {t['accent']}; selection-color: #FFFFFF; }}
QPushButton {{ background-color: {t['accent']}; color: #FFFFFF; border: 1px solid {t['accent']}; border-radius: 8px; padding: 10px 18px; font-weight: 600; }}
QPushButton:hover {{ background-color: {t['hover']}; border: 1px solid {t['pressed']}; }}
QPushButton:pressed {{ background-color: {t['pressed']}; border: 1px solid {t['pressed']}; padding-top: 11px; padding-bottom: 9px; }}
QPushButton#btnClose, QPushButton#btnExit {{ background-color: {DANGER['base']}; border: 1px solid {DANGER['base']}; }}
QPushButton#btnClose:hover, QPushButton#btnExit:hover {{ background-color: {DANGER['hover']}; border: 1px solid {DANGER['pressed']}; }}
QPushButton#btnClose:pressed, QPushButton#btnExit:pressed {{ background-color: {DANGER['pressed']}; border: 1px solid {DANGER['pressed']}; padding-top: 11px; padding-bottom: 9px; }}
QTableWidget {{ background-color: #FFFFFF; alternate-background-color: {t['alt']}; border: 1px solid {t['border']}; border-radius: 8px; gridline-color: #E3E8EE; selection-background-color: {t['sub']}; selection-color: {t['text']}; }}
QHeaderView::section {{ background-color: {t['accent']}; color: #FFFFFF; padding: 8px; border: none; font-weight: 600; }}
"""
