from imap_tools import MailBox, AND
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar variáveis do .env
load_dotenv()

def testar_conexao_gmail():
    """Testa a conexão com o Gmail"""
    try:
        EMAIL = os.getenv("GMAIL_EMAIL")
        APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
        
        if not EMAIL or not APP_PASSWORD:
            logger.error("❌ Credenciais do Gmail não encontradas no .env")
            return False
            
        logger.info(f"🔑 Testando conexão com: {EMAIL}")
        
        with MailBox("imap.gmail.com").login(EMAIL, APP_PASSWORD) as mailbox:
            logger.info("✅ Conexão com Gmail estabelecida com sucesso!")
            
            # Listar pastas disponíveis
            folders = [f.name for f in mailbox.folder.list()]
            logger.info(f"📁 Pastas disponíveis: {folders}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {str(e)}")
        return False

def baixar_pdfs_gmail(dias_anteriores=7, pasta_especifica=None):
    """
    Baixa PDFs do Gmail
    
    Args:
        dias_anteriores (int): Quantos dias para trás buscar emails (padrão: 7)
        pasta_especifica (str): Nome da pasta/label específica (opcional)
    """
    try:
        EMAIL = os.getenv("GMAIL_EMAIL")
        APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
        PASTA_DESTINO = r"C:\Users\durva\OneDrive\Área de Trabalho\Projeto\data"
        
        if not EMAIL or not APP_PASSWORD:
            logger.error("❌ Credenciais não encontradas no .env")
            return False
            
        # Garantir que a pasta destino existe
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        
        logger.info(f"🔍 Conectando ao Gmail: {EMAIL}")
        
        with MailBox("imap.gmail.com").login(EMAIL, APP_PASSWORD) as mailbox:
            
            # Definir pasta para buscar
            if pasta_especifica:
                try:
                    mailbox.folder.set(pasta_especifica)
                    logger.info(f"📂 Buscando na pasta: {pasta_especifica}")
                except:
                    logger.warning(f"⚠️ Pasta '{pasta_especifica}' não encontrada, usando INBOX")
                    mailbox.folder.set("INBOX")
            else:
                mailbox.folder.set("INBOX")
                logger.info("📂 Buscando na pasta: INBOX")
            
            # Data limite para busca
            data_limite = datetime.now() - timedelta(days=dias_anteriores)
            logger.info(f"📅 Buscando emails desde: {data_limite.strftime('%d/%m/%Y')}")
            
            # Buscar emails com anexos
            criterio = AND(date_gte=data_limite.date())
            emails = list(mailbox.fetch(criterio))
            
            # Filtrar apenas emails com anexos
            emails_com_anexos = [msg for msg in emails if msg.attachments]
            
            logger.info(f"📧 Encontrados {len(emails_com_anexos)} emails com anexos")
            
            pdfs_baixados = 0
            
            for msg in emails_com_anexos:
                logger.info(f"📩 Processando email: {msg.subject} - {msg.date}")
                
                for att in msg.attachments:
                    if att.filename and att.filename.lower().endswith(".pdf"):
                        filepath = os.path.join(PASTA_DESTINO, att.filename)
                        
                        # Verificar se arquivo já existe
                        if os.path.exists(filepath):
                            logger.info(f"⏭️ Arquivo já existe: {att.filename}")
                            continue
                            
                        try:
                            with open(filepath, 'wb') as f:
                                f.write(att.payload)
                            logger.info(f"📥 Baixado: {att.filename}")
                            pdfs_baixados += 1
                        except Exception as e:
                            logger.error(f"❌ Erro ao salvar {att.filename}: {str(e)}")
            
            logger.info(f"✅ Processo concluído! {pdfs_baixados} PDFs baixados")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro geral: {str(e)}")
        return False

def buscar_pdfs_relatorio(palavra_chave="RDS"):
    """
    Busca especificamente por PDFs de relatório contendo palavra-chave no nome
    
    Args:
        palavra_chave (str): Palavra-chave para filtrar PDFs (padrão: "RDS")
    """
    try:
        EMAIL = os.getenv("GMAIL_EMAIL")
        APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
        PASTA_DESTINO = r"C:\Users\durva\OneDrive\Área de Trabalho\Projeto\data"
        
        logger.info(f"🔍 Buscando PDFs contendo '{palavra_chave}' no nome...")
        
        with MailBox("imap.gmail.com").login(EMAIL, APP_PASSWORD) as mailbox:
            mailbox.folder.set("INBOX")
            
            # Buscar emails dos últimos 30 dias
            data_limite = datetime.now() - timedelta(days=30)
            criterio = AND(date_gte=data_limite.date())
            
            emails = list(mailbox.fetch(criterio))
            pdfs_encontrados = 0
            
            for msg in emails:
                if not msg.attachments:  # Pular emails sem anexos
                    continue
                for att in msg.attachments:
                    if (att.filename and 
                        att.filename.lower().endswith(".pdf") and 
                        palavra_chave.lower() in att.filename.lower()):
                        
                        filepath = os.path.join(PASTA_DESTINO, att.filename)
                        
                        if not os.path.exists(filepath):
                            with open(filepath, 'wb') as f:
                                f.write(att.payload)
                            logger.info(f"📥 Baixado relatório: {att.filename}")
                            pdfs_encontrados += 1
                        else:
                            logger.info(f"⏭️ Relatório já existe: {att.filename}")
            
            logger.info(f"✅ {pdfs_encontrados} relatórios novos baixados")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar relatórios: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testando conexão e download de PDFs do Gmail...")
    
    # Teste 1: Conexão
    if testar_conexao_gmail():
        print("\n📁 Testando download de PDFs...")
        
        # Teste 2: Download geral
        baixar_pdfs_gmail(dias_anteriores=10)
        
        print("\n📊 Buscando especificamente relatórios RDS...")
        
        # Teste 3: Relatórios específicos
        buscar_pdfs_relatorio("RDS")
        
    else:
        print("❌ Falha na conexão. Verifique as credenciais.")
