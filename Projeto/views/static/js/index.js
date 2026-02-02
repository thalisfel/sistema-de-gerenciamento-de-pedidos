const apiUrl = '/api/produtos';
let pedido = [];  // Lista de itens selecionados

// Navegação entre seções
function mostrarSecao(secao) {
    // Esconde o lobby
    document.getElementById('lobby').style.display = 'none';

    // Esconde todas as seções
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));

    // Mostra a seção selecionada
    document.getElementById(`secao-${secao}`).classList.add('active');

    // Carrega dados específicos da seção
    if (secao === 'cardapio') {
        carregarCardapio();
    } else if (secao === 'pedido') {
        carregarProdutosPedido();
    }
}

function voltarLobby() {
    // Esconde todas as seções
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));

    // Mostra o lobby
    document.getElementById('lobby').style.display = 'grid';
}

// Função para carregar cardápio (visualização simples)
async function carregarCardapio() {
    const response = await fetch(apiUrl, {
        credentials: 'include'
    });
    const produtos = await response.json();
    const lista = document.getElementById('lista-cardapio');
    lista.innerHTML = '';

    if (produtos.length === 0) {
        lista.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">Nenhum produto cadastrado ainda.</p>';
        return;
    }

    produtos.forEach(produto => {
        const div = document.createElement('div');
        div.className = 'produto';
        div.innerHTML = `
            <h3>${produto.nome}</h3>
            <p>${produto.descricao}</p>
            <p style="font-size: 1.3em; color: #28a745; font-weight: bold;">R$ ${produto.preco.toFixed(2)}</p>
        `;
        lista.appendChild(div);
    });
}

// Função para carregar produtos na seção de pedidos
async function carregarProdutosPedido() {
    const response = await fetch(apiUrl, {
        credentials: 'include'
    });
    const produtos = await response.json();
    const lista = document.getElementById('lista-produtos-pedido');
    lista.innerHTML = '';

    if (produtos.length === 0) {
        lista.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">Nenhum produto disponível para pedido.</p>';
        return;
    }

    produtos.forEach(produto => {
        const div = document.createElement('div');
        div.className = 'produto';
        div.innerHTML = `
            <h3>${produto.nome}</h3>
            <p>${produto.descricao}</p>
            <p style="font-size: 1.2em; color: #28a745; font-weight: bold;">R$ ${produto.preco.toFixed(2)}</p>
            <button class="btn-success" onclick="adicionarAoPedido(${produto.id}, '${produto.nome.replace(/'/g, "\\'")}', ${produto.preco})">
                ➕ Adicionar ao Pedido
            </button>
        `;
        lista.appendChild(div);
    });
}

// Função para adicionar ao pedido
function adicionarAoPedido(id, nome, preco) {
    pedido.push({ id, nome, preco });
    atualizarPedido();
    alert(`✅ "${nome}" adicionado ao pedido!`);
}

// Função para atualizar exibição do pedido
function atualizarPedido() {
    const itensDiv = document.getElementById('itens-pedido');
    const totalSpan = document.getElementById('total');

    if (pedido.length === 0) {
        itensDiv.innerHTML = '<p style="color: #999;">Nenhum item selecionado.</p>';
        totalSpan.textContent = '0.00';
        return;
    }

    itensDiv.innerHTML = pedido.map((item, index) =>
        `<div style="margin: 10px 0; padding: 5px; background: white; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
            <span><strong>${item.nome}</strong> - R$ ${item.preco.toFixed(2)}</span>
            <button class="btn-danger" onclick="removerDoPedido(${index})">🗑️ Remover</button>
        </div>`
    ).join('');

    const total = pedido.reduce((sum, item) => sum + item.preco, 0);
    totalSpan.textContent = total.toFixed(2);
}

// Função para remover do pedido
function removerDoPedido(index) {
    const item = pedido[index];
    
    if (confirm(`⚠️ Remover item do pedido?\n\n"${item.nome}" - R$ ${item.preco.toFixed(2)}\n\nDeseja confirmar a remoção?`)) {
        pedido.splice(index, 1);
        atualizarPedido();
        alert(`✅ "${item.nome}" removido do pedido!`);
    }
}

// Função para limpar pedido
function limparPedido() {
    if (pedido.length === 0) {
        alert('O pedido já está vazio!');
        return;
    }

    if (confirm('Deseja limpar todo o pedido?')) {
        pedido = [];
        atualizarPedido();
        alert('🗑️ Pedido limpo!');
    }
}

// Função para finalizar pedido
async function finalizarPedido() {
    if (pedido.length === 0) {
        alert('⚠️ Adicione itens ao pedido antes de finalizar!');
        return;
    }

    const total = pedido.reduce((sum, item) => sum + item.preco, 0);
    const itens = pedido.map(item => `- ${item.nome}: R$ ${item.preco.toFixed(2)}`).join('\n');

    if (confirm(`Confirmar pedido?\n\n${itens}\n\nTotal: R$ ${total.toFixed(2)}`)) {
        try {
            // Enviar pedido para o backend
            const response = await fetch('/api/pedidos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    itens: pedido,
                    total: total
                })
            });

            if (response.ok) {
                alert('✅ Pedido finalizado com sucesso!\n\nTotal: R$ ' + total.toFixed(2) + '\n\n📋 O pedido foi enviado para a área de gerenciamento.');
                pedido = [];
                atualizarPedido();
            } else {
                alert('❌ Erro ao finalizar pedido!');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('❌ Erro ao conectar com o servidor!');
        }
    }
}

// Função para abrir modal de edição
function abrirModalEditar(produto) {
    // Esta função foi movida para pedidos.html
    alert('Esta funcionalidade agora está disponível na área de gerenciamento de pedidos.');
    window.location.href = '/login.html';
}