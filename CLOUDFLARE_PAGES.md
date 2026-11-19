# Publicação comercial WebCore — Cloudflare Pages

Este projeto mantém o aplicativo FastAPI original para desenvolvimento, mas publica **somente o site comercial estático** no Cloudflare Pages.

## Configuração no painel Cloudflare

1. **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Autorize o GitHub e selecione **JoaoGabrii/web_core**, branch **main**.
3. Framework preset: **None**.
4. Build command: `python3 build_static.py`.
5. Build output directory: `dist`.
6. Root directory: deixe vazio (raiz do repositório).
7. Clique em **Save and Deploy**.

A Cloudflare deve disponibilizar uma URL `*.pages.dev`. Não precisa configurar banco, secrets, Railway ou variáveis de ambiente para a landing page.

## O que funciona na versão estática

- Visual 1 e Visual 2
- Logo WC, favicon, portfólio e galerias de projetos
- Planos e complemento de marketing digital
- Seleção de serviços e prévia da mensagem
- Formulário que abre o WhatsApp comercial com a mensagem preenchida

**Importante:** o formulário **não grava leads** no servidor. O visitante precisa efetivamente enviar a mensagem no WhatsApp. Se ele fechar o WhatsApp antes de enviar, a solicitação não será recebida. Nenhum painel administrativo ou financeiro é publicado na Cloudflare.

## Atualizações automáticas

Todo push na branch `main` dispara novo build e deploy no Cloudflare Pages. O GitHub continua sendo a fonte de verdade do código.

## Diagnóstico

- Erro de build: confira se o comando está exatamente `python3 build_static.py`.
- Página em branco: confira se o diretório de saída é `dist`.
- Estilos não carregam: verifique se `/static/style.css` responde.
- Ícone não atualiza: faça atualização forçada no navegador ou limpe o cache.
- Imagens externas de projetos: algumas capturas dependem de serviços de terceiros; confira se estão disponíveis.
