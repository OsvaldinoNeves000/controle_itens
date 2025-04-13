from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Company:
    nome_empresa: str = ""
    endereco: str = ""
    cnpj: str = ""
    telefone: str = ""
    id: Optional[int] = None  # Assuming ID can be None when creating a new company

@dataclass
class Item:
    quantidade: int = 0
    descricao: str = ""
    destino: str = ""
    valor_unitario: float = 0.0
    valor_total: float = 0.0
    id: Optional[int] = None  # Assuming ID can be None when creating a new item
    pago: int = 0  # Default value for payment status
    criado_em: Optional[str] = None  # Assuming creation date can be None initially