-- =============================================
-- MODELO FÍSICO DO BANCO DE DADOS
-- Sistema de Gerenciamento de Restaurante
-- Versão: 1.0
-- Data: 05/01/2026
-- =============================================

-- =============================================
-- TABELA: usuarios
-- Descrição: Armazena informações dos usuários do sistema
-- =============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'gerente')),
    data_cadastro TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    ativo BOOLEAN DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_usuario ON usuarios(usuario);
CREATE INDEX IF NOT EXISTS idx_tipo ON usuarios(tipo);
CREATE INDEX IF NOT EXISTS idx_ativo ON usuarios(ativo);

-- =============================================
-- TABELA: produtos
-- Descrição: Catálogo de produtos do restaurante
-- =============================================
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL CHECK(preco >= 0),
    ativo BOOLEAN DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_produto_nome ON produtos(nome);
CREATE INDEX IF NOT EXISTS idx_produto_ativo ON produtos(ativo);
CREATE INDEX IF NOT EXISTS idx_produto_preco ON produtos(preco);

-- =============================================
-- TABELA: pedidos
-- Descrição: Pedidos em andamento
-- =============================================
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    itens_json TEXT NOT NULL,
    total REAL NOT NULL CHECK(total >= 0),
    status TEXT NOT NULL DEFAULT 'Pendente'
        CHECK(status IN ('Pendente', 'Preparando', 'Pronto', 'Entregue')),
    data_pedido TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    data_entrega TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_pedido_status ON pedidos(status);
CREATE INDEX IF NOT EXISTS idx_pedido_data ON pedidos(data_pedido);
CREATE INDEX IF NOT EXISTS idx_pedido_total ON pedidos(total);

-- =============================================
-- TABELA: historico_pedidos
-- Descrição: Histórico de pedidos entregues
-- =============================================
CREATE TABLE IF NOT EXISTS historico_pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    itens_json TEXT NOT NULL,
    total REAL NOT NULL CHECK(total >= 0),
    status TEXT NOT NULL,
    data_pedido TIMESTAMP NOT NULL,
    data_entrega TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_historico_data_pedido ON historico_pedidos(data_pedido);
CREATE INDEX IF NOT EXISTS idx_historico_data_entrega ON historico_pedidos(data_entrega);
CREATE INDEX IF NOT EXISTS idx_historico_total ON historico_pedidos(total);

-- =============================================
-- TABELA: lucros_diarios
-- Descrição: Resumo financeiro diário
-- =============================================
CREATE TABLE IF NOT EXISTS lucros_diarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE UNIQUE NOT NULL,
    total_pedidos INTEGER DEFAULT 0 CHECK(total_pedidos >= 0),
    receita_total REAL DEFAULT 0 CHECK(receita_total >= 0),
    ticket_medio REAL DEFAULT 0 CHECK(ticket_medio >= 0),
    atualizado_em TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_lucros_data ON lucros_diarios(data);
CREATE INDEX IF NOT EXISTS idx_lucros_receita ON lucros_diarios(receita_total);

-- =============================================
-- VIEWS ÚTEIS
-- =============================================

-- View: Resumo de vendas por produto
CREATE VIEW IF NOT EXISTS vendas_por_produto AS
SELECT
    p.id,
    p.nome,
    p.preco,
    COUNT(*) as total_vendido,
    SUM(p.preco) as receita_gerada
FROM produtos p
JOIN (
    SELECT
        json_extract(value, '$.id') as produto_id,
        CAST(json_extract(value, '$.quantidade') AS INTEGER) as quantidade
    FROM historico_pedidos hp,
    json_each(hp.itens_json)
) vendas ON p.id = vendas.produto_id
GROUP BY p.id, p.nome, p.preco;

-- View: Estatísticas gerais
CREATE VIEW IF NOT EXISTS estatisticas_gerais AS
SELECT
    (SELECT COUNT(*) FROM usuarios WHERE ativo = 1) as total_usuarios,
    (SELECT COUNT(*) FROM produtos WHERE ativo = 1) as total_produtos,
    (SELECT COUNT(*) FROM pedidos WHERE status != 'Entregue') as pedidos_pendentes,
    (SELECT COUNT(*) FROM historico_pedidos) as pedidos_entregues,
    (SELECT COALESCE(SUM(receita_total), 0) FROM lucros_diarios
     WHERE data >= date('now', '-30 days')) as receita_30_dias;

-- =============================================
-- TRIGGERS PARA MANUTENÇÃO AUTOMÁTICA
-- =============================================

-- Trigger: Atualizar lucros diários quando pedido é entregue
CREATE TRIGGER IF NOT EXISTS atualizar_lucros_diarios
AFTER INSERT ON historico_pedidos
BEGIN
    INSERT OR REPLACE INTO lucros_diarios (data, total_pedidos, receita_total, ticket_medio, atualizado_em)
    SELECT
        DATE(NEW.data_entrega),
        COUNT(*) + COALESCE(ld.total_pedidos, 0),
        NEW.total + COALESCE(ld.receita_total, 0),
        (NEW.total + COALESCE(ld.receita_total, 0)) / (COUNT(*) + COALESCE(ld.total_pedidos, 0)),
        CURRENT_TIMESTAMP
    FROM historico_pedidos hp
    LEFT JOIN lucros_diarios ld ON ld.data = DATE(NEW.data_entrega)
    WHERE DATE(hp.data_entrega) = DATE(NEW.data_entrega);
END;

-- =============================================
-- DADOS INICIAIS (SEED)
-- =============================================

-- Usuário admin padrão
INSERT OR IGNORE INTO usuarios (usuario, senha_hash, tipo)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8GdqGzKj6', 'admin');

-- Produtos padrão
INSERT OR IGNORE INTO produtos (nome, descricao, preco) VALUES
('Pizza Margherita', 'Pizza com queijo e tomate', 25.00),
('Hambúrguer', 'Hambúrguer com batata frita', 15.00);