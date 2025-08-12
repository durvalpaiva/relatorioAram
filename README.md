# 🏨 Dashboard Hoteleiro - Análise RDS & Chart

> Sistema completo de análise de dados hoteleiros com automação de PDFs, dashboard interativo e deploy em nuvem.

## 📊 Demonstração

🔗 **[Ver Dashboard Online](https://dashboard-hotel-aram.streamlit.app/)** *(Deploy no Streamlit Cloud)*

## ✨ Funcionalidades

- 📈 **Dashboard Interativo** - Análise completa com gráficos e KPIs
- 🇧🇷 **Formatação Brasileira** - Datas, moeda (R$) e números formatados
- 📄 **Extração Automática de PDFs** - Processamento de relatórios RDS e Chart
- 📧 **Automação Gmail** - Busca e download automático de anexos
- ☁️ **Deploy em Nuvem** - Supabase (PostgreSQL) + Streamlit Cloud
- 🔄 **Atualização Automática** - GitHub Actions com agendamento diário

## 🧰 Tecnologias Utilizadas

### Frontend & Dashboard
- **Streamlit 1.48.0** - Interface web interativa
- **Plotly 6.2.0** - Gráficos dinâmicos e visualizações

### Backend & Banco de Dados  
- **Supabase** - PostgreSQL em nuvem
- **python-dotenv** - Gerenciamento de variáveis de ambiente

### Processamento de Dados
- **pandas 2.2.3** - Manipulação e análise de dados
- **pdfplumber 0.7.6** - Extração de dados de PDFs
- **sqlite3** - Banco local para desenvolvimento

### Automação & Deploy
- **GitHub Actions** - CI/CD e automação
- **imaplib/smtplib** - Integração com Gmail (nativo Python)

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.11+
- Conta Gmail com senha de aplicativo
- Conta Supabase (para produção)

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/dashboard-hoteleiro.git
cd dashboard-hoteleiro
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure Variáveis de Ambiente
Crie um arquivo `.env`:
```env
GMAIL_EMAIL=seu-email@gmail.com
GMAIL_PASSWORD=sua-senha-de-aplicativo
SUPABASE_URL=sua-url-do-supabase
SUPABASE_ANON_KEY=sua-chave-anonima
SUPABASE_SERVICE_KEY=sua-chave-de-servico
```

### 4. Execute o Dashboard
```bash
streamlit run main.py
```

## 🌐 Deploy em Produção

### Opção 1: Streamlit Cloud (Recomendado)
1. Faça push para GitHub
2. Acesse [Streamlit Cloud](https://share.streamlit.io/)
3. Conecte seu repositório
4. Configure as variáveis de ambiente
5. Deploy automático! 🎉

### Opção 2: Deploy Manual
Consulte o arquivo `README_DEPLOY.md` para instruções detalhadas.

## 📊 Estrutura do Projeto

```
projeto-hotel/
├── 📄 main.py                 # Arquivo principal do dashboard
├── 📁 pages/                  # Páginas do Streamlit
│   ├── 1_📊_Resumo_Geral.py  # KPIs e métricas principais
│   ├── 2_📅_Consulta_Periodo.py # Consulta por período
│   └── 3_📈_Visualizacao_Graficos.py # Gráficos comparativos
├── 📁 utils/                  # Utilitários
│   ├── database.py           # Conexão com banco
│   └── email_utils.py         # Automação Gmail
├── 📁 .streamlit/            # Configurações Streamlit
├── 📁 .github/workflows/     # GitHub Actions
└── 📄 requirements.txt       # Dependências Python
```

## 🔐 Segurança

- ✅ Variáveis sensíveis em `.env` (não commitado)
- ✅ Conexão segura com Supabase via chaves de API
- ✅ Senha de aplicativo Gmail (não senha principal)
- ✅ Arquivos locais excluídos via `.gitignore`

## 📈 Dados Processados

### Fonte RDS (Revenue Data System)
- 💰 Faturamento diário
- 👥 Número de hóspedes (PAX)
- 🏠 Taxa de ocupação
- 💵 Diária média

### Fonte Chart (Online Travel Agencies)
- 🌐 Booking.com, Expedia, Decolar
- 🏨 Vendas internas (site próprio)
- 📊 Ranking de compradores
- 💲 Valores por OTA

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 Suporte

- 📧 **Email:** seu-email@dominio.com
- 📱 **WhatsApp:** +55 11 99999-9999
- � **Issues:** [GitHub Issues](https://github.com/seu-usuario/dashboard-hoteleiro/issues)

---

<div align="center">

**⭐ Se este projeto foi útil, deixe uma estrela!**

Made with ❤️ in Brasil 🇧🇷

</div>

- O projeto funciona com qualquer conta Yahoo que tenha IMAP e SMTP ativados.
- A senha de aplicativo é obrigatória para autenticação segura.
- Você pode bloquear remetentes indesejados diretamente nas configurações de privacidade do Yahoo:
  https://mail.yahoo.com/d/settings/9 
