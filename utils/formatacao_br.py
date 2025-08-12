import pandas as pd
from datetime import datetime

def formatar_data_br(data_str):
    """
    Converte data para formato brasileiro dd/mm/aaaa
    """
    try:
        if pd.isna(data_str) or data_str == '' or data_str is None:
            return "N/A"
        
        # Se é um objeto datetime, converte diretamente
        if isinstance(data_str, datetime):
            return data_str.strftime('%d/%m/%Y')
        
        # Se já está no formato correto, retorna como está
        if isinstance(data_str, str) and len(data_str) == 10 and '/' in data_str:
            return data_str
        
        # Tenta converter diferentes formatos
        if isinstance(data_str, str):
            try:
                # Formato DD/MM/YYYY
                dt = datetime.strptime(data_str, '%d/%m/%Y')
                return dt.strftime('%d/%m/%Y')
            except:
                try:
                    # Formato YYYY-MM-DD
                    dt = datetime.strptime(data_str, '%Y-%m-%d')
                    return dt.strftime('%d/%m/%Y')
                except:
                    return data_str
        
        return str(data_str)
    except:
        return "N/A"

def formatar_moeda_br(valor):
    """
    Formata valor monetário no padrão brasileiro: R$ 1.234.567,89
    """
    try:
        if pd.isna(valor) or valor == '' or valor is None:
            return "N/A"
        
        valor_float = float(valor)
        
        # Formatação brasileira: ponto para milhares, vírgula para decimais
        valor_formatado = f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return f"R$ {valor_formatado}"
    except:
        return "N/A"

def formatar_numero_br(valor):
    """
    Formata número no padrão brasileiro: 1.234.567
    """
    try:
        if pd.isna(valor) or valor == '' or valor is None:
            return "N/A"
        
        valor_int = int(float(valor))
        
        # Formatação brasileira com pontos para milhares
        return f"{valor_int:,}".replace(',', '.')
    except:
        return "N/A"

def formatar_percentual_br(valor):
    """
    Formata percentual no padrão brasileiro: 12,5%
    """
    try:
        if pd.isna(valor) or valor == '' or valor is None:
            return "N/A"
        
        valor_float = float(valor)
        
        # Formatação brasileira com vírgula para decimais
        valor_formatado = f"{valor_float:.1f}".replace('.', ',')
        
        return f"{valor_formatado}%"
    except:
        return "N/A"
