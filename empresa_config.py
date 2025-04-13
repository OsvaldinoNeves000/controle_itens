import os
import shutil
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
)

DB_FILE = "dados.sqlite"

class EmpresaConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração da Empresa")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout()

        # Layout horizontal para logo + botão lado a lado
        logo_layout = QHBoxLayout()
        self.logo_label = QLabel("Nenhuma logo carregada")
        self.logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.logo_label.setFixedHeight(128)

        self.btn_logo = QPushButton("Selecionar Logo")
        self.btn_logo.clicked.connect(self.selecionar_logo)

        logo_layout.addWidget(self.logo_label)
        logo_layout.addWidget(self.btn_logo)

        self.nome_input = QLineEdit()
        self.nome_input.setStyleSheet("margin-bottom: 4px;")
        self.telefone_input = QLineEdit()
        self.telefone_input.setStyleSheet("margin-bottom: 4px;")
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setStyleSheet("margin-bottom: 4px;")
        self.endereco_input = QLineEdit()
        self.endereco_input.setStyleSheet("margin-bottom: 4px;")

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_dados)

        self.layout.addWidget(QLabel("Nome da Empresa:"))
        self.layout.addWidget(self.nome_input)
        self.layout.addWidget(QLabel("Telefone:"))
        self.layout.addWidget(self.telefone_input)
        self.layout.addWidget(QLabel("CNPJ:"))
        self.layout.addWidget(self.cnpj_input)
        self.layout.addWidget(QLabel("Endereço:"))
        self.layout.addWidget(self.endereco_input)
        self.layout.addLayout(logo_layout)
        self.layout.addWidget(self.btn_salvar)

        self.setLayout(self.layout)

        self.logo_path = None
        self.carregar_existente()

    def carregar_existente(self):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM configuracao_empresa ORDER BY id DESC LIMIT 1")
        empresa = cur.fetchone()
        conn.close()

        if empresa:
            _, nome, endereco, cnpj, telefone = empresa
            self.nome_input.setText(nome)
            self.endereco_input.setText(endereco)
            self.cnpj_input.setText(cnpj)
            self.telefone_input.setText(telefone)
            if os.path.exists("logo.png"):
                self.logo_label.setPixmap(QPixmap("logo.png").scaledToHeight(128, Qt.SmoothTransformation))

    def selecionar_logo(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar Logo", "", "Imagens (*.png *.jpg *.jpeg *.bmp)")
        if caminho:
            self.logo_path = caminho
            self.logo_label.setPixmap(QPixmap(caminho).scaledToHeight(64, Qt.SmoothTransformation))

    def salvar_dados(self):
        nome = self.nome_input.text().strip()
        telefone = self.telefone_input.text().strip()
        cnpj = self.cnpj_input.text().strip()
        endereco = self.endereco_input.text().strip()

        if not all([nome, telefone, cnpj, endereco]):
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO configuracao_empresa (nome_empresa, endereco, cnpj, telefone) VALUES (?, ?, ?, ?)",
                    (nome, endereco, cnpj, telefone))
        conn.commit()
        conn.close()

        if self.logo_path:
            shutil.copyfile(self.logo_path, "logo.png")

        QMessageBox.information(self, "Sucesso", "Dados salvos com sucesso!")
        self.accept()
