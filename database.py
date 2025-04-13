import sqlite3
from typing import Optional, List
from models import Company, Item

DB_FILE = "dados.sqlite"

def connect_db() -> sqlite3.Connection:
    """Connects to the SQLite database and returns a connection object."""
    try:
        conn: sqlite3.Connection = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

def create_tables():
    """Creates the necessary tables if they don't exist."""
    conn = connect_db()
    cursor: sqlite3.Cursor = conn.cursor()
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
    conn.close()

def get_company_config() -> Optional[Company]:
    """Retrieves the latest company configuration and returns a Company object."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM configuracao_empresa ORDER BY id DESC LIMIT 1")
        company_info = cursor.fetchone()
        conn.close()

        if company_info:
            id, nome_empresa, endereco, cnpj, telefone = company_info
            return Company(id=id, nome_empresa=nome_empresa, endereco=endereco, cnpj=cnpj, telefone=telefone)
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise



def insert_company_info(nome: str, endereco: str, cnpj: str, telefone: str) -> None:
    """Inserts new company configuration data."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO configuracao_empresa (nome_empresa, endereco, cnpj, telefone)
        VALUES (?, ?, ?, ?)""", (nome, endereco, cnpj, telefone))
    conn.commit()
    conn.close()


# Corrected get_items function

def get_items(paid: int = 0) -> List[Item]:
    """Retrieves items based on their payment status."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, quantidade, descricao, destino, valor_unitario, valor_total, criado_em 
        FROM itens 
        WHERE pago = ? 
        ORDER BY criado_em DESC""", (paid,))
    items = cursor.fetchall()
    conn.close()

    return [
        Item(
            id=row[0],
            quantidade=row[1],
            descricao=row[2],
            destino=row[3],
            valor_unitario=row[4],
            valor_total=row[5],
            criado_em=row[6],
        )
        for row in items
    ]

def insert_item(item: Item) -> None:
    """Inserts a new item into the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO itens (quantidade, descricao, destino, valor_unitario, valor_total, pago)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (item.quantidade, item.descricao, item.destino, item.valor_unitario, item.valor_total, item.pago))
    conn.commit()
    conn.close()

def update_item(item: Item) -> None:
    """Updates an existing item in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE itens
        SET quantidade=?, descricao=?, destino=?, valor_unitario=?, valor_total=?
        WHERE id=?""",
        (item.quantidade, item.descricao, item.destino, item.valor_unitario, item.valor_total, item.id))
    conn.commit()
    conn.close()

def init_db() -> None:
    create_tables()