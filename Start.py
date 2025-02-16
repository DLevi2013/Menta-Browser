import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLineEdit, QTextEdit,
                            QTabWidget, QLabel, QListWidget, QCalendarWidget,
                            QStackedWidget, QTreeWidget, QTreeWidgetItem,
                            QScrollArea, QFrame, QSplitter, QMenu, QAction,
                            QDialog, QComboBox, QCheckBox, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QIcon, QPixmap
import sqlite3
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Beállítások")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        # Böngésző beállítások
        browser_group = QFrame()
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.addWidget(QLabel("Böngésző beállítások:"))
        
        self.search_engine = QComboBox()
        self.search_engine.addItems(["Google", "Bing", "DuckDuckGo"])
        browser_layout.addWidget(QLabel("Alapértelmezett kereső:"))
        browser_layout.addWidget(self.search_engine)
        
        # Email beállítások
        email_group = QFrame()
        email_layout = QVBoxLayout(email_group)
        email_layout.addWidget(QLabel("Email beállítások:"))
        
        self.smtp_server = QLineEdit()
        self.smtp_port = QLineEdit()
        self.imap_server = QLineEdit()
        self.imap_port = QLineEdit()
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        
        email_layout.addWidget(QLabel("SMTP szerver:"))
        email_layout.addWidget(self.smtp_server)
        email_layout.addWidget(QLabel("SMTP port:"))
        email_layout.addWidget(self.smtp_port)
        email_layout.addWidget(QLabel("IMAP szerver:"))
        email_layout.addWidget(self.imap_server)
        email_layout.addWidget(QLabel("IMAP port:"))
        email_layout.addWidget(self.imap_port)
        email_layout.addWidget(QLabel("Email cím:"))
        email_layout.addWidget(self.email)
        email_layout.addWidget(QLabel("Jelszó:"))
        email_layout.addWidget(self.password)
        
        # Mentés gomb
        save_btn = QPushButton("Mentés")
        save_btn.clicked.connect(self.save_settings)
        
        layout.addWidget(browser_group)
        layout.addWidget(email_group)
        layout.addWidget(save_btn)
        
        self.load_settings()
    
    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.search_engine.setCurrentText(settings.get('search_engine', 'Google'))
                self.smtp_server.setText(settings.get('smtp_server', ''))
                self.smtp_port.setText(settings.get('smtp_port', ''))
                self.imap_server.setText(settings.get('imap_server', ''))
                self.imap_port.setText(settings.get('imap_port', ''))
                self.email.setText(settings.get('email', ''))
                self.password.setText(settings.get('password', ''))
    
    def save_settings(self):
        settings = {
            'search_engine': self.search_engine.currentText(),
            'smtp_server': self.smtp_server.text(),
            'smtp_port': self.smtp_port.text(),
            'imap_server': self.imap_server.text(),
            'imap_port': self.imap_port.text(),
            'email': self.email.text(),
            'password': self.password.text()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        self.accept()

class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        
        # Logó és kereső
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("google_logo.png").scaled(200, 70, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Keresés...")
        self.search_box.returnPressed.connect(self.search)
        
        search_btn = QPushButton("Keresés")
        search_btn.clicked.connect(self.search)
        
        layout.addStretch()
        layout.addWidget(logo_label)
        layout.addWidget(self.search_box)
        layout.addWidget(search_btn)
        layout.addStretch()
    
    def search(self):
        query = self.search_box.text()
        settings = {}
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        
        search_engine = settings.get('search_engine', 'Google')
        if search_engine == 'Google':
            url = f"https://www.google.com/search?q={query}"
        elif search_engine == 'Bing':
            url = f"https://www.bing.com/search?q={query}"
        else:
            url = f"https://duckduckgo.com/?q={query}"
        
        self.main_window.create_new_tab(url)

class EmailClient(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        
        # Email mappaszerkezet
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabel("Mappák")
        inbox = QTreeWidgetItem(["Beérkezett levelek"])
        sent = QTreeWidgetItem(["Elküldött levelek"])
        drafts = QTreeWidgetItem(["Piszkozatok"])
        self.folder_tree.addTopLevelItems([inbox, sent, drafts])
        
        # Email lista és tartalom
        email_content = QWidget()
        email_layout = QVBoxLayout(email_content)
        
        # Email lista
        self.email_list = QListWidget()
        
        # Email tartalom
        self.email_content = QTextEdit()
        self.email_content.setReadOnly(True)
        
        email_layout.addWidget(self.email_list)
        email_layout.addWidget(self.email_content)
        
        # Új email gomb
        new_email_btn = QPushButton("Új email")
        new_email_btn.clicked.connect(self.new_email)
        email_layout.addWidget(new_email_btn)
        
        # Splitter hozzáadása
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.folder_tree)
        splitter.addWidget(email_content)
        
        layout.addWidget(splitter)
        
        self.load_emails()
    
    def load_emails(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                try:
                    mail = imaplib.IMAP4_SSL(settings['imap_server'])
                    mail.login(settings['email'], settings['password'])
                    mail.select('inbox')
                    _, messages = mail.search(None, 'ALL')
                    
                    for num in messages[0].split():
                        _, msg = mail.fetch(num, '(RFC822)')
                        email_body = msg[0][1]
                        email_message = email.message_from_bytes(email_body)
                        self.email_list.addItem(email_message['subject'])
                    
                    mail.logout()
                except Exception as e:
                    print(f"Hiba az emailek betöltésekor: {str(e)}")
    
    def new_email(self):
        compose_dialog = ComposeEmail()
        compose_dialog.exec_()

class ComposeEmail(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Új email")
        layout = QVBoxLayout(self)
        
        self.to_input = QLineEdit()
        self.to_input.setPlaceholderText("Címzett")
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Tárgy")
        self.body_input = QTextEdit()
        
        send_btn = QPushButton("Küldés")
        send_btn.clicked.connect(self.send_email)
        
        layout.addWidget(self.to_input)
        layout.addWidget(self.subject_input)
        layout.addWidget(self.body_input)
        layout.addWidget(send_btn)
    
    def send_email(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                try:
                    msg = MIMEMultipart()
                    msg['From'] = settings['email']
                    msg['To'] = self.to_input.text()
                    msg['Subject'] = self.subject_input.text()
                    msg.attach(MIMEText(self.body_input.toPlainText(), 'plain'))
                    
                    server = smtplib.SMTP(settings['smtp_server'], int(settings['smtp_port']))
                    server.starttls()
                    server.login(settings['email'], settings['password'])
                    server.send_message(msg)
                    server.quit()
                    
                    self.accept()
                except Exception as e:
                    QMessageBox.warning(self, "Hiba", f"Nem sikerült elküldeni az emailt: {str(e)}")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menta Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Központi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Oldalsáv
        sidebar = QWidget()
        sidebar.setMaximumWidth(50)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Oldalsáv ikonok
        home_btn = QPushButton("🏠")
        web_btn = QPushButton("🌐")
        email_btn = QPushButton("✉")
        calendar_btn = QPushButton("📅")
        settings_btn = QPushButton("⚙")
        
        for btn in [home_btn, web_btn, email_btn, calendar_btn, settings_btn]:
            btn.setFixedSize(40, 40)
        
        sidebar_layout.addWidget(home_btn)
        sidebar_layout.addWidget(web_btn)
        sidebar_layout.addWidget(email_btn)
        sidebar_layout.addWidget(calendar_btn)
        sidebar_layout.addWidget(settings_btn)
        sidebar_layout.addStretch()
        
        # Fő tartalom terület
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        
        # Keresősáv
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Keresés vagy URL...")
        search_bar.returnPressed.connect(lambda: self.navigate_to_url(search_bar.text()))
        content_layout.addWidget(search_bar)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        content_layout.addWidget(self.tabs)
        
        # Kezdőlap hozzáadása
        self.home_page = HomePage(self)
        self.tabs.addTab(self.home_page, "Kezdőlap")
        
        # Email kliens
        self.email_client = EmailClient()
        
        # Naptár
        self.calendar = QCalendarWidget()
        
        # Események összekötése
        home_btn.clicked.connect(lambda: self.tabs.setCurrentWidget(self.home_page))
        web_btn.clicked.connect(lambda: self.create_new_tab("about:blank"))
        email_btn.clicked.connect(lambda: self.show_email_client())
        calendar_btn.clicked.connect(lambda: self.show_calendar())
        settings_btn.clicked.connect(self.show_settings)
        
        # Layout összeállítása
        layout.addWidget(sidebar)
        layout.addWidget(content_area)
    
    def create_new_tab(self, url):
        web_view = QWebEngineView()
        web_view.setUrl(QUrl(url))
        self.tabs.addTab(web_view, "Új lap")
        self.tabs.setCurrentWidget(web_view)
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
    
    def show_email_client(self):
        if self.tabs.indexOf(self.email_client) == -1:
            self.tabs.addTab(self.email_client, "Email")
        self.tabs.setCurrentWidget(self.email_client)
    
    def show_calendar(self):
        if self.tabs.indexOf(self.calendar) == -1:
            self.tabs.addTab(self.calendar, "Naptár")
        self.tabs.setCurrentWidget(self.calendar)
    
    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()
    
    def navigate_to_url(self, url_or_search):
        if not url_or_search.startswith(('http://', 'https://')):
            if '.' in url_or_search:
                url = 'http://' + url_or_search
            else:
                settings = {}
                
    def navigate_to_url(self, url_or_search):
        if not url_or_search.startswith(('http://', 'https://')):
            if '.' in url_or_search:
                url = 'http://' + url_or_search
            else:
                settings = {}
                if os.path.exists('settings.json'):
                    with open('settings.json', 'r') as f:
                        settings = json.load(f)
                
                search_engine = settings.get('search_engine', 'Google')
                if search_engine == 'Google':
                    url = f"https://www.google.com/search?q={url_or_search}"
                elif search_engine == 'Bing':
                    url = f"https://www.bing.com/search?q={url_or_search}"
                else:
                    url = f"https://duckduckgo.com/?q={url_or_search}"
        else:
            url = url_or_search
        
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QWebEngineView):
            current_tab.setUrl(QUrl(url))
        else:
            self.create_new_tab(url)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Alkalmazás stílus beállítása
    app.setStyle('Fusion')
    
    browser = Browser()
    browser.show()
    
    sys.exit(app.exec_())