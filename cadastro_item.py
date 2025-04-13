from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget
from typing import Optional, Any
from models import Item
from database import insert_item, update_item


class CadastroItemDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, editar: bool = False, dados: Optional[dict[str, Any]] = None) -> None:
        super().__init__(parent)
        self.editar: bool = editar
        self.dados: Optional[dict[str, Any]] = dados
        self.setWindowTitle("Cadastrar Novo Item")
        self.setMinimumWidth(400)

        self.layout: QVBoxLayout = QVBoxLayout()

        self.quantidade_input = QLineEdit()
        if editar and dados:
            self.quantidade_input.setText(dados['quantidade'])
        self.quantidade_input.setValidator(QIntValidator(1, 9999))

        self.descricao_input = QLineEdit()
        if editar and dados:
            self.descricao_input.setText(dados['descricao'])

        self.destino_input = QLineEdit()
        if editar and dados:
            self.destino_input.setText(dados['destino'])

        self.valor_unitario_input: QLineEdit = QLineEdit()
        # Allow numbers with up to 2 decimal places
        self.valor_unitario_input.setValidator(QRegularExpressionValidator(r"^\d+(\,\d{2})?$"))
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
            self.valor_unitario_input.setText(f"{valor:,.2f}")

        # Limit to 10 million (including cents)
        self.valor_unitario_input.textChanged.connect(self.formatar_valor_unitario)
        self.valor_unitario_input.textChanged.connect(self.atualizar_valor_total)

        self.valor_total_input: QLineEdit = QLineEdit()
        self.valor_total_input.setReadOnly(True)
        self.valor_total_input.setPlaceholderText("Valor total calculado")

        self.layout.addWidget(QLabel("Quantidade:"))
        self.layout.addWidget(self.quantidade_input)  # type: ignore
        self.layout.addWidget(QLabel("Descrição:"))
        self.layout.addWidget(self.descricao_input)
        self.layout.addWidget(QLabel("Destino:"))
        self.layout.addWidget(self.destino_input)
        self.layout.addWidget(QLabel("Valor Unitário (ex: 10,50):"))
        self.layout.addWidget(self.valor_unitario_input)
        self.layout.addWidget(QLabel("Valor Total:"))
        self.layout.addWidget(self.valor_total_input)

        btn_layout = QHBoxLayout()
        self.btn_cancelar: QPushButton = QPushButton("Cancelar")
        self.btn_salvar: QPushButton = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_cancelar.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_salvar)

        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

        self.quantidade_input.textChanged.connect(self.atualizar_valor_total)

    def atualizar_valor_total(self) -> None:
        try:
            qtd: int = int(self.quantidade_input.text()) if self.quantidade_input.text() else 0
            valor_texto: str = self.valor_unitario_input.text().replace('R$', '').replace('.', '').replace(',', '.').strip()
            vu: float = float(valor_texto) if valor_texto else 0.0
            total: float = qtd * vu
            self.valor_total_input.setText(f"R$ {total:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
        except ValueError:
            self.valor_total_input.clear()

    def formatar_valor_unitario(self) -> None:
        texto: str = self.valor_unitario_input.text().replace('R$', '').replace('.', '').replace(',', '').strip()
        if texto.isdigit():
            valor: float = int(texto) / 100
            self.valor_unitario_input.blockSignals(True)
            self.valor_unitario_input.setText(f"R$ {valor:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
            self.valor_unitario_input.blockSignals(False)

    def salvar(self) -> None:
        editar = self.editar
        try:
            quantidade: int = int(self.quantidade_input.text())
            descricao: str = self.descricao_input.text().strip()
            destino: str = self.destino_input.text().strip()
            valor_texto: str = self.valor_unitario_input.text().replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_unitario: float = float(valor_texto)
            valor_total: float = quantidade * valor_unitario

            if not descricao or not destino:
                raise ValueError("Preencha todos os campos.")

            item: Item = Item(quantidade=quantidade, descricao=descricao, destino=destino, valor_unitario=valor_unitario, valor_total=valor_total)

            if editar and self.dados and 'id' in self.dados:  # Assuming 'id' is in self.dados when editing
                item.id = self.dados['id']  # Set the item ID for updating
                update_item(item)
            else:
                insert_item(item)

            QMessageBox.information(self, "Sucesso", "Item cadastrado com sucesso!")
            self.accept()
        except Exception as e:  # Catch any exception during database interaction
            QMessageBox.warning(
                self, "Erro", f"Erro ao salvar item: {e}"
            )  # Show error message
