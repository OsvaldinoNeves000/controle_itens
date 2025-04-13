import os
import shutil
from models import Company
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QWidget
)

from database import get_company_config, update_company_config

class EmpresaConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(\"Configuração da Empresa\")
        self.setMinimumWidth(400)

        self.layout: QVBoxLayout = QVBoxLayout()

        # Layout horizontal para logo + botão lado a lado
        logo_layout: QHBoxLayout = QHBoxLayout()
        self.logo_label: QLabel = QLabel(\"Nenhuma logo carregada\")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedHeight(128)
        self.logo_label.setFixedWidth(128)

        self.btn_logo: QPushButton = QPushButton(\"Selecionar Logo\")

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

        self.logo_path: Optional[str] = None
        self.carregar_dados_existentes()

    def carregar_dados_existentes(self) -> None:
        try:
            empresa: Optional[Company] = get_company_config()
            if empresa:
                self.nome_input.setText(empresa.nome_empresa)
                self.endereco_input.setText(empresa.endereco)
                self.cnpj_input.setText(empresa.cnpj)
                self.telefone_input.setText(empresa.telefone)
                if os.path.exists("logo.png"):
                    pixmap = QPixmap("logo.png").scaledToHeight(128, Qt.SmoothTransformation)
                    self.logo_label.setPixmap(pixmap)
                    self.logo_label.setFixedSize(QSize(128, 128))
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar dados da empresa: {e}")

    def selecionar_logo(self) -> None:
        # Abre o diálogo para selecionar a imagem
        # _ é usado para descartar o segundo valor retornado, que indica o filtro selecionado
        # '': diretório inicial do diálogo (vazio para o diretório atual ou padrão)
        # \"Imagens...\" :  string que define os tipos de arquivos que podem ser selecionados.
        #       Neste caso, arquivos com extensões .png, .jpg, .jpeg e .bmp são permitidos.
        #       O uso de parênteses e asteriscos segue a sintaxe específica do Qt para filtros de arquivos.
        #       O nome que precede a lista de extensões (Imagens) é exibido para o usuário no diálogo.
        # getOpenFileName retorna uma tupla contendo o caminho do arquivo selecionado e o filtro usado
        #   (que descartamos com o uso de _).
        # Ex: ('/home/user/Documents/my_image.png', 'Images (*.png *.xpm *.jpg)')
        #       seria o retorno se o usuário selecionar 'my_image.png'.


        # Abre o diálogo para selecionar a imagem.
        # O segundo valor retornado (o filtro selecionado) é descartado usando _
        # '': diretório inicial (diretório atual ou padrão)
        # \"Imagens...\": string que define os tipos de arquivos que podem ser selecionados
        # getOpenFileName retorna uma tupla: (caminho do arquivo, filtro selecionado)
        # Ex: ('/home/user/Documents/my_image.png', 'Images (*.png *.xpm *.jpg)')
        # se o usuário selecionar 'my_image.png'.


        # Abre o diálogo para selecionar a imagem
        # _ é usado para descartar o segundo valor retornado, que indica o filtro selecionado
        # '': diretório inicial do diálogo (vazio para o diretório atual ou padrão)
        # \"Imagens...\" :  string que define os tipos de arquivos que podem ser selecionados.
        #       Neste caso, arquivos com extensões .png, .jpg, .jpeg e .bmp são permitidos.
        #       O uso de parênteses e asteriscos segue a sintaxe específica do Qt para filtros de arquivos.
        #       O nome que precede a lista de extensões (Imagens) é exibido para o usuário no diálogo.
        # getOpenFileName retorna uma tupla contendo o caminho do arquivo selecionado e o filtro usado
        #   (que descartamos com o uso de _).
        # Ex: ('/home/user/Documents/my_image.png', 'Images (*.png *.xpm *.jpg)')
        #       seria o retorno se o usuário selecionar 'my_image.png'.


        # Abre o diálogo para selecionar a imagem.
        # O segundo valor retornado (o filtro selecionado) é descartado usando _
        # '': diretório inicial (diretório atual ou padrão)
        # \"Imagens...\": string que define os tipos de arquivos que podem ser selecionados
        # getOpenFileName retorna uma tupla: (caminho do arquivo, filtro selecionado)
        # Ex: ('/home/user/Documents/my_image.png', 'Images (*.png *.xpm *.jpg)')
        # se o usuário selecionar 'my_image.png'.


        # Abre o diálogo para selecionar a imagem
        # _ é usado para descartar o segundo valor retornado, que indica o filtro selecionado
        # '': diretório inicial do diálogo (vazio para o diretório atual ou padrão)
        # \"Imagens...\" :  string que define os tipos de arquivos que podem ser selecionados.
        #       Neste caso, arquivos com extensões .png, .jpg, .jpeg e .bmp são permitidos.
        #       O uso de parênteses e asteriscos segue a sintaxe específica do Qt para filtros de arquivos.
        #       O nome que precede a lista de extensões (Imagens) é exibido para o usuário no diálogo.
        # getOpenFileName retorna uma tupla contendo o caminho do arquivo selecionado e o filtro usado
        #   (que descartamos com o uso de _).
        # Ex: ('/home/user/Documents/my_image.png', 'Images (*.png *.xpm *.jpg)')
        #       seria o retorno se o usuário selecionar 'my_image.png'.


        # Abre o diálogo para selecionar a imagem.
        # O segundo valor retornado (o filtro selecionado) é descartado usando _
        # '': diretório inicial (diretório atual ou padrão)
        # \"Imagens...\": string que define os tipos de arquivos que podem ser selecionados
        # getOpenFileName retorna uma tupla: (caminho do arquivo, filtro selecionado)
        # Ex: ('/home/user/Documents/my_image.png', 'Images (*.png *.xpm *.jpg)')
        # se o usuário selecionar 'my_image.png'.

        caminho: str, _ = QFileDialog.getOpenFileName(self, "Selecionar Logo", "", "Imagens (*.png *.jpg *.jpeg *.bmp)")
        if caminho:
            self.logo_path = caminho
            pixmap: QPixmap = QPixmap(caminho).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
            self.logo_label.setFixedSize(QSize(128, 128))

    def salvar_dados(self) -> None:
        nome = self.nome_input.text().strip()
        telefone = self.telefone_input.text().strip()
        cnpj = self.cnpj_input.text().strip()
        endereco = self.endereco_input.text().strip()

        if not all([nome, telefone, cnpj, endereco]):
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        try:
            empresa: Company = Company(nome_empresa=nome, endereco=endereco, cnpj=cnpj, telefone=telefone)
            update_company_config(empresa)
            if self.logo_path:
                shutil.copyfile(self.logo_path, "logo.png")
            QMessageBox.information(self, "Sucesso", "Dados salvos com sucesso!")
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar dados da empresa: {e}")

