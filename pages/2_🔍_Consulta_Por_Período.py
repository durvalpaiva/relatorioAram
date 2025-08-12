import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Funções de formatação brasileira
def formatar_data_br(data_str):
    """Converte data para formato brasileiro dd/mm/aaaa"""
    try:
        if pd.isna(data_str) or data_str == '' or data_str is None:
            return "N/A"
        return str(data_str)
    except:
        return "N/A"

def formatar_moeda_br(valor):
    """Formata valor monetário no padrão brasileiro: R$ 1.234.567,89"""
    try:
        if pd.isna(valor) or valor == '' or valor is None:
            return "N/A"
        
        valor_float = float(valor)
        valor_str = f"{valor_float:,.2f}"
        partes = valor_str.split('.')
        parte_inteira = partes[0].replace(',', '.')
        parte_decimal = partes[1] if len(partes) > 1 else '00'
        return f"R$ {parte_inteira},{parte_decimal}"
    except:
        return "N/A"

def formatar_numero_br(valor):
    """Formata número no padrão brasileiro: 1.234.567"""
    try:
        if pd.isna(valor) or valor == '' or valor is None:
            return "N/A"
        
        valor_int = int(float(valor))
        return f"{valor_int:,}".replace(',', '.')
    except:
        return "N/A"

def formatar_percentual_br(valor):
    """Formata percentual no padrão brasileiro: 12,5%"""
    try:
        if pd.isna(valor) or valor == '' or valor is None:
            return "N/A"
        
        valor_float = float(valor)
        return f"{valor_float:.1f}%".replace('.', ',')
    except:
        return "N/A"

st.set_page_config(page_title="Consulta Por Período", page_icon="🔍")
st.title("🔍 Consulta de Relatórios por Período")

# Conexão com o banco de dados
conn = sqlite3.connect("relatorios.db")

# Consultar dados RDS
st.subheader("📊 Filtro por Período - Vendas RDS")

try:
    rds = pd.read_sql_query("SELECT * FROM rds_vendas ORDER BY data", conn)
    
    if not rds.empty:
        # Converter datas para datetime para filtros
        rds['data_dt'] = pd.to_datetime(rds['data'], format='%d/%m/%Y', errors='coerce')
        
        # Filtros de data
        col1, col2 = st.columns(2)
        
        with col1:
            data_inicio = st.date_input(
                "📅 Data Início:",
                value=rds['data_dt'].min().date() if not rds['data_dt'].isna().all() else datetime.now().date()
            )
        
        with col2:
            data_fim = st.date_input(
                "📅 Data Fim:",
                value=rds['data_dt'].max().date() if not rds['data_dt'].isna().all() else datetime.now().date()
            )
        
        # Filtrar dados
        mask = (rds['data_dt'] >= pd.to_datetime(data_inicio)) & (rds['data_dt'] <= pd.to_datetime(data_fim))
        rds_filtrado = rds[mask]
        
        if not rds_filtrado.empty:
            # Formatação brasileira para datas
            data_inicio_br = data_inicio.strftime('%d/%m/%Y')
            data_fim_br = data_fim.strftime('%d/%m/%Y')
            st.subheader(f"📈 Resultados: {data_inicio_br} a {data_fim_br}")
            
            # Métricas do período
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_faturamento = rds_filtrado['valor_total'].sum()
                st.metric("💰 Faturamento Total", formatar_moeda_br(total_faturamento))
            
            with col2:
                total_pax = rds_filtrado['pax_hoje'].sum()
                st.metric("👥 Total PAX", formatar_numero_br(total_pax))
            
            with col3:
                ocupacao_media = rds_filtrado['ocupacao_hoje'].mean()
                st.metric("🏨 Ocupação Média", formatar_percentual_br(ocupacao_media))
            
            with col4:
                diaria_media = rds_filtrado['diaria_media_uh'].mean()
                st.metric("💎 Diária Média", formatar_moeda_br(diaria_media))
            
            # Tabela detalhada
            st.subheader("📋 Detalhamento por Data")
            
            # Preparar dados para exibição
            rds_display = rds_filtrado.drop(['data_dt'], axis=1, errors='ignore')
            if 'id' in rds_display.columns:
                rds_display = rds_display.drop('id', axis=1)
            
            # Formatação brasileira
            rds_display['data'] = rds_display['data'].apply(formatar_data_br)
            rds_display['valor_total'] = rds_display['valor_total'].apply(formatar_moeda_br)
            rds_display['valor_eventos'] = rds_display['valor_eventos'].apply(formatar_moeda_br)
            rds_display['pax_hoje'] = rds_display['pax_hoje'].apply(formatar_numero_br)
            rds_display['ocupacao_hoje'] = rds_display['ocupacao_hoje'].apply(formatar_percentual_br)
            rds_display['diaria_media_uh'] = rds_display['diaria_media_uh'].apply(formatar_moeda_br)
            
            # Renomear colunas
            rds_display.columns = ['Data', 'Valor Total', 'Valor Eventos', 'PAX Hoje', 'Ocupação %', 'Diária Média']
            
            st.dataframe(rds_display, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado para o período selecionado.")
    else:
        st.info("Nenhum dado de vendas RDS disponível.")
        
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")

# Consultar dados Chart
st.subheader("🏢 Filtro por Período - Principais Clientes ou OTA/AGÊNCIAS")

try:
    # Tentar primeiro a nova tabela com totais reais
    try:
        chart = pd.read_sql_query("SELECT * FROM chart_compradores_duplo ORDER BY data, total_reservas DESC", conn)
        usa_totais_reais = True
    except:
        # Fallback para tabela antiga
        chart = pd.read_sql_query("SELECT * FROM chart_compradores ORDER BY data, valor DESC", conn)
        usa_totais_reais = False
    
    if not chart.empty:
        # Converter datas
        chart['data_dt'] = pd.to_datetime(chart['data'], format='%d/%m/%Y', errors='coerce')
        
        # Aplicar mesmo filtro de data
        mask_chart = (chart['data_dt'] >= pd.to_datetime(data_inicio)) & (chart['data_dt'] <= pd.to_datetime(data_fim))
        chart_filtrado = chart[mask_chart]
        
        if not chart_filtrado.empty:
            # Métricas dos compradores
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_compradores = chart_filtrado['comprador'].nunique()
                st.metric("🏢 Clientes/OTA Únicos", formatar_numero_br(total_compradores))
            
            with col2:
                if usa_totais_reais:
                    total_reservas = chart_filtrado['total_reservas'].sum()
                    campo_valor = 'total_reservas'
                else:
                    total_reservas = chart_filtrado['valor'].sum()
                    campo_valor = 'valor'
                st.metric("📊 Total Reservas", formatar_numero_br(total_reservas))
            
            with col3:
                if usa_totais_reais:
                    media_reservas = chart_filtrado['total_reservas'].mean()
                else:
                    media_reservas = chart_filtrado['valor'].mean()
                st.metric("📈 Média por Cliente/OTA", formatar_numero_br(media_reservas))
            
            # Top 10 principais clientes do período
            st.subheader("🏆 Top 10 Principais Clientes ou OTA/AGÊNCIAS do Período")
            
            if usa_totais_reais:
                top10 = chart_filtrado.groupby('comprador')['total_reservas'].sum().nlargest(10).reset_index()
                top10_grafico = chart_filtrado.groupby('comprador')['total_reservas'].sum().nlargest(10)
            else:
                top10 = chart_filtrado.groupby('comprador')['valor'].sum().nlargest(10).reset_index()
                top10_grafico = chart_filtrado.groupby('comprador')['valor'].sum().nlargest(10)
            
            top10.columns = ['Cliente/OTA', 'Total Reservas']
            top10['Total Reservas'] = top10['Total Reservas'].apply(formatar_numero_br)
            
            st.dataframe(top10, use_container_width=True)
            
            # Gráfico
            st.bar_chart(top10_grafico)
        else:
            st.warning("Nenhum dado de principais clientes/OTA/AGÊNCIAS encontrado para o período selecionado.")
    else:
        st.info("Nenhum dado de principais clientes/OTA/AGÊNCIAS disponível.")
        
except Exception as e:
    st.error(f"Erro ao carregar dados de principais clientes/OTA/AGÊNCIAS: {str(e)}")

conn.close()
