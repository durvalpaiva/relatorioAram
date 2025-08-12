import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório raiz ao path para importar o módulo de formatação
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.formatacao_br import (
    formatar_data_br,
    formatar_moeda_br,
    formatar_numero_br,
    formatar_percentual_br
)

from utils.database import execute_query, test_connection

st.set_page_config(page_title="Resumo Geral", page_icon="📊", layout="wide")

def get_ultimo_dia_data():
    """Obtém dados do último dia disponível da tabela rds_vendas"""
    try:
        # Buscar último dia com dados na tabela rds_vendas (mesma da página 2)
        query_ultimo_dia = """
        SELECT 
            data,
            valor_total,
            pax_hoje,
            ocupacao_hoje,
            valor_eventos,
            diaria_media_uh
        FROM rds_vendas 
        WHERE data = (SELECT MAX(data) FROM rds_vendas)
        ORDER BY data DESC
        LIMIT 1
        """
        ultimo_dia = execute_query(query_ultimo_dia)
        
        return ultimo_dia
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados do último dia: {str(e)}")
        return pd.DataFrame()

def get_acumulado_mes():
    """Obtém dados acumulados do mês atual até o dia de hoje"""
    try:
        # Dados do mês atual até hoje
        hoje = datetime.now().strftime('%d/%m/%Y')
        query_mes = """
        SELECT 
            SUM(valor_total) as faturamento_mes,
            COUNT(*) as vendas_mes,
            AVG(ocupacao_hoje) as ocupacao_media
        FROM rds_vendas 
        WHERE substr(data, 4, 2) = '08' AND substr(data, 7, 4) = '2025'
        AND data <= ?
        """
        mes_atual = execute_query(query_mes, params=(hoje,))
        
        return mes_atual
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados do mês: {str(e)}")
        return pd.DataFrame()

def get_top_ota_agencias():
    """Obtém as 3 principais OTA/AGÊNCIAS da tabela chart_compradores"""
    try:
        # Primeiro tentar a nova tabela com dados duplos
        hoje = datetime.now().strftime('%d/%m/%Y')
        query_duplos = """
        SELECT 
            comprador as ota_agencia,
            SUM(total_reservas) as total_reservas,
            COUNT(*) as qtd_reservas
        FROM chart_compradores_duplo 
        WHERE substr(data, 4, 2) = '08' AND substr(data, 7, 4) = '2025'
        AND data <= ?
        GROUP BY comprador
        ORDER BY total_reservas DESC
        LIMIT 5
        """
        
        try:
            top_ota = execute_query(query_duplos, params=(hoje,))
            if not top_ota.empty:
                return top_ota
        except:
            pass  # Tabela ainda não existe, usar fallback
        
        # Fallback para tabela chart_compradores antiga
        query_ota = """
        SELECT 
            comprador as ota_agencia,
            SUM(valor) as total_reservas,
            COUNT(*) as qtd_reservas
        FROM chart_compradores 
        WHERE substr(data, 4, 2) = '08' AND substr(data, 7, 4) = '2025'
        AND data <= ?
        GROUP BY comprador
        ORDER BY total_reservas DESC
        LIMIT 5
        """
        top_ota = execute_query(query_ota, params=(hoje,))
        
        return top_ota
    except Exception as e:
        # Fallback para rds_vendas se chart_compradores não existir
        try:
            query_fallback = """
            SELECT 
                'RDS VENDAS' as ota_agencia,
                SUM(valor_total) as total_reservas,
                COUNT(*) as qtd_reservas
            FROM rds_vendas 
            WHERE substr(data, 4, 2) = '08' AND substr(data, 7, 4) = '2025'
            AND data <= ?
            ORDER BY total_reservas DESC
            LIMIT 3
            """
            hoje = datetime.now().strftime('%d/%m/%Y')
            top_ota = execute_query(query_fallback, params=(hoje,))
            return top_ota
        except:
            st.error(f"❌ Erro ao buscar OTA/Agências: {str(e)}")
            return pd.DataFrame()

def get_vendas_internas():
    """Obtém dados de vendas internas do hotel - categorias específicas com valores duplos"""
    try:
        # Primeiro tentar a nova tabela com dados duplos
        query_duplos = """
        SELECT 
            comprador as categoria_venda,
            SUM(total_reservas) as total_reservas,
            SUM(reservas_dia) as reservas_dia_especifico,
            dia_referencia
        FROM chart_compradores_duplo 
        WHERE substr(data, 4, 2) = '08' AND substr(data, 7, 4) = '2025'
        AND (
            comprador LIKE '%MOTOR DE RESERVAS%' 
            OR comprador LIKE '%PARTICULAR%'
            OR comprador LIKE '%EVENTOS IMIRA PLAZA%'
            OR comprador = 'PARTICULAR'
        )
        GROUP BY comprador, dia_referencia
        ORDER BY total_reservas DESC
        """
        
        try:
            vendas_internas = execute_query(query_duplos)
            if not vendas_internas.empty:
                return vendas_internas
        except:
            pass  # Tabela ainda não existe, usar fallback
        
        # Fallback para tabela antiga
        query_internas = """
        SELECT 
            comprador as categoria_venda,
            SUM(valor) as faturamento_servico
        FROM chart_compradores 
        WHERE substr(data, 4, 2) = '08' AND substr(data, 7, 4) = '2025'
        AND (
            comprador LIKE '%MOTOR DE RESERVAS%' 
            OR comprador LIKE '%PARTICULAR%'
            OR comprador LIKE '%EVENTOS IMIRA PLAZA%'
            OR comprador = 'PARTICULAR'
        )
        GROUP BY comprador
        ORDER BY faturamento_servico DESC
        """
        vendas_internas = execute_query(query_internas)
        
        return vendas_internas
    except Exception as e:
        st.error(f"❌ Erro ao buscar vendas internas: {str(e)}")
        return pd.DataFrame()

st.title("📊 Resumo Geral do Hotel")

# Obter dados
ultimo_dia = get_ultimo_dia_data()
mes_atual = get_acumulado_mes()
top_ota_agencias = get_top_ota_agencias()
vendas_internas = get_vendas_internas()

# Seção de métricas principais
st.header("📈 Principais Indicadores")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not ultimo_dia.empty:
        st.metric(
            "💰 Faturamento Último Dia", 
            formatar_moeda_br(ultimo_dia.iloc[0]['valor_total']),
            delta=f"{formatar_data_br(ultimo_dia.iloc[0]['data'])}"
        )
    else:
        st.metric("💰 Faturamento Último Dia", "N/A")

with col2:
    if not mes_atual.empty:
        st.metric(
            "📊 Acumulado do Mês (até hoje)", 
            formatar_moeda_br(mes_atual.iloc[0]['faturamento_mes'])
        )
    else:
        st.metric("📊 Acumulado do Mês (até hoje)", "N/A")

with col3:
    if not ultimo_dia.empty:
        st.metric(
            "🏨 Ocupação do Dia", 
            formatar_percentual_br(ultimo_dia.iloc[0]['ocupacao_hoje']),
            delta=f"{formatar_data_br(ultimo_dia.iloc[0]['data'])}"
        )
    else:
        st.metric("🏨 Ocupação do Dia", "N/A")

with col4:
    if not ultimo_dia.empty:
        st.metric(
            "👥 PAX Hoje", 
            formatar_numero_br(ultimo_dia.iloc[0]['pax_hoje']),
            delta=f"{formatar_data_br(ultimo_dia.iloc[0]['data'])}"
        )
    else:
        st.metric("👥 PAX Hoje", "N/A")

# Métricas adicionais do último dia
st.header("📅 Detalhes do Último Dia")

col1, col2, col3 = st.columns(3)

with col1:
    if not ultimo_dia.empty:
        st.metric("🎉 Eventos do Dia", formatar_moeda_br(ultimo_dia.iloc[0]['valor_eventos']))
    else:
        st.metric("🎉 Eventos do Dia", "N/A")

with col2:
    if not ultimo_dia.empty:
        st.metric("💎 Diária Média UH", formatar_moeda_br(ultimo_dia.iloc[0]['diaria_media_uh']))
    else:
        st.metric("💎 Diária Média UH", "N/A")

with col3:
    if not ultimo_dia.empty:
        # Calcular receita total do dia (faturamento + eventos)
        receita_total = ultimo_dia.iloc[0]['valor_total'] + ultimo_dia.iloc[0]['valor_eventos']
        st.metric("💰 Receita Total do Dia", formatar_moeda_br(receita_total))
    else:
        st.metric("💰 Receita Total do Dia", "N/A")

# Seção de principais clientes/OTA/AGÊNCIAS
st.header("🏢 Principais Clientes ou OTA/AGÊNCIAS (Acumulado)")

if not top_ota_agencias.empty:
    for i, ota in top_ota_agencias.iterrows():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{i+1}º {ota['ota_agencia']}**")
        with col2:
            st.write(f"**{formatar_numero_br(ota['total_reservas'])}** reservas")
else:
    st.info("Dados de principais clientes/OTA/AGÊNCIAS não disponíveis")

# Seção de vendas internas
st.header("🏪 Vendas Internas do Hotel (Acumulado)")
st.caption("**Categorias:** MOTOR DE RESERVAS (SITE DO HOTEL), PARTICULAR, PARTICULAR - GRUPOS e EVENTOS IMIRA PLAZA")

if not vendas_internas.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Por Categoria")
        for i, categoria in vendas_internas.iterrows():
            # Simplificar nomes longos para exibição
            nome_categoria = categoria['categoria_venda']
            if 'MOTOR DE RESERVAS' in nome_categoria:
                nome_exibido = "🌐 Site do Hotel"
            elif 'EVENTOS IMIRA' in nome_categoria:
                nome_exibido = "🎉 Eventos Imira Plaza"
            elif nome_categoria == 'PARTICULAR':
                nome_exibido = "👤 Particular"
            else:
                nome_exibido = nome_categoria
            
            # Verificar se temos dados duplos (nova estrutura) ou simples (antiga)
            if 'total_reservas' in categoria:
                # Nova estrutura - mostrar apenas total de reservas
                total = categoria['total_reservas']
                st.write(f"**{nome_exibido}:** {total} reservas")
            elif 'faturamento_servico' in categoria:
                # Estrutura antiga
                st.write(f"**{nome_exibido}:** {formatar_moeda_br(categoria['faturamento_servico'])}")
            else:
                st.write(f"**{nome_exibido}:** Dados não disponíveis")
    
    with col2:
        st.subheader("Total Vendas Internas")
        
        # Calcular total baseado na estrutura disponível
        if 'total_reservas' in vendas_internas.columns:
            # Nova estrutura - mostrar apenas total de reservas
            total_reservas = vendas_internas['total_reservas'].sum()
            st.metric("Total Reservas", f"{total_reservas}")
            
        elif 'faturamento_servico' in vendas_internas.columns:
            # Estrutura antiga - mostrar faturamento
            total_interno = vendas_internas['faturamento_servico'].sum()
            st.metric("Total", formatar_moeda_br(total_interno))
            
            # Calcular percentual do total geral
            if not ultimo_dia.empty and not mes_atual.empty:
                percentual_interno = (total_interno / mes_atual.iloc[0]['faturamento_mes']) * 100 if mes_atual.iloc[0]['faturamento_mes'] > 0 else 0
                st.write(f"📊 **{formatar_percentual_br(percentual_interno)}** do faturamento total")
else:
    st.info("📝 Dados de vendas internas não disponíveis ou ainda não processados")

# Resumo final
st.header("📋 Resumo Executivo")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Hoje")
    if not ultimo_dia.empty:
        st.write(f"• **Data:** {formatar_data_br(ultimo_dia.iloc[0]['data'])}")
        st.write(f"• **Faturamento:** {formatar_moeda_br(ultimo_dia.iloc[0]['valor_total'])}")
        st.write(f"• **PAX:** {formatar_numero_br(ultimo_dia.iloc[0]['pax_hoje'])}")
        st.write(f"• **Ocupação:** {formatar_percentual_br(ultimo_dia.iloc[0]['ocupacao_hoje'])}")
        st.write(f"• **Eventos:** {formatar_moeda_br(ultimo_dia.iloc[0]['valor_eventos'])}")
    else:
        st.info("Dados do último dia não disponíveis")

with col2:
    st.subheader("📊 Mês Atual (até hoje)")
    if not mes_atual.empty:
        st.write(f"• **Faturamento Acumulado:** {formatar_moeda_br(mes_atual.iloc[0]['faturamento_mes'])}")
        st.write(f"• **Total de Registros:** {formatar_numero_br(mes_atual.iloc[0]['vendas_mes'])}")
        st.write(f"• **Ocupação Média:** {formatar_percentual_br(mes_atual.iloc[0]['ocupacao_media'])}")
    
    if not ultimo_dia.empty:
        st.write(f"• **Última atualização:** {formatar_data_br(ultimo_dia.iloc[0]['data'])}")
    else:
        st.info("Dados do mês não disponíveis")

# Informações do sistema
st.header("ℹ️ Informações do Sistema")
st.info(f"📅 **Última atualização:** {formatar_data_br(datetime.now())} às {datetime.now().strftime('%H:%M:%S')}")

# Nota sobre dados
st.warning("📝 **Nota:** Os dados são consultados em tempo real do banco de dados. Se alguma informação não estiver disponível, verifique se as tabelas correspondentes existem no banco.")
