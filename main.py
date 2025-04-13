import os
import sys
import sqlite3
import sqlite3
from datetime import datetime

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QCheckBox, QFrame, QHeaderView, QMessageBox
)

from database import init_db, get_company_config, get_items
from models import Company, Item

DB_FILE = "items.db"



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
    def apply_styles(self) -> None:
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

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sistema de Controle de Itens")
        self.setMinimumSize(900, 600)

        self.apply_styles()

        self.widget = QWidget()
        self.layout: QVBoxLayout = QVBoxLayout()

        self.logo: QLabel = QLabel()
        self.logo.setFixedHeight(72)

        self.nome_empresa: QLabel = QLabel("Nome da Empresa")
        self.endereco: QLabel = QLabel("Endereço")
        self.dados_empresa: QLabel = QLabel("CNPJ: - Tel: ")

        cabecalho_layout: QHBoxLayout = QHBoxLayout()
        self.config_btn: QPushButton = QPushButton()
        self.config_btn.setIcon(QIcon("icons/settings_24dp.svg"))
        self.config_btn.setIconSize(QSize(24, 24))
        self.config_btn.setFixedSize(36, 36)  # tamanho do botão
        self.config_btn.clicked.connect(self.abrir_configuracao)

        info_empresa: QVBoxLayout = QVBoxLayout()
        info_empresa.addWidget(self.nome_empresa)
        info_empresa.addWidget(self.endereco)
        info_empresa.addWidget(self.dados_empresa)

        cabecalho_layout.addWidget(self.logo)
        cabecalho_layout.addLayout(info_empresa)
        cabecalho_layout.addStretch()
        cabecalho_layout.addWidget(self.config_btn)

        self.layout.addLayout(cabecalho_layout)  # Use self.layout

        separador: QFrame = QFrame()
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

        self.layout.addLayout(botoes_layout)  # Use self.layout

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

        try:
            init_db()
            self.carregar_dados_empresa()
            self.carregar_itens()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erro", f"Erro de banco de dados: {e}. O aplicativo não pode iniciar.")

    def carregar_dados_empresa(self) -> None:
        empresa: Optional[Company] = get_company_config()
        if empresa:
            self.nome_empresa.setText(empresa.nome_empresa)
            self.endereco.setText(empresa.endereco)
            self.dados_empresa.setText(f"CNPJ: {empresa.cnpj} - Tel: {empresa.telefone}")

            if os.path.exists("logo.png"):
                pixmap = QPixmap("logo.png").scaledToHeight(72)
                self.logo.setPixmap(pixmap)
    
    def carregar_itens(self):
        itens = get_items()
        self.tabela.setRowCount(len(itens))
        for row, item in enumerate(itens):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(item.quantidade)))  # Qtd
            self.tabela.setItem(row, 1, QTableWidgetItem(item.descricao))
            self.tabela.setItem(row, 2, QTableWidgetItem(item.destino))

            # Format numeric values with currency and decimal separators
            valor_unitario_formatted = f"R$ {item.valor_unitario:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            valor_total_formatted = f"R$ {item.valor_total:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')

            self.tabela.setItem(row, 3, QTableWidgetItem(valor_unitario_formatted))
            self.tabela.setItem(row, 4, QTableWidgetItem(valor_total_formatted))

            # Format the date, handling potential None values
            created_at = datetime.strptime(item.criado_em, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") if item.criado_em else ""
            self.tabela.setItem(row, 5, QTableWidgetItem(created_at))           








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
