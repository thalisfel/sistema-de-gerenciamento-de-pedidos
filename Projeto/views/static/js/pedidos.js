const apiUrl = '';

// Formatar data e hora
function formatarDataHora(dataString) {
    if (!dataString) return 'Data não disponível';
    
    try {
        const data = new Date(dataString);
        
        // Formatar como DD/MM/YYYY HH:MM
        const dia = String(data.getDate()).padStart(2, '0');
        const mes = String(data.getMonth() + 1).padStart(2, '0');
        const ano = data.getFullYear();
        const horas = String(data.getHours()).padStart(2, '0');
        const minutos = String(data.getMinutes()).padStart(2, '0');
        
        return `${dia}/${mes}/${ano} ${horas}:${minutos}`;
    } catch (e) {
        return dataString;
    }
}

// Verificar autenticação ao carregar a página
async function verificarAuth() {
    try {
        const response = await fetch(`${apiUrl}/api/verificar-auth`, {
            credentials: 'include'
        });

        if (!response.ok) {
            window.location.href = '/login.html';
            return false;
        }

        const data = await response.json();
        document.getElementById('nome-usuario').textContent = data.usuario;

        // Mostrar botão de cadastro apenas para admins
        if (data.tipo === 'admin') {
            document.getElementById('btn-cadastro-func').style.display = 'inline-block';
            document.getElementById('btn-resetar-ids').style.display = 'inline-block';
        }

        return true;
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        window.location.href = '/login.html';
        return false;
    }
}

// Carregar pedidos
async function carregarPedidos() {
    try {
        console.log('🔄 Carregando pedidos...');
        const response = await fetch(`${apiUrl}/api/pedidos`, {
            credentials: 'include'
        });

        console.log('📡 Status da resposta:', response.status);

        if (!response.ok) {
            console.log('❌ Não autenticado, redirecionando...');
            window.location.href = '/login.html';
            return;
        }

        const pedidos = await response.json();
        console.log('📦 Pedidos recebidos:', pedidos);
        console.log('📊 Total de pedidos:', pedidos.length);

        exibirPedidos(pedidos);
        atualizarEstatisticas(pedidos);
    } catch (error) {
        console.error('❌ Erro ao carregar pedidos:', error);
    }
}

// Exibir pedidos
function exibirPedidos(pedidos) {
    console.log('🎨 Exibindo pedidos na interface...');
    const lista = document.getElementById('lista-pedidos');
    const countAtivos = document.getElementById('count-ativos');

    if (!lista) {
        console.error('❌ Elemento lista-pedidos não encontrado!');
        return;
    }

    // Atualizar contador
    if (countAtivos) {
        countAtivos.textContent = pedidos.length;
    }

    if (pedidos.length === 0) {
        console.log('📭 Nenhum pedido para exibir');
        lista.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <h3>Nenhum pedido ativo</h3>
                <p>Os novos pedidos aparecerão aqui</p>
            </div>
        `;
        return;
    }

    console.log(`✅ Exibindo ${pedidos.length} pedido(s)`);
    lista.innerHTML = pedidos.map(pedido => `
        <div class="pedido-card">
            <div class="pedido-header">
                <div>
                    <span class="pedido-id">Pedido #${pedido.id}</span>
                    <span class="status-badge status-${pedido.status.toLowerCase()}">${pedido.status}</span>
                </div>
                <div class="pedido-data">📅 ${formatarDataHora(pedido.data_pedido)}</div>
            </div>

            <div class="pedido-itens">
                <strong>Itens do Pedido:</strong>
                ${pedido.itens.map(item => {
                    const quantidade = item.quantidade || 1;
                    const preco = parseFloat(item.preco) || 0;
                    const subtotal = preco * quantidade;
                    return `
                    <div class="pedido-item">
                        • ${item.nome} ${quantidade > 1 ? `(x${quantidade})` : ''} - R$ ${subtotal.toFixed(2)}
                    </div>`;
                }).join('')}
            </div>

            <div class="pedido-total">
                💰 Total: R$ ${pedido.total.toFixed(2)}
            </div>

            <div class="pedido-acoes">
                ${pedido.status === 'Pendente' ? `
                    <button class="btn-status btn-preparar" onclick="atualizarStatus(${pedido.id}, 'Preparando')">
                        👨‍🍳 Preparar
                    </button>
                    <button class="btn-status btn-cancelar" onclick="cancelarPedido(${pedido.id})">
                        ❌ Cancelar
                    </button>
                ` : ''}
                ${pedido.status === 'Preparando' ? `
                    <button class="btn-status btn-pronto" onclick="atualizarStatus(${pedido.id}, 'Pronto')">
                        ✅ Marcar como Pronto
                    </button>
                ` : ''}
                ${pedido.status === 'Pronto' ? `
                    <button class="btn-status btn-entregar" onclick="atualizarStatus(${pedido.id}, 'Entregue')">
                        🚚 Marcar como Entregue
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Atualizar estatísticas
function atualizarEstatisticas(pedidos) {
    document.getElementById('total-pedidos').textContent = pedidos.length;

    const pendentes = pedidos.filter(p => p.status === 'Pendente').length;
    document.getElementById('pedidos-pendentes').textContent = pendentes;

    const receitaTotal = pedidos.reduce((sum, p) => sum + p.total, 0);
    document.getElementById('receita-total').textContent = `R$ ${receitaTotal.toFixed(2)}`;
}

// Atualizar status do pedido
async function atualizarStatus(id, novoStatus) {
    try {
        const response = await fetch(`${apiUrl}/api/pedidos/${id}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ status: novoStatus })
        });

        if (response.ok) {
            alert(`✅ Status atualizado para: ${novoStatus}`);
            carregarPedidos();
            carregarHistorico(); // Atualizar histórico também
        }
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
        alert('❌ Erro ao atualizar status!');
    }
}

// Cancelar pedido (remover permanentemente)
async function cancelarPedido(id) {
    if (!confirm('⚠️ Tem certeza que deseja REMOVER este pedido?\n\nEsta ação não pode ser desfeita!')) {
        return;
    }

    try {
        console.log(`🗑️ Removendo pedido #${id}...`);
        const response = await fetch(`${apiUrl}/api/pedidos/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            alert('✅ ' + data.mensagem);
            carregarPedidos();
        } else {
            alert('❌ ' + data.erro);
        }
    } catch (error) {
        console.error('Erro ao remover pedido:', error);
        alert('❌ Erro ao remover pedido!');
    }
}

// Carregar histórico de pedidos entregues
async function carregarHistorico() {
    try {
        console.log('📜 Carregando histórico...');
        const response = await fetch(`${apiUrl}/api/pedidos/historico`, {
            credentials: 'include'
        });

        if (!response.ok) {
            console.error('Erro ao carregar histórico');
            return;
        }

        const historico = await response.json();
        console.log('📊 Histórico recebido:', historico.length, 'pedidos');

        exibirHistorico(historico);
    } catch (error) {
        console.error('❌ Erro ao carregar histórico:', error);
    }
}

// Exibir histórico
function exibirHistorico(historico) {
    const lista = document.getElementById('lista-historico');
    const countElement = document.getElementById('count-historico');

    if (!lista) {
        console.error('❌ Elemento lista-historico não encontrado!');
        return;
    }

    // Atualizar contador
    countElement.textContent = historico.length;

    if (historico.length === 0) {
        lista.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <p>Nenhum pedido entregue ainda</p>
            </div>
        `;
        return;
    }

    // Exibir apenas os últimos 10 pedidos
    const historicoRecente = historico.slice(0, 10);

    lista.innerHTML = historicoRecente.map(pedido => {
        const itensHtml = pedido.itens.map(item => {
            const quantidade = item.quantidade || 1;
            const preco = parseFloat(item.preco) || 0;
            const subtotal = preco * quantidade;

            return `<div style="padding: 5px 0; display: flex; justify-content: space-between;">
                <span>${item.nome} ${quantidade > 1 ? `(x${quantidade})` : ''}</span>
                <span>R$ ${subtotal.toFixed(2)}</span>
            </div>`;
        }).join('');

        return `
            <div class="historico-item">
                <div class="historico-header">
                    <div>
                        <span class="historico-id">Pedido #${pedido.pedido_id || pedido.id}</span>
                        <span class="badge-entregue">✓ Entregue</span>
                    </div>
                    <span class="historico-data">
                        📅 ${formatarDataHora(pedido.data_pedido)} 
                        → 🚚 ${formatarDataHora(pedido.data_entrega)}
                    </span>
                </div>
                <div style="margin: 10px 0; font-size: 0.9em;">
                    ${itensHtml}
                </div>
                <div class="historico-total">
                    💰 Total: R$ ${pedido.total.toFixed(2)}
                </div>
            </div>
        `;
    }).join('');
}

// Limpar histórico
async function limparHistorico() {
    if (!confirm('⚠️ Tem certeza que deseja LIMPAR TODO O HISTÓRICO?\n\nEsta ação não pode ser desfeita!')) {
        return;
    }

    try {
        console.log('🗑️ Limpando histórico...');
        const response = await fetch(`${apiUrl}/api/pedidos/historico`, {
            method: 'DELETE',
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            alert('✅ ' + data.mensagem);
            carregarHistorico();
        } else {
            alert('❌ ' + data.erro);
        }
    } catch (error) {
        console.error('Erro ao limpar histórico:', error);
        alert('❌ Erro ao limpar histórico!');
    }
}

// Resetar o sistema através dos contadores de IDs
async function resetarContadores() {
    if (!confirm('🔄 RESETAR SISTEMA?\n\n⚠️ ATENÇÃO: Esta ação irá:\n\n1️⃣ Deletar TODOS os pedidos ativos\n2️⃣ Limpar TODO o histórico\n3️⃣ Deletar TODOS os produtos\n\n❌ ESTA AÇÃO NÃO PODE SER DESFEITA!\n\nDeseja continuar?')) {
        return;
    }

    try {
        console.log('🔄 Resetando sistema...');
        const response = await fetch(`${apiUrl}/api/resetar-ids`, {
            method: 'POST',
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            alert('✅ ' + data.mensagem);
            // Recarregar páginas
            carregarPedidos();
            carregarHistorico();
        } else {
            alert('❌ ' + data.erro);
        }
    } catch (error) {
        console.error('Erro ao resetar sistema:', error);
        alert('❌ Erro ao resetar sistema!');
    }
}

// Logout
async function logout() {
    if (confirm('Deseja realmente sair?')) {
        try {
            await fetch(`${apiUrl}/api/logout`, {
                method: 'POST',
                credentials: 'include'
            });
            window.location.href = '/';
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
        }
    }
}

// Inicializar
(async () => {
    const autenticado = await verificarAuth();
    if (autenticado) {
        carregarPedidos();
        carregarHistorico();
        // Atualizar a cada 10 segundos
        setInterval(() => {
            carregarPedidos();
            carregarHistorico();
        }, 10000);
    }
})();