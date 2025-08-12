import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# Funções de formatação brasileira
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

st.set_page_config(page_title="Visualização de Gráficos", page_icon="📈")
st.title("📈 Visualização de Gráficos")

# Conexão com o banco de dados
conn = sqlite3.connect("relatorios.db")

# Gráficos RDS
st.subheader("💰 Análise de Vendas RDS")

try:
    rds = pd.read_sql_query("SELECT * FROM rds_vendas ORDER BY data", conn)
    
    if not rds.empty:
        # Converter data para formato datetime
        rds['data_dt'] = pd.to_datetime(rds['data'], format='%d/%m/%Y', errors='coerce')
        
        # Gráfico de Faturamento por Data
        st.subheader("📊 Faturamento por Data")
        fig_faturamento = px.line(
            rds, 
            x='data_dt', 
            y='valor_total', 
            title='Evolução do Faturamento Diário',
            labels={'data_dt': 'Data', 'valor_total': 'Faturamento (R$)'}
        )
        fig_faturamento.update_traces(line_color='#1f77b4', line_width=3)
        fig_faturamento.update_layout(
            title_font_size=16,
            xaxis_title="Data",
            yaxis_title="Faturamento (R$)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_faturamento, use_container_width=True)
        
        # Gráfico de PAX por Data
        st.subheader("👥 PAX por Data")
        fig_pax = px.bar(
            rds, 
            x='data_dt', 
            y='pax_hoje', 
            title='Número de Hóspedes (PAX) por Data',
            labels={'data_dt': 'Data', 'pax_hoje': 'PAX'},
            color='pax_hoje',
            color_continuous_scale='Blues'
        )
        fig_pax.update_layout(
            title_font_size=16,
            xaxis_title="Data",
            yaxis_title="PAX",
            showlegend=False
        )
        st.plotly_chart(fig_pax, use_container_width=True)
        
        # Gráfico de Ocupação por Data
        st.subheader("🏨 Taxa de Ocupação por Data")
        fig_ocupacao = px.area(
            rds, 
            x='data_dt', 
            y='ocupacao_hoje', 
            title='Taxa de Ocupação Diária (%)',
            labels={'data_dt': 'Data', 'ocupacao_hoje': 'Ocupação (%)'}
        )
        fig_ocupacao.update_traces(fill='tonexty', fillcolor='rgba(0,176,246,0.2)', line_color='rgba(0,176,246,1)')
        fig_ocupacao.update_layout(
            title_font_size=16,
            xaxis_title="Data",
            yaxis_title="Ocupação (%)",
        )
        st.plotly_chart(fig_ocupacao, use_container_width=True)
        
        # Gráfico de Diária Média
        st.subheader("💎 Diária Média por Data")
        fig_diaria = px.bar(
            rds, 
            x='data_dt', 
            y='diaria_media_uh', 
            title='Diária Média por Data',
            labels={'data_dt': 'Data', 'diaria_media_uh': 'Diária Média (R$)'},
            color='diaria_media_uh',
            color_continuous_scale='Greens'
        )
        fig_diaria.update_layout(
            title_font_size=16,
            xaxis_title="Data",
            yaxis_title="Diária Média (R$)",
            showlegend=False
        )
        st.plotly_chart(fig_diaria, use_container_width=True)
        
    else:
        st.info("Nenhum dado RDS disponível para gráficos.")
        
except Exception as e:
    st.error(f"Erro ao carregar dados RDS: {str(e)}")

# Gráficos Chart
st.subheader("🏢 Análise de Principais Clientes ou OTA/AGÊNCIAS")

try:
    chart = pd.read_sql_query("SELECT * FROM chart_compradores ORDER BY valor DESC", conn)
    
    if not chart.empty:
        # Top 10 Principais Clientes
        st.subheader("🏆 Top 10 Principais Clientes ou OTA/AGÊNCIAS por Volume")
        top10_compradores = chart.groupby('comprador')['valor'].sum().nlargest(10).reset_index()
        
        fig_top10 = px.bar(
            top10_compradores, 
            x='valor', 
            y='comprador', 
            orientation='h',
            title='Top 10 Principais Clientes ou OTA/AGÊNCIAS por Total de Reservas',
            labels={'valor': 'Total de Reservas', 'comprador': 'Cliente/OTA'},
            color='valor',
            color_continuous_scale='Viridis'
        )
        fig_top10.update_layout(
            title_font_size=16,
            xaxis_title="Total de Reservas",
            yaxis_title="Cliente/OTA",
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig_top10, use_container_width=True)
        
        # Distribuição de Reservas por Data
        st.subheader("📅 Distribuição de Reservas por Data")
        reservas_por_data = chart.groupby('data')['valor'].sum().reset_index()
        reservas_por_data['data_dt'] = pd.to_datetime(reservas_por_data['data'], format='%d/%m/%Y', errors='coerce')
        
        fig_dist = px.bar(
            reservas_por_data, 
            x='data_dt', 
            y='valor', 
            title='Total de Reservas por Data',
            labels={'data_dt': 'Data', 'valor': 'Total de Reservas'},
            color='valor',
            color_continuous_scale='Oranges'
        )
        fig_dist.update_layout(
            title_font_size=16,
            xaxis_title="Data",
            yaxis_title="Total de Reservas",
            showlegend=False
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Gráfico de Pizza - Top 5 Principais Clientes
        st.subheader("🥧 Participação dos Top 5 Principais Clientes ou OTA/AGÊNCIAS")
        top5_compradores = chart.groupby('comprador')['valor'].sum().nlargest(5).reset_index()
        
        fig_pizza = px.pie(
            top5_compradores, 
            values='valor', 
            names='comprador', 
            title='Participação dos Top 5 Principais Clientes ou OTA/AGÊNCIAS no Total de Reservas'
        )
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        fig_pizza.update_layout(title_font_size=16)
        st.plotly_chart(fig_pizza, use_container_width=True)
        
    else:
        st.info("Nenhum dado de principais clientes/OTA/AGÊNCIAS disponível para gráficos.")
        
except Exception as e:
    st.error(f"Erro ao carregar dados de principais clientes/OTA/AGÊNCIAS: {str(e)}")

# Comparativo RDS vs Chart
st.subheader("⚖️ Comparativo: Faturamento vs Reservas")

try:
    # Combinar dados por data
    rds_resumo = rds.groupby('data').agg({
        'valor_total': 'sum',
        'pax_hoje': 'sum'
    }).reset_index()
    
    chart_resumo = chart.groupby('data').agg({
        'valor': 'sum'
    }).reset_index()
    
    # Merge dos dados com tratamento de valores nulos
    comparativo = pd.merge(rds_resumo, chart_resumo, on='data', how='outer')
    
    # Preencher valores nulos com 0 para evitar gaps no gráfico
    comparativo['valor_total'] = comparativo['valor_total'].fillna(0)
    comparativo['valor'] = comparativo['valor'].fillna(0)
    
    # Converter data e ordenar
    comparativo['data_dt'] = pd.to_datetime(comparativo['data'], format='%d/%m/%Y', errors='coerce')
    comparativo = comparativo.sort_values('data_dt').dropna(subset=['data_dt'])
    
    # Mostrar informações sobre dados faltantes
    dados_faltantes = []
    if comparativo['valor_total'].eq(0).any():
        dias_sem_rds = comparativo[comparativo['valor_total'] == 0]['data'].tolist()
        dados_faltantes.append(f"📊 RDS faltante: {', '.join(dias_sem_rds)}")
    
    if comparativo['valor'].eq(0).any():
        dias_sem_chart = comparativo[comparativo['valor'] == 0]['data'].tolist()
        dados_faltantes.append(f"📈 Chart faltante: {', '.join(dias_sem_chart)}")
    
    if dados_faltantes:
        st.warning("⚠️ **Dados faltantes detectados:**\n" + "\n".join(dados_faltantes))
    
    # Gráfico comparativo
    fig_comparativo = go.Figure()
    
    # Linha RDS - remover pontos com valor 0
    rds_data = comparativo[comparativo['valor_total'] > 0]
    fig_comparativo.add_trace(go.Scatter(
        x=rds_data['data_dt'], 
        y=rds_data['valor_total'],
        mode='lines+markers',
        name='Faturamento RDS (R$)',
        line=dict(color='blue', width=3),
        yaxis='y1',
        connectgaps=False  # Não conectar lacunas
    ))
    
    # Linha Chart - remover pontos com valor 0
    chart_data = comparativo[comparativo['valor'] > 0]
    fig_comparativo.add_trace(go.Scatter(
        x=chart_data['data_dt'], 
        y=chart_data['valor'],
        mode='lines+markers',
        name='Total Reservas Chart',
        line=dict(color='red', width=3),
        yaxis='y2',
        connectgaps=False  # Não conectar lacunas
    ))
    
    fig_comparativo.update_layout(
        title='Comparativo: Faturamento RDS vs Total de Reservas Chart',
        xaxis_title='Data',
        yaxis=dict(title='Faturamento RDS (R$)', side='left', color='blue'),
        yaxis2=dict(title='Total Reservas Chart', side='right', overlaying='y', color='red'),
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_comparativo, use_container_width=True)
    
except Exception as e:
    st.error(f"Erro ao criar gráfico comparativo: {str(e)}")

conn.close()
