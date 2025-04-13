import os
import sqlite3
import sys
from datetime import datetime

from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QCheckBox
)
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHeaderView

DB_FILE = "dados.sqlite"

# Conecta ou cria banco e tabelas
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS configuracao_empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_empresa TEXT,
    endereco TEXT,
    cnpj TEXT,
    telefone TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantidade INTEGER,
    descricao TEXT,
    destino TEXT,
    valor_unitario REAL,
    valor_total REAL,
    pago INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()


class MainWindow(QMainWindow):
    def apply_styles(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                padding: 6px 12px;
                background-color: #1976d2;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QTableWidget {
                border: 1px solid #ccc;
                background-color: white;
                alternate-background-color: #f5f5f5;
            }
        """)
        self.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #42a5f5;
                color: white;
            }
        """)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Controle de Itens")
        self.setMinimumSize(900, 600)

        self.apply_styles()

        self.widget = QWidget()
        self.layout = QVBoxLayout()

        self.logo = QLabel()
        self.logo.setFixedHeight(72)

        self.nome_empresa = QLabel("Nome da Empresa")
        self.endereco = QLabel("Endereço")
        self.dados_empresa = QLabel("CNPJ: - Tel: ")

        cabecalho_layout = QHBoxLayout()
        self.config_btn = QPushButton()
        self.config_btn.setIcon(QIcon("icons/settings_24dp.svg"))  # ícone local
        self.config_btn.setIconSize(QSize(24, 24))  # 👈 tamanho do ícone
        self.config_btn.setFixedSize(36, 36)  # tamanho do botão
        self.config_btn.clicked.connect(self.abrir_configuracao)

        info_empresa = QVBoxLayout()
        info_empresa.addWidget(self.nome_empresa)
        info_empresa.addWidget(self.endereco)
        info_empresa.addWidget(self.dados_empresa)

        cabecalho_layout.addWidget(self.logo)
        cabecalho_layout.addLayout(info_empresa)
        cabecalho_layout.addStretch()
        cabecalho_layout.addWidget(self.config_btn)

        self.layout.addLayout(cabecalho_layout)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separador)

        self.layout.addSpacing(20)

        botoes_layout = QHBoxLayout()
        for texto in ["Cadastrar Novo", "Editar", "Lancar Pago", "Excluir", "Ver Itens Pagos"]:
            btn = QPushButton(texto)

            if texto == "Cadastrar Novo":
                btn.clicked.connect(self.abrir_cadastro)
            elif texto == "Editar":
                btn.clicked.connect(self.abrir_edicao)

            botoes_layout.addWidget(btn)

        self.layout.addLayout(botoes_layout)

        self.tabela = QTableWidget()
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Qtd", "Descrição", "Destino", "Valor Unitário", "Valor Total", "Criado em"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.setColumnWidth(0, 40)  # Qtd
        self.tabela.setColumnWidth(1, 350)  # Descrição
        self.tabela.setColumnWidth(2, 150)  # Destino
        self.tabela.setColumnWidth(3, 100)  # Valor Unitário
        self.tabela.setColumnWidth(4, 100)  # Valor Total
        self.tabela.setColumnWidth(5, 80)  # Criado em
        self.layout.addWidget(self.tabela)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.carregar_dados_empresa()
        self.carregar_itens()

    def carregar_dados_empresa(self):
        cursor.execute("SELECT * FROM configuracao_empresa ORDER BY id DESC LIMIT 1")
        empresa = cursor.fetchone()
        if empresa:
            _, nome, endereco, cnpj, telefone = empresa
            self.nome_empresa.setText(nome)
            self.endereco.setText(endereco)
            self.dados_empresa.setText(f"CNPJ: {cnpj} - Tel: {telefone}")
            if os.path.exists("logo.png"):
                pixmap = QPixmap("logo.png").scaledToHeight(72)
                self.logo.setPixmap(pixmap)

    def carregar_itens(self):
        cursor.execute(
            "SELECT id, quantidade, descricao, destino, valor_unitario, valor_total, criado_em FROM itens WHERE pago = 0 ORDER BY criado_em DESC"
        )
        itens = cursor.fetchall()
        self.tabela.setRowCount(len(itens))
        for row, item in enumerate(itens):
            for col, valor in enumerate(item[1:]):  # pula o id (item[0])
                if col == 5:
                    try:
                        data = datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
                        texto = data.strftime("%d/%m/%Y")
                    except:
                        texto = str(valor)
                    cell = QTableWidgetItem(texto)
                    cell.setTextAlignment(Qt.AlignCenter)
                else:
                    if col in [3, 4]:  # Valor Unitário e Total
                        try:
                            numero = float(valor)
                            texto = f"R$ {numero:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
                        except ValueError:
                            texto = str(valor)
                        cell = QTableWidgetItem(texto)
                        cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    else:
                        cell = QTableWidgetItem(str(valor))
                        if col == 0:  # Quantidade
                            cell.setData(Qt.UserRole, item[0])  # salva id do item
                            cell.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(row, col, cell)
            # Checkbox centralizado na última coluna
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            layout = QHBoxLayout(checkbox_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget.setLayout(layout)
            self.tabela.setWordWrap(False)
            self.tabela.verticalHeader().setDefaultSectionSize(30)

    def abrir_configuracao(self):
        from empresa_config import EmpresaConfigDialog
        dialog = EmpresaConfigDialog(self)
        if dialog.exec():
            self.carregar_dados_empresa()

    def abrir_cadastro(self):
        from cadastro_item import CadastroItemDialog
        dialog = CadastroItemDialog(self)
        if dialog.exec():
            self.carregar_itens()

    def abrir_edicao(self):
        selected = self.tabela.currentRow()
        if selected < 0:
            return  # Nenhuma linha selecionada

        id_item = self.tabela.item(selected, 0).data(Qt.UserRole)

        quantidade = self.tabela.item(selected, 0).text()
        descricao = self.tabela.item(selected, 1).text()
        destino = self.tabela.item(selected, 2).text()
        valor_unitario = self.tabela.item(selected, 3).text().replace("R$ ", "").replace(".", "").replace(",", ".")

        from cadastro_item import CadastroItemDialog
        dialog = CadastroItemDialog(self, editar=True, dados={
            "id": id_item,
            "quantidade": quantidade,
            "descricao": descricao,
            "destino": destino,
            "valor_unitario": valor_unitario
        })

        if dialog.exec():
            self.carregar_itens()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open("style.qss").read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
