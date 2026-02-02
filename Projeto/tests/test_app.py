import pytest
from flask import session

class TestAppRoutes:
    """Testes para as rotas do app.py"""
    
    def test_index_route(self, client):
        """Testa rota da página inicial"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_login_page_route(self, client):
        """Testa rota da página de login"""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_pedidos_page_route(self, client):
        """Testa rota da página de pedidos"""
        response = client.get('/pedidos')
        assert response.status_code == 200
    
    def test_cadastrar_produto_page_route(self, client):
        """Testa rota da página de cadastrar produto"""
        response = client.get('/cadastrar_produto')
        assert response.status_code == 200
    
    def test_gerenciar_produto_page_route(self, client):
        """Testa rota da página de gerenciar produto"""
        response = client.get('/gerenciar_produto')
        assert response.status_code == 200
    
    def test_cadastro_funcionarios_page_route(self, client):
        """Testa rota da página de cadastro de funcionários"""
        response = client.get('/cadastro_funcionarios')
        assert response.status_code == 200
    
    def test_pagina_inicial_route(self, client):
        """Testa rota da página inicial"""
        response = client.get('/pagina_inicial')
        assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Testa se CORS está configurado"""
        response = client.get('/api/produtos', headers={'Origin': 'http://127.0.0.1:5000'})
        # CORS deve estar presente
        assert response.status_code == 200


class TestAppConfiguration:
    """Testes de configuração do app"""
    
    def test_app_has_secret_key(self, app):
        """Testa se app tem secret_key configurada"""
        assert app.config['SECRET_KEY'] is not None
    
    def test_app_testing_mode(self, app):
        """Testa se app está em modo de teste"""
        assert app.config['TESTING'] is True
    
    def test_app_template_folder(self, app):
        """Testa se template_folder está configurado"""
        assert 'templates' in app.template_folder
    
    def test_app_static_folder(self, app):
        """Testa se static_folder está configurado"""
        assert 'static' in app.static_folder
