<<<<<<< HEAD
# fila_zero
=======
# 🍽️ FilaZero

Sistema web para gestão de pedidos e fila de almoço comunitário.
Projeto de Extensão I — Engenharia de Software (Anhanguera).

## ✨ Funcionalidades

- **Cliente**: faz pedido pelo celular e recebe ficha digital com senha (formato `A123`)
- **Acompanhamento ao vivo**: a ficha do cliente atualiza sozinha quando a marmita está pronta
- **Painel da Cozinha**: kanban com 4 colunas (Aguardando → Preparando → Pronto → Entregue)
- **Relatórios**: indicadores do dia + gráfico de 7 dias

## 🛠️ Stack

- Python 3.10+ · FastAPI · SQLAlchemy
- SQLite (local) · PostgreSQL (produção)
- Jinja2 · Tailwind CSS (via CDN) · Chart.js

## 🚀 Como rodar localmente

```bash
# 1. Crie um ambiente virtual
python -m venv venv

# 2. Ative
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode
uvicorn app.main:app --reload
```

Abra http://127.0.0.1:8000

## 🔑 Senhas padrão da equipe

Definidas em `app/auth.py` (sobrescreva por variável de ambiente em produção):

- **Cozinha**: `cozinha123` → leva direto ao painel da cozinha
- **Admin**: `admin123` → leva ao relatório

**Sempre troque em produção** definindo:
- `SENHA_COZINHA`
- `SENHA_ADMIN`
- `SECRET_KEY` (qualquer string longa e aleatória)

## 🌐 Deploy no Render (gratuito)

1. Suba o código para um repositório no GitHub
2. No Render → **New +** → **Web Service** → conecte o repositório
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Em **Environment**, adicione as variáveis:
   - `SECRET_KEY` = (gere uma string aleatória longa)
   - `SENHA_COZINHA` = (sua senha)
   - `SENHA_ADMIN` = (sua senha)
   - `DATABASE_URL` = (opcional — se quiser usar Postgres do Render)

## 📂 Estrutura

```
filazero/
├── app/
│   ├── main.py              # App FastAPI
│   ├── database.py          # Conexão SQLAlchemy
│   ├── models.py            # Pedido + StatusPedido
│   ├── auth.py              # Login simples por sessão
│   ├── utils.py             # Gerador de senha A123
│   ├── routers/
│   │   ├── cliente.py       # /, /pedir, /ficha/{senha}
│   │   ├── cozinha.py       # /cozinha + ações
│   │   └── admin.py         # /admin (relatórios)
│   ├── templates/
│   │   ├── base.html        # Layout
│   │   ├── home.html        # Formulário do cliente
│   │   ├── ficha.html       # Ficha com senha
│   │   ├── cozinha.html     # Kanban da cozinha
│   │   ├── admin.html       # Dashboard
│   │   ├── login.html
│   │   ├── 404.html
│   │   └── _card_pedido.html
│   └── static/
└── requirements.txt
```

## 🔄 Fluxo

```
[Cliente] → preenche nome → recebe senha A123 → acompanha status
              ↓
       (pedido criado)
              ↓
[Cozinha] → vê na coluna "Aguardando" → clica "Preparar" → "Pronto"
              ↓
[Cliente] → ficha atualiza sozinha → "🎉 Está pronto!" → vai retirar
              ↓
[Cozinha] → clica "Confirmar entrega" → pedido vai para "Entregue"
```

## 💡 Próximos passos (opcionais)

- Integração com Pix (cobrança do R$ 1,00 antecipado)
- Notificação WhatsApp quando ficar pronto
- QR Code na ficha para conferência rápida na retirada
- Histórico para o beneficiário (login simples por telefone)
>>>>>>> f135630 (Initial commit from local)
