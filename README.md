# WebCore — site público + portal privado

Projeto FastAPI com landing page, captação de orçamentos, login privado, controle financeiro e gestão simples de leads.

## Executar localmente

1. Instale Python 3.11+.
2. `python -m venv .venv`
3. Ative: Windows `.venv\\Scripts\\activate`; Linux/macOS `source .venv/bin/activate`.
4. `pip install -r requirements.txt`
5. `python setup_admin.py` e copie os valores gerados para variáveis de ambiente (ou `.env` usando carregador externo; FastAPI não lê `.env` automaticamente).
6. Defina também `WHATSAPP_NUMBER` (apenas números com DDI 55), `CONTACT_EMAIL`, `INSTAGRAM_URL`.
7. `uvicorn app:app --reload`
8. Site: `http://127.0.0.1:8000/` — Portal: `http://127.0.0.1:8000/portal/login`.

## Publicação

- Use PostgreSQL via `DATABASE_URL` para dados persistentes. SQLite é adequado apenas a testes locais.
- Em produção, defina `COOKIE_SECURE=true`, HTTPS, `SESSION_SECRET` fixo e longo, e credenciais fortes.
- Para usar dois domínios distintos, configure proxy/redirecionamento de `/portal` e `/portal/*` para um subdomínio privado, com cookies e rotas ajustados; a versão inicial usa um único domínio com rota privada.
- Não há envio automático de e-mail, WhatsApp ou Instagram; os contatos são armazenados em `leads` e vistos no portal. Botões de contato só aparecem quando as variáveis são configuradas.
- Antes de produção: adicionar proteção CSRF, limitação de tentativas de login, backups automáticos, monitoramento, política de privacidade/LGPD e integração de notificações.
- Para iniciar na Railway, configure comando `uvicorn app:app --host 0.0.0.0 --port $PORT` e variáveis de ambiente.

## Organização

- `app.py`: rotas, autenticação e banco
- `templates/`: páginas
- `static/style.css`: identidade visual responsiva
- `setup_admin.py`: gera hash de senha sem salvar a senha

## Escopo da primeira versão

A área privada possui dois cards principais (landing page e controle de custos), além de acesso aos orçamentos. O portfólio está marcado como espaço reservado, sem trabalhos fictícios. O nome WebCore ainda deve ser verificado no INPI e a disponibilidade de domínio/arroba confirmada.
