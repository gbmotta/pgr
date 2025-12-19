"""
Testes automatizados da API usando pytest.
"""
import os
import subprocess
import sys
from fastapi.testclient import TestClient

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api import app

client = TestClient(app)

def setup_module(module):
    """Recria o banco antes dos testes."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    script = os.path.join(base_dir, 'create_db.py')
    subprocess.check_call(['python3', script])

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_list_process_types():
    response = client.get("/process-types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    codes = [t['code'] for t in data]
    assert 'PROM_CAP' in codes
    assert 'PROG_MER' in codes

def test_list_statuses():
    response = client.get("/statuses")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5

def test_list_processes():
    response = client.get("/processes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_process_details():
    response = client.get("/processes/PGR-2025-0001")
    assert response.status_code == 200
    proc = response.json()
    assert proc['protocol_number'] == 'PGR-2025-0001'
    assert 'documents' in proc
    assert 'deadlines' in proc
    assert len(proc['documents']) >= 1
    assert any(d['required'] for d in proc['documents'])

def test_provide_document():
    response = client.post(
        "/processes/PGR-2025-0001/documents/RG/provide",
        json={"provided_date": "2025-12-10"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['document_code'] == 'RG'

def test_list_overdue_deadlines():
    response = client.get("/deadlines/overdue")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_list_upcoming_deadlines():
    response = client.get("/deadlines/upcoming?days=30")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
