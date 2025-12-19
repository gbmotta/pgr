"""
Script de Testes - Sistema PGR em Produção
Testa todos os endpoints da API online
"""
import requests
import json
from datetime import datetime

# ========================================
# CONFIGURAÇÃO
# ========================================
# Altere para a URL do seu deploy no Railway
API_URL = input("Digite a URL do Railway (ex: https://pgr-production-xxx.up.railway.app): ").strip()

if not API_URL.startswith('http'):
    API_URL = 'https://' + API_URL

print(f"\n{'='*60}")
print(f"🧪 TESTANDO API EM PRODUÇÃO")
print(f"{'='*60}")
print(f"URL: {API_URL}\n")


# ========================================
# TESTES
# ========================================

def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Executa um teste em um endpoint"""
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        status_ok = response.status_code == expected_status
        icon = "✅" if status_ok else "❌"
        
        print(f"{icon} {name}")
        print(f"   {method} {endpoint}")
        print(f"   Status: {response.status_code} (esperado: {expected_status})")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
                print(f"   Resposta: {json.dumps(data, indent=2)[:200]}...")
            except:
                pass
        elif not status_ok:
            print(f"   Erro: {response.text[:200]}")
        
        print()
        return status_ok, response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}")
        print(f"   ERRO: Não foi possível conectar ao servidor")
        print(f"   Verifique se a URL está correta e o deploy foi concluído\n")
        return False, None
    except Exception as e:
        print(f"❌ {name}")
        print(f"   ERRO: {str(e)}\n")
        return False, None


print("="*60)
print("1️⃣  TESTES BÁSICOS")
print("="*60 + "\n")

# Teste 1: Health Check
test_endpoint(
    "Health Check",
    "GET",
    "/health"
)

# Teste 2: Documentação
test_endpoint(
    "API Docs (Swagger)",
    "GET",
    "/docs",
    expected_status=200
)

# Teste 3: Frontend
test_endpoint(
    "Frontend Dashboard",
    "GET",
    "/pgr/",
    expected_status=200
)


print("="*60)
print("2️⃣  TESTES DE PROCESSOS")
print("="*60 + "\n")

# Teste 4: Listar Processos
success, response = test_endpoint(
    "Listar Todos os Processos",
    "GET",
    "/processes"
)

if success and response:
    try:
        processes = response.json()
        print(f"   📊 Total de processos: {len(processes)}")
        if processes:
            print(f"   📋 Primeiro processo: {processes[0]['protocol_number']}")
        print()
    except:
        pass

# Teste 5: Filtrar por Tipo
test_endpoint(
    "Filtrar Processos (PROM_CAP)",
    "GET",
    "/processes?type_code=PROM_CAP"
)

# Teste 6: Filtrar por Status
test_endpoint(
    "Filtrar Processos (RECEBIDO)",
    "GET",
    "/processes?status_code=RECEBIDO"
)

# Teste 7: Buscar Processo Específico
test_endpoint(
    "Buscar Processo por Protocolo",
    "GET",
    "/processes/PGR-2025-0001"
)


print("="*60)
print("3️⃣  TESTE DE CADASTRO")
print("="*60 + "\n")

# Teste 8: Criar Novo Processo
new_process_data = {
    "protocol_number": f"PGR-2025-TEST-{datetime.now().strftime('%H%M%S')}",
    "type_code": "PROM_CAP",
    "applicant_name": "Teste Produção",
    "applicant_registration": "999999",
    "created_date": datetime.now().strftime('%Y-%m-%d')
}

success, response = test_endpoint(
    "Criar Novo Processo",
    "POST",
    "/processes",
    data=new_process_data,
    expected_status=201
)

if success and response:
    try:
        created = response.json()
        protocol = created.get('protocol_number')
        print(f"   ✅ Processo criado: {protocol}")
        
        # Teste 9: Buscar o processo recém-criado
        print(f"\n   Verificando processo criado...\n")
        test_endpoint(
            "Buscar Processo Recém-Criado",
            "GET",
            f"/processes/{protocol}"
        )
    except:
        pass


print("="*60)
print("4️⃣  TESTES DE PRAZOS")
print("="*60 + "\n")

# Teste 10: Prazos Vencidos
test_endpoint(
    "Listar Prazos Vencidos",
    "GET",
    "/deadlines/overdue"
)

# Teste 11: Prazos Próximos
test_endpoint(
    "Prazos Próximos (7 dias)",
    "GET",
    "/deadlines/upcoming?days=7"
)


print("="*60)
print("5️⃣  TESTES DE ESTATÍSTICAS")
print("="*60 + "\n")

# Teste 12: Estatísticas
success, response = test_endpoint(
    "Resumo Estatístico",
    "GET",
    "/statistics/summary"
)

if success and response:
    try:
        stats = response.json()
        print(f"   📊 Estatísticas:")
        print(f"      Total de processos: {stats.get('total_processes', 0)}")
        print(f"      Prazos vencidos: {stats.get('overdue_deadlines', 0)}")
        if 'by_status' in stats:
            print(f"      Por status:")
            for status, count in stats['by_status'].items():
                if count > 0:
                    print(f"         {status}: {count}")
        print()
    except:
        pass


print("="*60)
print("📊 RESUMO DOS TESTES")
print("="*60)
print()
print("✅ Se todos os testes passaram, seu sistema está ONLINE e funcionando!")
print()
print("🌐 Acesse o frontend:")
print(f"   {API_URL}/pgr/")
print()
print("📚 Documentação interativa (Swagger):")
print(f"   {API_URL}/docs")
print()
print("💡 Compartilhe a URL com seu cliente:")
print(f"   {API_URL}/pgr/")
print()
print("="*60)
