import pytest
import os
import sys
import tempfile
import shutil

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from models.database_manager import DatabaseManager

@pytest.fixture
def app():
    """Cria instância do Flask app para testes"""
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    return flask_app

@pytest.fixture
def client(app):
    """Cria cliente de teste do Flask"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Cria runner CLI para testes"""
    return app.test_cli_runner()

@pytest.fixture
def temp_db():
    """Cria um banco de dados temporário para testes"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    # Cria o schema
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_schema.sql')
    db = DatabaseManager(db_path=db_path)
    
    yield db
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def authenticated_client(client):
    """Cliente autenticado como admin"""
    # Primeiro, garantir que existe um admin
    with client.session_transaction() as session:
        session['autenticado'] = True
        session['usuario'] = 'admin'
        session['tipo'] = 'admin'
    
    return client

@pytest.fixture
def authenticated_gerente(client):
    """Cliente autenticado como gerente"""
    with client.session_transaction() as session:
        session['autenticado'] = True
        session['usuario'] = 'gerente1'
        session['tipo'] = 'gerente'
    
    return client
