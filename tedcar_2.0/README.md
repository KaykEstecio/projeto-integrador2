# TedCar 2.0 - Sistema de Locação de Veículos

Bem-vindo ao **TedCar 2.0**, um sistema web completo para gerenciamento e locação de veículos. Este projeto foi desenvolvido como parte do **Projeto Integrador** do curso de **Análise e Desenvolvimento de Sistemas (ADS)** da **UNISA**.

## 👨‍🎓 Autores

*   **Thiago Pereira**
*   **Kayk Nascimento**

---

## 📝 Descrição do Projeto

O **TedCar 2.0** é uma plataforma que conecta clientes a uma frota de veículos disponíveis para aluguel. O sistema oferece uma interface intuitiva para usuários navegarem, filtrarem e reservarem carros, além de um painel administrativo robusto para gerenciamento total da frota, usuários e locações.

### Principais Funcionalidades

#### 🚗 Para Clientes (Usuários)
*   **Catálogo de Veículos:** Visualização de carros disponíveis com fotos, preços e detalhes.
*   **Filtros Avançados:** Busca por marca, preço máximo e ordenação.
*   **Reservas:** Sistema de agendamento de datas para locação.
*   **Minhas Reservas:** Painel para acompanhar status das solicitações e histórico.
*   **Cancelamento:** Possibilidade de cancelar reservas pendentes.
*   **Autenticação:** Cadastro e Login seguros.

#### 🛠️ Para Administradores
*   **Dashboard:** Visão geral com métricas (Total de Carros, Usuários, Locações Ativas/Pendentes).
*   **Gestão de Veículos:** Adicionar, editar, remover e alterar status (Disponível, Alugado, Manutenção).
*   **Gestão de Usuários:** Listar usuários e bloquear/desbloquear acesso.
*   **Gestão de Locações:** Aprovar, rejeitar ou finalizar reservas.
*   **Logs de Auditoria:** Registro detalhado de todas as ações administrativas.

---

## 🚀 Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes tecnologias:

*   **Linguagem:** [Python 3](https://www.python.org/)
*   **Framework Web:** [Flask](https://flask.palletsprojects.com/)
*   **Banco de Dados:** [SQLite](https://www.sqlite.org/) (via SQLAlchemy)
*   **ORM:** [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
*   **Autenticação:** [Flask-Login](https://flask-login.readthedocs.io/)
*   **Frontend:** HTML5, CSS3 (Design Responsivo e Moderno)

---

## 📂 Estrutura do Projeto

```
tedcar_2.0/
├── app.py              # Aplicação principal e rotas
├── debug_run.py        # Script de execução (Debug)
├── requirements.txt    # Dependências do projeto
├── instance/
│   └── database.db     # Banco de dados SQLite
├── static/             # Arquivos estáticos (CSS, Imagens)
│   ├── css/
│   └── images/
└── templates/          # Templates HTML (Jinja2)
    ├── admin/          # Templates da área administrativa
    └── ...             # Templates públicos e de usuário
```

---

## ⚙️ Instalação e Configuração

Siga os passos abaixo para rodar o projeto em sua máquina local.

### Pré-requisitos
*   Python 3.x instalado.
*   Pip (gerenciador de pacotes do Python).

### Passo a Passo

1.  **Clone ou baixe o repositório:**
    Navegue até a pasta do projeto.

2.  **Instale as dependências:**
    Abra o terminal na pasta `tedcar_2.0` e execute:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Inicialize o Banco de Dados (Automático):**
    O sistema criará o banco de dados automaticamente na primeira execução.

---

## ▶️ Como Executar

Para iniciar o servidor de desenvolvimento:

1.  Certifique-se de estar na pasta `tedcar_2.0`.
2.  Execute o comando:
    ```bash
    python debug_run.py
    ```
3.  O servidor iniciará em: `http://127.0.0.1:5000`

---

## 🔐 Acesso Administrativo

O sistema possui um usuário "Mestre" para primeiro acesso ou recuperação:

*   **Usuário:** `unisa`
*   **Senha:** `unisa`

> **Nota:** Este usuário possui privilégios totais de administrador.

---

## 📞 Contato e Suporte

Para dúvidas sobre o projeto acadêmico, entre em contato com os autores através dos canais institucionais da UNISA.

---
*Projeto desenvolvido para fins acadêmicos - UNISA 2025*
