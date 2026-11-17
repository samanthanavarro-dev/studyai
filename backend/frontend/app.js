class StudyAI {
    constructor() {
        this.token = localStorage.getItem('studyai_token');
        this.currentQuiz = null;
        this.currentUser = null;
        this.init();
    }

    init() {
        this.bindEvents();
        if (this.token) {
            this.showDashboard();
            document.getElementById('userName').textContent = 'Usuário logado!';
        }
    }

    bindEvents() {
        // ===== LOGIN/REGISTER =====
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });

        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.register();
        });

        // ===== TOGGLE SCREENS =====
        document.getElementById('showRegister').onclick = (e) => {
            e.preventDefault();
            this.showRegister();
        };
        document.getElementById('showLogin').onclick = (e) => {
            e.preventDefault();
            this.showLogin();
        };

        // ===== DASHBOARD =====
        document.getElementById('materiaForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addMateria();
        });

        document.getElementById('logout').onclick = () => this.logout();
        document.getElementById('verificarRespostas').onclick = () => this.verificarQuiz();
        document.getElementById('gerarPDF').onclick = () => this.gerarPDF();
    }

    // ===== API HELPER =====
    async apiCall(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && {'Authorization': `Bearer ${this.token}`})
            },
            ...options
        };

        try {
            const response = await fetch(`${endpoint}`, config);
            if (!response.ok) {
                throw new Error(`Erro ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // ===== AUTENTICAÇÃO =====
    async login() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch('/token', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Email ou senha inválidos');
            }

            const data = await response.json();
            this.token = data.access_token;
            localStorage.setItem('studyai_token', this.token);
            document.getElementById('userName').textContent = 'Usuário logado!';
            this.showDashboard();
        } catch (error) {
            alert('❌ Erro no login: ' + error.message);
        }
    }

    async register() {
        const nome = document.getElementById('nome').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;

        try {
            const data = await this.apiCall('/register', {
                method: 'POST',
                body: JSON.stringify({nome, email, password})
            });

            this.token = data.access_token;
            localStorage.setItem('studyai_token', this.token);
            document.getElementById('userName').textContent = `Olá, ${nome}!`;
            this.showDashboard();
        } catch (error) {
            alert('❌ Erro no cadastro: Email já existe?');
        }
    }

    logout() {
        this.token = null;
        this.currentQuiz = null;
        localStorage.removeItem('studyai_token');
        document.getElementById('quizSection').classList.add('hidden');
        this.showLogin();
    }

    // ===== NAVEGAÇÃO =====
    showLogin() {
        document.getElementById('loginScreen').classList.add('active');
        document.getElementById('registerScreen').classList.remove('active');
        document.getElementById('dashboard').classList.remove('active');
    }

    showRegister() {
        document.getElementById('registerScreen').classList.add('active');
        document.getElementById('loginScreen').classList.remove('active');
        document.getElementById('dashboard').classList.remove('active');
    }

    showDashboard() {
        document.getElementById('loginScreen').classList.remove('active');
        document.getElementById('registerScreen').classList.remove('active');
        document.getElementById('dashboard').classList.add('active');
        this.loadMaterias();
    }

    // ===== MATÉRIAS =====
    async loadMaterias() {
        try {
            const materias = await this.apiCall('/materias/');
            const container = document.getElementById('materiasList');
            container.innerHTML = materias.map(m => `
                <div class="materia-item" onclick="studyAI.gerarQuiz('${m.nome}', '${m.topico}')">
                    <strong>📚 ${m.nome}</strong>
                    <small>${m.topico}</small>
                    <button style="font-size:12px;padding:5px;">Quiz →</button>
                </div>
            `).join('') || '<p>Nenhuma matéria cadastrada</p>';
        } catch (error) {
            document.getElementById('materiasList').innerHTML = '<p>Erro ao carregar</p>';
        }
    }

    async addMateria() {
        const nome = document.getElementById('materiaNome').value;
        const topico = document.getElementById('materiaTopico').value;

        if (!nome || !topico) {
            alert('Preencha todos os campos!');
            return;
        }

        try {
            await this.apiCall('/materias/', {
                method: 'POST',
                body: JSON.stringify({nome, topico})
            });
            this.loadMaterias();
            document.getElementById('materiaForm').reset();
            alert('✅ Matéria salva!');
        } catch (error) {
            alert('❌ Erro ao salvar');
        }
    }

    // ===== QUIZ =====
    async gerarQuiz(materia, topico) {
        try {
            this.currentQuiz = await this.apiCall('/gerar-quiz/', {
                method: 'POST',
                body: JSON.stringify({materia, topico})
            });

            document.getElementById('quizTitle').textContent = `${materia} - ${topico}`;
            const container = document.getElementById('perguntasContainer');
            
            container.innerHTML = this.currentQuiz.perguntas.map((p, i) => `
                <div class="pergunta">
                    <h4>${i+1}. ${p.pergunta}</h4>
                    ${p.opcoes.map((op, j) => `
                        <label class="opcao">
                            <input type="radio" name="q${i}" value="${j}" onchange="studyAI.selecionarResposta(${i}, ${j})">
                            ${op}
                        </label>
                    `).join('')}
                </div>
            `).join('');

            document.getElementById('quizSection').classList.remove('hidden');
            window.scrollTo(0, document.body.scrollHeight);
        } catch (error) {
            alert('❌ Erro ao gerar quiz: ' + error.message);
        }
    }

    selecionarResposta(perguntaIndex, opcaoIndex) {
        if (!this.currentQuiz.respostas) {
            this.currentQuiz.respostas = {};
        }
        this.currentQuiz.respostas[perguntaIndex] = opcaoIndex;
    }

    verificarQuiz() {
        if (!this.currentQuiz?.respostas || Object.keys(this.currentQuiz.respostas).length < this.currentQuiz.perguntas.length) {
            alert('Responda todas as perguntas primeiro!');
            return;
        }

        let acertos = 0;
        this.currentQuiz.perguntas.forEach((p, i) => {
            const userResposta = this.currentQuiz.respostas[i];
            const correta = p.resposta_correta;
            
            const inputs = document.querySelectorAll(`input[name="q${i}"]`);
            inputs.forEach((input, j) => {
                const label = input.parentElement;
                label.classList.remove('correct', 'incorrect');
                
                if (j == correta) {
                    label.classList.add('correct');
                } else if (j == userResposta && userResposta != correta) {
                    label.classList.add('incorrect');
                }
            });

            if (userResposta == correta) {
                acertos++;
            }
        });

        alert(`🎯 Você acertou ${acertos} de ${this.currentQuiz.perguntas.length} perguntas!`);
    }

    async gerarPDF() {
        if (!this.currentQuiz) {
            alert('Gere um quiz primeiro!');
            return;
        }

        try {
            const response = await fetch('/gerar-pdf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(this.token && {'Authorization': `Bearer ${this.token}`})
                },
                body: JSON.stringify(this.currentQuiz)
            });

            if (!response.ok) {
                throw new Error('Falha ao gerar PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'quiz-studyai.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            alert('❌ Erro ao gerar PDF: ' + error.message);
        }
    }
}

const studyAI = new StudyAI();

    
  
           
            

    
                
       
               
    
           
            

