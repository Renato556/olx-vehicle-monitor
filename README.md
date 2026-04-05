# OLX Vehicle Monitor (Home Assistant Add-on)

Add-on para Home Assistant OS que monitora novos anúncios de veículos na OLX (Minas Gerais) e envia notificações formatadas para o ntfy.sh.

## Funcionalidades (v1.3.1)

- **Frequência:** Verifica novos anúncios a cada 10 minutos.
- **Scraping de Alta Performance:** Utiliza `curl-cffi` com impersonação de Chrome 120 para evitar bloqueios da OLX (sem necessidade de Chromium/Playwright).
- **Filtros Inteligentes:** 
    - Ignora automaticamente anúncios de **Peugeot** e **Citroën**.
    - Filtra por faixa de preço e parâmetros específicos via URL.
- **Notificações Ricas (ntfy.sh):**
    - Títulos como **hyperlinks clicáveis** (Markdown).
    - Exibição de **Preço e Quilometragem** formatada (ex: `R$ 25.000 - 120.000 km`).
    - Remoção automática de acentos e caracteres especiais para compatibilidade total.
    - Divisão inteligente de mensagens para respeitar o limite de 4KB do ntfy.sh.
- **Deduplicação:** Armazena anúncios já vistos em `/data/seen_listings.json` para evitar repetições.

## Configuração Atual (Hardcoded)

- **URL OLX:** Carros em MG, R$ 19.000 a R$ 26.000 (Filtro Particular).
- **Tópico ntfy:** `carros-olx-mg` (ntfy.sh).
- **Intervalo:** 600 segundos (10 minutos).

## Instalação no Home Assistant

1. Vá em **Configurações** > **Add-ons** > **Loja de Add-ons**.
2. Clique nos três pontos (canto superior direito) > **Repositórios**.
3. Adicione a URL do seu repositório GitHub.
4. Localize "OLX Vehicle Monitor" na lista e clique em **Instalar**.
5. Inicie o add-on e acompanhe os logs.

## Estrutura do Projeto

- `olx-monitor/`: Pasta principal do add-on.
  - `app/monitor.py`: Loop principal e lógica de filtros.
  - `app/scraper.py`: Extração de dados via curl-cffi.
  - `app/notifier.py`: Formatação de mensagens e envio.
  - `app/storage.py`: Persistência de dados.
  - `Dockerfile` & `config.yaml`: Configurações do HAOS.
