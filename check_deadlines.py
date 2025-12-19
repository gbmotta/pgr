#!/usr/bin/env python3
"""
Script para processar arquivo processos.csv:
- Calcula dias restantes com base na data limite
- Marca processos vencidos
- Gera novo CSV com alertas

Uso:
    python3 check_deadlines.py processos.csv
    python3 check_deadlines.py processos.csv --output alertas.csv
"""

import csv
import sys
import argparse
from datetime import datetime, date
from typing import List, Dict

def parse_date(date_str: str) -> date:
    """Converte string de data em objeto date."""
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
    except ValueError:
        try:
            # Tenta formato DD/MM/YYYY
            return datetime.strptime(date_str.strip(), '%d/%m/%Y').date()
        except ValueError:
            return None

def calculate_days_remaining(deadline: date, reference_date: date = None) -> int:
    """Calcula dias restantes até a data limite."""
    if not deadline:
        return None
    if reference_date is None:
        reference_date = date.today()
    delta = deadline - reference_date
    return delta.days

def get_alert_level(days_remaining: int) -> str:
    """Determina nível de alerta baseado nos dias restantes."""
    if days_remaining is None:
        return "SEM_PRAZO"
    elif days_remaining < 0:
        return "VENCIDO"
    elif days_remaining == 0:
        return "VENCE_HOJE"
    elif days_remaining <= 3:
        return "URGENTE"
    elif days_remaining <= 7:
        return "ATENCAO"
    elif days_remaining <= 15:
        return "PROXIMO"
    else:
        return "NORMAL"

def get_alert_message(alert_level: str, days_remaining: int) -> str:
    """Gera mensagem de alerta apropriada."""
    if alert_level == "SEM_PRAZO":
        return "ℹ️ Sem prazo definido"
    
    if days_remaining is None:
        return "ℹ️ Sem prazo definido"
    
    messages = {
        "VENCIDO": f"⚠️ VENCIDO há {abs(days_remaining)} dia(s)",
        "VENCE_HOJE": "🔴 VENCE HOJE",
        "URGENTE": f"🔴 Urgente: {days_remaining} dia(s) restante(s)",
        "ATENCAO": f"🟡 Atenção: {days_remaining} dia(s) restante(s)",
        "PROXIMO": f"🟢 Próximo: {days_remaining} dia(s) restante(s)",
        "NORMAL": f"✅ Normal: {days_remaining} dia(s) restante(s)"
    }
    return messages.get(alert_level, "")

def process_csv(input_file: str, output_file: str = None, reference_date: date = None):
    """
    Processa CSV de processos e gera arquivo com alertas.
    
    Args:
        input_file: Caminho do arquivo CSV de entrada
        output_file: Caminho do arquivo CSV de saída (padrão: processos_com_alertas.csv)
        reference_date: Data de referência para cálculo (padrão: hoje)
    """
    if output_file is None:
        output_file = input_file.replace('.csv', '_com_alertas.csv')
    
    if reference_date is None:
        reference_date = date.today()
    
    print(f"Processando: {input_file}")
    print(f"Data de referência: {reference_date.strftime('%d/%m/%Y')}")
    print("-" * 80)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            
            # Verificar se tem as colunas necessárias
            if 'data_limite' not in reader.fieldnames and 'deadline' not in reader.fieldnames:
                print("⚠️ Aviso: CSV não contém coluna 'data_limite' ou 'deadline'")
                print("Colunas encontradas:", reader.fieldnames)
                return
            
            # Preparar fieldnames de saída
            output_fieldnames = list(reader.fieldnames) + [
                'dias_restantes',
                'nivel_alerta',
                'mensagem_alerta',
                'vencido'
            ]
            
            rows_processed = []
            stats = {
                'total': 0,
                'vencidos': 0,
                'urgentes': 0,
                'atencao': 0,
                'proximos': 0,
                'normais': 0,
                'sem_prazo': 0
            }
            
            for row in reader:
                stats['total'] += 1
                
                # Identificar coluna de data limite
                deadline_str = row.get('data_limite') or row.get('deadline') or ''
                deadline = parse_date(deadline_str)
                
                # Calcular dias restantes
                days_remaining = calculate_days_remaining(deadline, reference_date)
                
                # Determinar nível de alerta
                alert_level = get_alert_level(days_remaining)
                alert_message = get_alert_message(alert_level, days_remaining)
                
                # Atualizar estatísticas
                if alert_level == 'VENCIDO':
                    stats['vencidos'] += 1
                elif alert_level == 'URGENTE' or alert_level == 'VENCE_HOJE':
                    stats['urgentes'] += 1
                elif alert_level == 'ATENCAO':
                    stats['atencao'] += 1
                elif alert_level == 'PROXIMO':
                    stats['proximos'] += 1
                elif alert_level == 'NORMAL':
                    stats['normais'] += 1
                else:
                    stats['sem_prazo'] += 1
                
                # Adicionar novos campos
                row['dias_restantes'] = days_remaining if days_remaining is not None else ''
                row['nivel_alerta'] = alert_level
                row['mensagem_alerta'] = alert_message
                row['vencido'] = 'SIM' if alert_level == 'VENCIDO' else 'NÃO'
                
                rows_processed.append(row)
                
                # Mostrar processos problemáticos
                if alert_level in ['VENCIDO', 'VENCE_HOJE', 'URGENTE']:
                    protocol = row.get('protocol_number') or row.get('protocolo') or f"Linha {stats['total']}"
                    print(f"{alert_message} - {protocol}")
        
        # Escrever arquivo de saída
        with open(output_file, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(rows_processed)
        
        # Mostrar estatísticas
        print("\n" + "=" * 80)
        print("RESUMO DO PROCESSAMENTO")
        print("=" * 80)
        print(f"Total de processos: {stats['total']}")
        print(f"  🔴 Vencidos: {stats['vencidos']}")
        print(f"  🔴 Urgentes: {stats['urgentes']}")
        print(f"  🟡 Atenção: {stats['atencao']}")
        print(f"  🟢 Próximos: {stats['proximos']}")
        print(f"  ✅ Normais: {stats['normais']}")
        print(f"  ℹ️ Sem prazo: {stats['sem_prazo']}")
        print(f"\nArquivo gerado: {output_file}")
        print("=" * 80)
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo '{input_file}' não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Processa CSV de processos e gera alertas de prazos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 check_deadlines.py processos.csv
  python3 check_deadlines.py processos.csv --output alertas.csv
  python3 check_deadlines.py processos.csv --date 2025-12-25

O CSV de entrada deve conter uma coluna 'data_limite' ou 'deadline' no formato YYYY-MM-DD ou DD/MM/YYYY.
        """
    )
    
    parser.add_argument('input', help='Arquivo CSV de entrada')
    parser.add_argument('-o', '--output', help='Arquivo CSV de saída (padrão: <input>_com_alertas.csv)')
    parser.add_argument('-d', '--date', help='Data de referência (formato YYYY-MM-DD, padrão: hoje)')
    
    args = parser.parse_args()
    
    # Processar data de referência
    reference_date = None
    if args.date:
        reference_date = parse_date(args.date)
        if not reference_date:
            print(f"❌ Erro: Data inválida '{args.date}'. Use formato YYYY-MM-DD")
            sys.exit(1)
    
    # Processar CSV
    process_csv(args.input, args.output, reference_date)

if __name__ == '__main__':
    main()
