#!/usr/bin/env python3
"""Deleta os processos de teste para poder reimportar"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.models_sqlalchemy import get_engine, get_session, Process  # noqa: E402

def delete_test_processes():
    session = get_session(get_engine())
    
    # Deletar processos PGR-2025-08xx (os que acabamos de importar)
    deleted = session.query(Process).filter(
        Process.protocol_number.like('PGR-2025-08%')
    ).delete(synchronize_session=False)
    
    session.commit()
    print(f'✅ {deleted} processos de teste deletados (PGR-2025-08xx)')
    print('📌 Agora você pode reimportar o arquivo Excel com as datas corretas')
    session.close()

if __name__ == "__main__":
    delete_test_processes()
