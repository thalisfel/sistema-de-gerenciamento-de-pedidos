        // Verificar se o usuário está autenticado e é admin
        async function verificarAutenticacao() {
            try {
                const response = await fetch('/api/verificar-auth', {
                    credentials: 'include'
                });
                
                if (!response.ok) {
                    window.location.href = '/login.html';
                    return false;
                }

                const data = await response.json();
                console.log('Autenticação verificada:', data);

                if (data.tipo !== 'admin') {
                    mostrarAlerta('Acesso negado! Apenas administradores podem acessar esta página.', 'error');
                    setTimeout(() => {
                        window.location.href = '/pedidos.html';
                    }, 2000);
                    return false;
                }

                return true;
            } catch (error) {
                console.error('Erro ao verificar autenticação:', error);
                window.location.href = '/login.html';
                return false;
            }
        }

        // Mostrar alerta
        function mostrarAlerta(mensagem, tipo = 'success') {
            const alertContainer = document.getElementById('alertContainer');
            const alertClass = tipo === 'success' ? 'alert-success' : 'alert-error';
            
            alertContainer.innerHTML = `
                <div class="alert ${alertClass} show">
                    ${tipo === 'success' ? '✅' : '❌'} ${mensagem}
                </div>
            `;

            setTimeout(() => {
                alertContainer.innerHTML = '';
            }, 5000);
        }

        // Carregar lista de usuários
        async function carregarUsuarios() {
            try {
                const response = await fetch('/api/usuarios', {
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error('Erro ao carregar usuários');
                }

                const usuarios = await response.json();
                console.log('Usuários carregados:', usuarios);

                const listaDiv = document.getElementById('usuariosLista');

                if (usuarios.length === 0) {
                    listaDiv.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📭</div>
                            <p>Nenhum funcionário cadastrado ainda.</p>
                        </div>
                    `;
                    return;
                }

                listaDiv.innerHTML = usuarios.map(usuario => {
                    const icone = usuario.tipo === 'admin' ? '👑' : '👨‍💼';
                    const badgeClass = usuario.tipo === 'admin' ? 'badge-admin' : 'badge-gerente';
                    const tipoTexto = usuario.tipo === 'admin' ? 'Administrador' : 'Gerente';

                    return `
                        <div class="usuario-card">
                            <div class="usuario-info">
                                <div class="usuario-icon">${icone}</div>
                                <div class="usuario-detalhes">
                                    <h3>${usuario.usuario}</h3>
                                    <span class="badge ${badgeClass}">${tipoTexto}</span>
                                </div>
                            </div>
                            <button onclick="removerUsuario('${usuario.usuario}')" 
                                    class="btn btn-danger">
                                🗑️ Remover
                            </button>
                        </div>
                    `;
                }).join('');

            } catch (error) {
                console.error('Erro ao carregar usuários:', error);
                mostrarAlerta('Erro ao carregar lista de funcionários!', 'error');
            }
        }

        // Cadastrar novo usuário
        document.getElementById('formCadastro').addEventListener('submit', async (e) => {
            e.preventDefault();

            const usuario = document.getElementById('usuario').value.trim();
            const senha = document.getElementById('senha').value;
            const tipo = document.getElementById('tipo').value;

            try {
                const response = await fetch('/api/usuarios', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ usuario, senha, tipo })
                });

                const data = await response.json();

                if (response.ok) {
                    mostrarAlerta(`Funcionário ${usuario} cadastrado com sucesso!`, 'success');
                    document.getElementById('formCadastro').reset();
                    carregarUsuarios();
                } else {
                    mostrarAlerta(data.erro || 'Erro ao cadastrar funcionário!', 'error');
                }

            } catch (error) {
                console.error('Erro ao cadastrar:', error);
                mostrarAlerta('Erro ao cadastrar funcionário!', 'error');
            }
        });

        // Remover usuário
        async function removerUsuario(usuario) {
            if (!confirm(`Deseja realmente remover o usuário "${usuario}"?`)) {
                return;
            }

            try {
                const response = await fetch(`/api/usuarios/${usuario}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });

                const data = await response.json();

                if (response.ok) {
                    mostrarAlerta(`Usuário ${usuario} removido com sucesso!`, 'success');
                    carregarUsuarios();
                } else {
                    mostrarAlerta(data.erro || 'Erro ao remover usuário!', 'error');
                }

            } catch (error) {
                console.error('Erro ao remover:', error);
                mostrarAlerta('Erro ao remover usuário!', 'error');
            }
        }

        // Inicializar página
        (async function inicializar() {
            const autenticado = await verificarAutenticacao();
            if (autenticado) {
                carregarUsuarios();
            }
        })();