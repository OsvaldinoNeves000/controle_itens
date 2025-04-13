from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator
import sqlite3

DB_FILE = "dados.sqlite"


class CadastroItemDialog(QDialog):
    def __init__(self, parent=None, editar=False, dados=None):
        super().__init__(parent)
        self.editar = editar
        self.dados = dados
        self.setWindowTitle("Cadastrar Novo Item")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout()

        self.quantidade_input = QLineEdit()
        if editar and dados:
            self.quantidade_input.setText(dados['quantidade'])
        self.quantidade_input.setValidator(QIntValidator(0, 9999))

        self.descricao_input = QLineEdit()
        if editar and dados:
            self.descricao_input.setText(dados['descricao'])
        self.destino_input = QLineEdit()
        if editar and dados:
            self.destino_input.setText(dados['destino'])

        self.valor_unitario_input = QLineEdit()
        if editar and dados:
            valor_texto = dados['valor_unitario']
            valor_sanitizado = (
                valor_texto.replace("R$", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            try:
                valor = float(valor_sanitizado)
            except ValueError:
                valor = 0.0
            self.valor_unitario_input.blockSignals(True)
            self.valor_unitario_input.setText(f"R$ {valor:,.2f}".replace(".", "X").replace(",", ".").replace("X", ","))
            self.valor_unitario_input.blockSignals(False)

        self.valor_unitario_input.setValidator(QDoubleValidator(0.0, 100000.0, 2))
        self.valor_unitario_input.textChanged.connect(self.formatar_valor_unitario)
        self.valor_unitario_input.textChanged.connect(self.atualizar_valor_total)

        self.valor_total_input = QLineEdit()
        self.valor_total_input.setReadOnly(True)
        self.valor_total_input.setPlaceholderText("Valor total calculado")

        self.layout.addWidget(QLabel("Quantidade:"))
        self.layout.addWidget(self.quantidade_input)
        self.layout.addWidget(QLabel("Descrição:"))
        self.layout.addWidget(self.descricao_input)
        self.layout.addWidget(QLabel("Destino:"))
        self.layout.addWidget(self.destino_input)
        self.layout.addWidget(QLabel("Valor Unitário (ex: 10.50):"))
        self.layout.addWidget(self.valor_unitario_input)
        self.layout.addWidget(QLabel("Valor Total:"))
        self.layout.addWidget(self.valor_total_input)

        btn_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_cancelar.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_salvar)

        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

        self.quantidade_input.textChanged.connect(self.atualizar_valor_total)

    def atualizar_valor_total(self):
        try:
            qtd = int(self.quantidade_input.text()) if self.quantidade_input.text() else 0
            valor_texto = self.valor_unitario_input.text().replace('R$', '').replace('.', '').replace(',', '.').strip()
            vu = float(valor_texto) if valor_texto else 0.0
            total = qtd * vu
            self.valor_total_input.setText(f"R$ {total:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
        except ValueError:
            self.valor_total_input.clear()

    def formatar_valor_unitario(self):
        texto = self.valor_unitario_input.text().replace('R$', '').replace('.', '').replace(',', '').strip()
        if texto.isdigit():
            valor = int(texto) / 100
            self.valor_unitario_input.blockSignals(True)
            self.valor_unitario_input.setText(f"R$ {valor:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
            self.valor_unitario_input.blockSignals(False)

    def salvar(self):
        editar = self.editar
        try:
            quantidade = int(self.quantidade_input.text())
            descricao = self.descricao_input.text().strip()
            destino = self.destino_input.text().strip()
            valor_texto = self.valor_unitario_input.text().replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_unitario = float(valor_texto)
            valor_total = quantidade * valor_unitario

            if not descricao or not destino:
                raise ValueError("Preencha todos os campos.")

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            if editar and self.dados and 'id' in self.dados:
                id_item = self.dados['id']
                cur.execute("""
                    UPDATE itens SET quantidade=?, descricao=?, destino=?, valor_unitario=?, valor_total=?
                    WHERE id=?
                """, (quantidade, descricao, destino, valor_unitario, valor_total, id_item))
            else:
                cur.execute("""
                    INSERT INTO itens (quantidade, descricao, destino, valor_unitario, valor_total, pago)
                    VALUES (?, ?, ?, ?, ?, 0)
                """, (quantidade, descricao, destino, valor_unitario, valor_total))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sucesso", "Item cadastrado com sucesso!")
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))
