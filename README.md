# OLX Vehicle Monitor - Home Assistant Add-on

Monitor de anúncios de veículos da OLX com notificações via ntfy.sh para Home Assistant OS.

## Sobre

Este add-on monitora automaticamente novos anúncios de veículos na OLX (Minas Gerais) e envia notificações via [ntfy.sh](https://ntfy.sh) quando novos anúncios são encontrados.

### Características

- 🚗 Monitora anúncios de veículos em Minas Gerais
- 💰 Filtro de preço: R$ 19.000 - R$ 26.000
- 🔔 Notificações via ntfy.sh (tópico: `carros-mg-olx`)
- ⏱️ Verificação automática a cada 10 minutos
- 📱 Todos os novos anúncios compilados em uma única mensagem
- 💾 Persistência de dados para evitar duplicatas
- 🐳 Containerizado para HAOS

## Instalação

### Método 1: Repositório Customizado (Recomendado)

1. Acesse o **Home Assistant** → **Configurações** → **Complementos** → **Loja de Complementos**
2. Clique no menu ⋮ (canto superior direito) → **Repositórios**
3. Adicione este repositório:
   ```
   https://github.com/YOUR_USERNAME/olx-vehicle-monitor
   ```
4. Clique em **Adicionar**
5. Atualize a página
6. Procure por "OLX Vehicle Monitor" e clique em **Instalar**

### Método 2: Instalação Local

1. Copie a pasta `olx-vehicle-monitor` para `/addons/` no seu HAOS:
   ```bash
   scp -r olx-vehicle-monitor root@homeassistant.local:/addons/
   ```
2. Acesse **Configurações** → **Complementos** → **Loja de Complementos**
3. Atualize a página
4. O add-on aparecerá na lista de complementos locais

## Uso

### 1. Iniciar o Add-on

1. Após a instalação, abra o add-on
2. Clique em **Iniciar**
3. Ative **Iniciar na inicialização** para executar automaticamente

### 2. Visualizar Logs

- Acesse a aba **Logs** do add-on para ver:
  - Status das verificações
  - Número de anúncios encontrados
  - Novos anúncios detectados
  - Erros (se houver)

### 3. Receber Notificações

Para receber as notificações no seu dispositivo:

1. **Instale o aplicativo ntfy.sh**:
   - Android: [Google Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
   - iOS: [App Store](https://apps.apple.com/app/ntfy/id1625396347)
   - Web: [ntfy.sh](https://ntfy.sh)

2. **Inscreva-se no tópico**:
   - Abra o app
   - Toque em **Subscribe to topic**
   - Digite: `carros-mg-olx`
   - Pronto! Você receberá notificações quando novos anúncios aparecerem

### Formato das Notificações

```
🚗 Novos Anúncios OLX - 3 veículos

1. Fiat Uno 2015
   R$ 25.000
   https://mg.olx.com.br/...
   📍 Belo Horizonte, Centro - DDD 31

2. VW Gol 2018
   R$ 22.500
   https://mg.olx.com.br/...
   📍 Contagem - DDD 31

3. Chevrolet Onix 2020
   R$ 24.800
   https://mg.olx.com.br/...
   📍 Betim - DDD 31
```

## Configuração

### Filtros OLX (Hardcoded)

Este add-on monitora veículos com os seguintes filtros:

- **Região**: Minas Gerais
- **Preço**: R$ 19.000 - R$ 26.000
- **Categoria**: Carros, vans e utilitários
- **Combustível**: Flex, Gasolina, Gasolina/GNV
- **Câmbio**: Manual, Automático, Automatizado/CVT

Para alterar os filtros, você precisará modificar a URL no arquivo `app/monitor.py`.

### Intervalo de Verificação

O add-on verifica novos anúncios a cada **10 minutos** por padrão.

Para alterar, edite a variável `CHECK_INTERVAL` em `app/monitor.py`:
```python
CHECK_INTERVAL = 600  # segundos (600 = 10 minutos)
```

### Tópico ntfy.sh

O tópico padrão é `carros-mg-olx`.

Para alterar, edite `NTFY_TOPIC` em `app/monitor.py`:
```python
NTFY_TOPIC = "seu-topico-personalizado"
```

## Arquitetura

### Estrutura do Projeto

```
olx-vehicle-monitor/
├── config.yaml           # Configuração do add-on HAOS
├── Dockerfile           # Container definition
├── run.sh              # Script de inicialização
├── requirements.txt    # Dependências Python
├── README.md          # Este arquivo
└── app/
    ├── monitor.py     # Loop principal de monitoramento
    ├── scraper.py     # Extração de anúncios (Playwright)
    ├── storage.py     # Persistência em JSON
    └── notifier.py    # Integração com ntfy.sh
```

### Como Funciona

1. **Scraping**: Usa Playwright para carregar a página OLX e extrair dados do `__NEXT_DATA__` (JSON embutido)
2. **Deduplicação**: Compara IDs dos anúncios com lista de IDs já vistos (armazenada em `/data/seen_listings.json`)
3. **Notificação**: Compila todos os novos anúncios em uma única mensagem e envia para ntfy.sh
4. **Persistência**: Salva IDs dos novos anúncios para evitar duplicatas futuras
5. **Loop**: Aguarda 10 minutos e repete

### Tecnologias

- **Python 3**: Linguagem principal
- **Playwright**: Browser automation para scraping
- **ntfy.sh**: Sistema de notificações push
- **Home Assistant OS**: Plataforma de execução
- **Docker**: Containerização

## Troubleshooting

### Add-on não inicia

- Verifique os logs para erros
- Certifique-se de que há espaço em disco suficiente
- Tente reiniciar o add-on

### Não recebo notificações

1. Verifique se você está inscrito no tópico correto: `carros-mg-olx`
2. Teste enviando uma mensagem manual:
   ```bash
   curl -d "Teste" ntfy.sh/carros-mg-olx
   ```
3. Verifique os logs do add-on para erros de notificação

### Muitas notificações duplicadas

- Verifique se o arquivo `/data/seen_listings.json` existe
- Se necessário, pare o add-on e exclua o arquivo para resetar

### OLX mudou a estrutura da página

Se o scraping parar de funcionar:
1. Abra uma issue no repositório GitHub
2. A estrutura `__NEXT_DATA__` pode ter mudado
3. O código em `scraper.py` precisará ser atualizado

## Desenvolvimento

### Testar Localmente

```bash
cd olx-vehicle-monitor

# Instalar dependências
pip3 install -r requirements.txt
playwright install chromium

# Criar diretório de dados
mkdir -p /tmp/data

# Executar (ajuste DATA_FILE em storage.py para /tmp/data)
python3 app/monitor.py
```

### Build Docker

```bash
docker build -t olx-vehicle-monitor .
docker run -v $(pwd)/data:/data olx-vehicle-monitor
```

## Contribuindo

Contribuições são bem-vindas! Para modificar:

1. Fork este repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## Licença

Este projeto é fornecido "como está", sem garantias.

## Avisos

- Este add-on faz scraping da OLX, o que pode violar os Termos de Serviço do site
- Use por sua conta e risco
- A OLX pode bloquear requisitos se detectar automação
- O formato da página pode mudar, quebrando o scraper
