#!/usr/bin/env python3
"""
Script de teste rápido para verificar que a API SQLAlchemy está funcionando.
Executa testes básicos nos modelos e na API.
"""
import sys
from datetime import date

def test_models():
    """Testa se os modelos SQLAlchemy estão funcionando."""
    print("\n" + "="*60)
    print("TESTE 1: Modelos SQLAlchemy")
    print("="*60)
    
    try:
        import models_sqlalchemy as models
        
        # Criar engine
        print("✓ Import dos modelos OK")
        engine = models.get_engine()
        print("✓ Engine criada OK")
        
        # Criar tabelas
        models.create_tables(engine)
        print("✓ Tabelas criadas OK")
        
        # Criar sessão
        db = models.get_session(engine)
        print("✓ Sessão criada OK")
        
        # Testar query simples
        count = db.query(models.ProcessType).count()
        print(f"✓ Query funcionando (tipos: {count})")
        
        db.close()
        print("\n✅ Teste de modelos PASSOU\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Teste de modelos FALHOU: {str(e)}\n")
        return False


def test_seed():
    """Testa o script de seed."""
    print("="*60)
    print("TESTE 2: Seed do Banco de Dados")
    print("="*60)
    
    try:
        import seed_sqlalchemy
        seed_sqlalchemy.seed_database()
        print("\n✅ Teste de seed PASSOU\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Teste de seed FALHOU: {str(e)}\n")
        return False


def test_queries():
    """Testa queries complexas."""
    print("="*60)
    print("TESTE 3: Queries e Relacionamentos")
    print("="*60)
    
    try:
        import models_sqlalchemy as models
        engine = models.get_engine()
        db = models.get_session(engine)
        
        # Contar registros
        tipos = db.query(models.ProcessType).count()
        status = db.query(models.Status).count()
        docs = db.query(models.Document).count()
        processos = db.query(models.Process).count()
        
        print(f"  Tipos de processo: {tipos}")
        print(f"  Status: {status}")
        print(f"  Documentos: {docs}")
        print(f"  Processos: {processos}")
        
        # Testar relacionamentos
        if processos > 0:
            proc = db.query(models.Process).first()
            print(f"\n  Processo: {proc.protocol_number}")
            print(f"    Tipo: {proc.process_type.name}")
            print(f"    Status: {proc.status.label}")
            print(f"    Documentos: {len(proc.documents)}")
            print(f"    Prazos: {len(proc.deadlines)}")
        
        # Testar query de prazos vencidos
        today = date.today()
        vencidos = db.query(models.ProcessDeadline).filter(
            models.ProcessDeadline.closed == False,
            models.ProcessDeadline.due_date < today
        ).count()
        
        print(f"\n  Prazos vencidos: {vencidos}")
        
        db.close()
        print("\n✅ Teste de queries PASSOU\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Teste de queries FALHOU: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_api_import():
    """Testa se a API pode ser importada."""
    print("="*60)
    print("TESTE 4: Import da API")
    print("="*60)
    
    try:
        import api_sqlalchemy
        print("✓ API importada OK")
        print(f"✓ App criada: {api_sqlalchemy.app.title}")
        print("\n✅ Teste de import da API PASSOU\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Teste de import da API FALHOU: {str(e)}\n")
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "🚀 " + "="*58)
    print("   TESTES DO SISTEMA DE PROCESSOS (SQLAlchemy)")
    print("="*60 + "\n")
    
    results = []
    
    # Executar testes
    results.append(("Modelos", test_models()))
    results.append(("Seed", test_seed()))
    results.append(("Queries", test_queries()))
    results.append(("API Import", test_api_import()))
    
    # Resumo
    print("="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {name:20s} {status}")
    
    print(f"\n  Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.\n")
        print("Para executar a API:")
        print("  python3 api_sqlalchemy.py")
        print("\nOu:")
        print("  uvicorn api_sqlalchemy:app --reload --host 0.0.0.0 --port 8000")
        print("\nDocumentação:")
        print("  http://localhost:8000/docs\n")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
