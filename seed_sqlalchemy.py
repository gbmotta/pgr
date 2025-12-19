#!/usr/bin/env python3
"""
Script para popular o banco de dados SQLAlchemy com dados iniciais.
Cria tipos de processo, status, documentos e prazos legais.
"""
import models_sqlalchemy as models
from datetime import date

def seed_database():
    """
    Popula o banco com dados iniciais necessários para o sistema funcionar.
    """
    print("Iniciando seed do banco de dados...")
    
    # Criar engine e sessão
    engine = models.get_engine()
    models.create_tables(engine)
    db = models.get_session(engine)
    
    try:
        # ============ 1. Tipos de Processo ============
        print("Criando tipos de processo...")
        
        # Verificar se já existem
        prom_cap = db.query(models.ProcessType).filter_by(code="PROM_CAP").first()
        if not prom_cap:
            prom_cap = models.ProcessType(
                code="PROM_CAP",
                name="Promoção por Capacitação Profissional",
                description="Promoção baseada em títulos e cursos de capacitação"
            )
            db.add(prom_cap)
        
        prog_mer = db.query(models.ProcessType).filter_by(code="PROG_MER").first()
        if not prog_mer:
            prog_mer = models.ProcessType(
                code="PROG_MER",
                name="Progressão por Mérito Profissional",
                description="Progressão baseada em avaliação de desempenho"
            )
            db.add(prog_mer)
        
        db.commit()
        db.refresh(prom_cap)
        db.refresh(prog_mer)
        
        # ============ 2. Status ============
        print("Criando status...")
        
        statuses_data = [
            ("RECEBIDO", "Recebido"),
            ("EM_ANALISE", "Em Análise"),
            ("PENDENTE_DOCS", "Pendente - Documentação"),
            ("COMPLETO", "Completo"),
            ("DEFERIDO", "Deferido"),
            ("INDEFERIDO", "Indeferido"),
            ("CANCELADO", "Cancelado")
        ]
        
        status_objs = {}
        for code, label in statuses_data:
            status = db.query(models.Status).filter_by(code=code).first()
            if not status:
                status = models.Status(code=code, label=label)
                db.add(status)
            status_objs[code] = status
        
        db.commit()
        
        # ============ 3. Documentos ============
        print("Criando catálogo de documentos...")
        
        docs_data = [
            ("RG", "Documento de Identificação (RG)", "Cópia do RG"),
            ("CPF", "CPF", "Cópia do CPF"),
            ("CERT_CURSO", "Certificado de Curso", "Certificado de capacitação"),
            ("DIPLOMA", "Diploma", "Diploma de graduação ou pós"),
            ("DECL_CHEFIA", "Declaração da Chefia", "Declaração do superior imediato"),
            ("FICHA_AVAL", "Ficha de Avaliação de Desempenho", "Avaliação de desempenho do último período"),
            ("HIST_FUNC", "Histórico Funcional", "Cópia da vida funcional do servidor")
        ]
        
        doc_objs = {}
        for code, name, desc in docs_data:
            doc = db.query(models.Document).filter_by(code=code).first()
            if not doc:
                doc = models.Document(code=code, name=name, description=desc)
                db.add(doc)
            doc_objs[code] = doc
        
        db.commit()
        
        # Refresh para pegar IDs
        for doc in doc_objs.values():
            db.refresh(doc)
        
        # ============ 4. Documentos Obrigatórios por Tipo ============
        print("Configurando documentos obrigatórios...")
        
        # Promoção por Capacitação: RG, CPF, CERT_CURSO, DECL_CHEFIA
        prom_cap_docs = ["RG", "CPF", "CERT_CURSO", "DECL_CHEFIA"]
        for i, doc_code in enumerate(prom_cap_docs, start=1):
            req_doc = models.RequiredDocument(
                type_id=prom_cap.id,
                document_id=doc_objs[doc_code].id,
                required=True,
                doc_order=i
            )
            db.add(req_doc)
        
        # Progressão por Mérito: RG, CPF, FICHA_AVAL, HIST_FUNC
        prog_mer_docs = ["RG", "CPF", "FICHA_AVAL", "HIST_FUNC"]
        for i, doc_code in enumerate(prog_mer_docs, start=1):
            req_doc = models.RequiredDocument(
                type_id=prog_mer.id,
                document_id=doc_objs[doc_code].id,
                required=True,
                doc_order=i
            )
            db.add(req_doc)
        
        db.commit()
        
        # ============ 5. Prazos Legais ============
        print("Criando prazos legais...")
        
        # Prazo geral: 30 dias corridos para instrução inicial
        prazo_geral = models.LegalDeadline(
            type_id=None,  # Aplica a todos os tipos
            name="Prazo para instrução inicial",
            days_limit=30,
            start_event="created_date",
            is_business_days=False,
            description="Prazo padrão para instrução do processo"
        )
        db.add(prazo_geral)
        
        # Prazo específico para Progressão: 45 dias para análise técnica
        prazo_prog = models.LegalDeadline(
            type_id=prog_mer.id,
            name="Análise técnica de mérito",
            days_limit=45,
            start_event="created_date",
            is_business_days=False,
            description="Prazo para análise técnica"
        )
        db.add(prazo_prog)
        
        # Prazo específico para Promoção: 30 dias para análise de capacitação
        prazo_prom = models.LegalDeadline(
            type_id=prom_cap.id,
            name="Análise de capacitação",
            days_limit=30,
            start_event="created_date",
            is_business_days=False,
            description="Prazo para análise de certificados"
        )
        db.add(prazo_prom)
        
        # Prazo para complementação: 15 dias úteis
        prazo_compl = models.LegalDeadline(
            type_id=None,
            name="Prazo para complementação documental",
            days_limit=15,
            start_event="created_date",
            is_business_days=True,
            description="Prazo para apresentar documentos faltantes"
        )
        db.add(prazo_compl)
        
        db.commit()
        
        # ============ 6. Processos de Exemplo ============
        print("Criando processos de exemplo...")
        
        # Verificar se já existem processos
        existing_count = db.query(models.Process).count()
        if existing_count > 0:
            print(f"  ⏭️  {existing_count} processos já existem. Pulando criação de exemplos.")
        else:
            # Processo 1: Promoção por Capacitação (Recebido)
            proc1 = models.Process(
                protocol_number="PGR-2025-0001",
                type_id=prom_cap.id,
                    applicant_name="João Silva Santos",
                applicant_registration="123456",
                created_date=date(2025, 12, 1),
                status_id=status_objs["RECEBIDO"].id,
                notes="Aguardando certificado"
            )
            db.add(proc1)
            
            # Processo 2: Progressão por Mérito (Em Análise)
            proc2 = models.Process(
                protocol_number="PGR-2025-0002",
                type_id=prog_mer.id,
                applicant_name="Maria Oliveira Costa",
                applicant_registration="789012",
                created_date=date(2025, 11, 15),
                status_id=status_objs["EM_ANALISE"].id,
                parecer="Análise preliminar favorável",
                financial_effective_date=date(2026, 1, 1),
                notes="Requer parecer da chefia"
            )
            db.add(proc2)
            
            # Processo 3: Promoção por Capacitação (Deferido)
            proc3 = models.Process(
                protocol_number="PGR-2025-0003",
                type_id=prom_cap.id,
                applicant_name="Carlos Alberto Pereira",
                applicant_registration="345678",
                created_date=date(2025, 10, 20),
                status_id=status_objs["DEFERIDO"].id,
                parecer="Aprovado conforme critérios técnicos",
                financial_effective_date=date(2025, 12, 1),
                closed_date=date(2025, 12, 5),
                notes="Efeito financeiro retroativo"
            )
            db.add(proc3)
            
            # Processo 4: Progressão por Mérito (Pendente Documentos)
            proc4 = models.Process(
                protocol_number="PGR-2025-0004",
                type_id=prog_mer.id,
                applicant_name="Ana Paula Souza",
                applicant_registration="901234",
                created_date=date(2025, 11, 30),
                status_id=status_objs["PENDENTE_DOCS"].id,
                parecer="Falta ficha de avaliação",
                notes="Notificado em 2025-12-10"
            )
            db.add(proc4)
            
            db.commit()
        
        print("✓ Seed concluído com sucesso!")
        print(f"  - 2 tipos de processo")
        print(f"  - 7 status")
        print(f"  - 7 documentos")
        print(f"  - 4 prazos legais")
        print(f"  - 4 processos de exemplo")
        
    except Exception as e:
        print(f"✗ Erro durante seed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
