import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QMessageBox, QTextEdit, QListWidget)
from PyQt5.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self, switch_to_chat):
        super().__init__()
        self.switch_to_chat = switch_to_chat
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("Bem-vindo ao ChatApp")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Nome de usuário")
        self.user_input.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 5px;")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Senha")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 5px;")
        layout.addWidget(self.pass_input)

        login_btn = QPushButton("Entrar")
        login_btn.setStyleSheet("background-color: #0078D7; color: white; padding: 10px; font-size: 14px; border-radius: 5px; font-weight: bold;")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def handle_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        if username and password:
            self.switch_to_chat(username)
        else:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos!")

class ChatWindow(QWidget):
    def __init__(self, username, logout_callback):
        super().__init__()
        self.username = username
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Sidebar com conversas
        sidebar = QVBoxLayout()
        sidebar_label = QLabel(f"Logado como: <b>{self.username}</b>")
        sidebar.addWidget(sidebar_label)

        self.contacts_list = QListWidget()
        self.contacts_list.addItems(["Geral", "Trabalho", "Amigos", "Suporte"])
        sidebar.addWidget(self.contacts_list)

        logout_btn = QPushButton("Sair")
        logout_btn.setStyleSheet("background-color: #d9534f; color: white; padding: 5px; border-radius: 3px;")
        logout_btn.clicked.connect(self.logout_callback)
        sidebar.addWidget(logout_btn)

        # Área de chat principal
        chat_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; padding: 10px;")
        chat_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Digite sua mensagem...")
        self.msg_input.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 5px;")
        self.msg_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.msg_input)

        send_btn = QPushButton("Enviar")
        send_btn.setStyleSheet("background-color: #5cb85c; color: white; padding: 10px 20px; font-size: 14px; border-radius: 5px; font-weight: bold;")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        chat_layout.addLayout(input_layout)

        layout.addLayout(sidebar, 1)
        layout.addLayout(chat_layout, 3)
        self.setLayout(layout)

        # Mensagem inicial
        self.chat_display.append(f"<b>Sistema:</b> Bem-vindo ao chat, {self.username}!")

    def send_message(self):
        text = self.msg_input.text().strip()
        if text:
            self.chat_display.append(f"<b>{self.username}:</b> {text}")
            self.msg_input.clear()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatApp - Login e Mensagens")
        self.setGeometry(100, 100, 700, 450)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_window = LoginWindow(self.switch_to_chat)
        self.stacked_widget.addWidget(self.login_window)

    def switch_to_chat(self, username):
        self.chat_window = ChatWindow(username, self.switch_to_login)
        self.stacked_widget.addWidget(self.chat_window)
        self.stacked_widget.setCurrentWidget(self.chat_window)

    def switch_to_login(self):
        self.stacked_widget.setCurrentWidget(self.login_window)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
