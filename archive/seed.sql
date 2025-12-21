-- Dados iniciais: tipos de processo, status, documentos e prazos legais

-- Tipos de processo
INSERT OR IGNORE INTO process_types (code, name, description) VALUES
('PROM_CAP','Promoção por Capacitação Profissional','Promoção baseada em títulos e cursos de capacitação'),
('PROG_MER','Progressão por Mérito Profissional','Progressão baseada em avaliação de desempenho');

-- Status
INSERT OR IGNORE INTO statuses (code, label) VALUES
('RECEBIDO','Recebido'),
('EM_ANALISE','Em Análise'),
('PENDENTE_DOCS','Pendente - Documentação'),
('COMPLETO','Completo'),
('DEFERIDO','Deferido'),
('INDEFERIDO','Indeferido'),
('CANCELADO','Cancelado');

-- Documentos
INSERT OR IGNORE INTO documents (code, name, description) VALUES
('RG','Documento de Identificação (RG)','Cópia do RG'),
('CPF','CPF','Cópia do CPF'),
('CERT_CURSO','Certificado de Curso','Certificado de capacitação'),
('DIPLOMA','Diploma','Diploma de graduação ou pós'),
('DECL_CHEFIA','Declaração da Chefia','Declaração do superior imediato'),
('FICHA_AVAL','Ficha de Avaliação de Desempenho','Avaliação de desempenho do último período'),
('HIST_FUNC','Histórico Funcional','Cópia da vida funcional do servidor');

-- Documentos obrigatórios: Promoção por Capacitação
INSERT OR IGNORE INTO required_documents (type_id, document_id, required, doc_order)
SELECT t.id, d.id, 1, 1 FROM process_types t, documents d WHERE t.code='PROM_CAP' AND d.code='RG';
INSERT OR IGNORE INTO required_documents (type_id, document_id, required, doc_order)
SELECT t.id, d.id, 1, 2 FROM process_types t, documents d WHERE t.code='PROM_CAP' AND d.code='CPF';
INSERT OR IGNORE INTO required_documents (type_id, document_id, required, doc_order)
SELECT t.id, d.id, 1, 3 FROM process_types t, documents d WHERE t.code='PROM_CAP' AND d.code='CERT_CURSO';
INSERT OR IGNORE INTO required_documents (type_id, document_id, required, doc_order)
SELECT t.id, d.id, 1, 4 FROM process_types t, documents d WHERE t.code='PROM_CAP' AND d.code='DECL_CHEFIA';

-- Documentos obrigatórios: Progressão por Mérito
INSERT OR IGNORE INTO required_documents (type_id, document_id, required, doc_order)
SELECT t.id, d.id, 1, 1 FROM process_types t, documents d WHERE t.code='PROG_MER' AND d.code='RG';
INSERT OR IGNORE INTO required_documents (type_id, document_id, required, doc_order)
SELECT t.id, d.id, 1, 2 FROM process_types t, documents d WHERE t.code='PROG_MER' AND d.code='CPF';
INSERT OR IGNORE INTO required_documents (type_id, document_id, required, doc_order)
SELECT t.id, d.id, 1, 3 FROM process_types t, documents d WHERE t.code='PROG_MER' AND d.code='FICHA_AVAL';
INSERT OR IGNORE INTO required_documents (type_id, document_id, required, doc_order)
SELECT t.id, d.id, 1, 4 FROM process_types t, documents d WHERE t.code='PROG_MER' AND d.code='HIST_FUNC';

-- Prazos legais
INSERT OR IGNORE INTO legal_deadlines (type_id, name, days_limit, start_event, is_business_days, description)
VALUES (NULL, 'Prazo para instrução inicial', 30, 'created_date', 0, 'Prazo padrão para instrução do processo');

INSERT OR IGNORE INTO legal_deadlines (type_id, name, days_limit, start_event, is_business_days, description)
SELECT t.id, 'Análise técnica de mérito', 45, 'created_date', 0, 'Prazo para análise técnica'
FROM process_types t WHERE t.code='PROG_MER';

INSERT OR IGNORE INTO legal_deadlines (type_id, name, days_limit, start_event, is_business_days, description)
SELECT t.id, 'Análise de capacitação', 30, 'created_date', 0, 'Prazo para análise de certificados'
FROM process_types t WHERE t.code='PROM_CAP';

INSERT OR IGNORE INTO legal_deadlines (type_id, name, days_limit, start_event, is_business_days, description)
VALUES (NULL, 'Prazo para complementação documental', 15, 'created_date', 1, 'Prazo para apresentar documentos faltantes');
