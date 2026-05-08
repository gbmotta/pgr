#!/usr/bin/env python3
"""
Diagramas de arquitetura PGR com o pacote ``diagrams`` (mingrammer/diagrams).

Requisitos:
  pip install diagrams
  Graphviz instalado no sistema (pacote ``graphviz`` / ``dot`` no PATH).

Execução (a partir deste diretório):
  python3 architecture_diagrams.py

Saída:
  pgr_fluxo_geral.png / pgr_fluxo_detalhado.png (formato por defeito do diagrams).
"""
from __future__ import annotations

from pathlib import Path

from diagrams import Diagram, Cluster, Edge

# Ícones disponíveis em https://diagrams.mingrammer.com/docs/nodes/onprem
from diagrams.generic.blank import Blank
from diagrams.onprem.client import Client
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python


HERE = Path(__file__).resolve().parent
OUT_DIR = HERE


def build_general() -> None:
    graph_attr = {"fontsize": "11", "bgcolor": "white"}
    with Diagram(
        "PGR_fluxo_geral",
        filename=str(OUT_DIR / "pgr_fluxo_geral"),
        show=False,
        direction="LR",
        graph_attr=graph_attr,
    ):
        user = Client("Utilizador\n(browser)")
        with Cluster("Frontend"):
            spa = Blank("React + Vite\n(TypeScript/JS)")
        with Cluster("Backend"):
            api = FastAPI("FastAPI\n(api_sqlalchemy)")
            svc = Python("Serviços\n(auth, sheets, drive)")
        db = Blank("SQLite\n(data/PGR.db)")
        drive = Blank("Google Drive\nSheets API")

        user >> Edge(label="HTTPS") >> spa
        spa >> Edge(label="/api, JWT") >> api
        api >> Edge(label="ORM") >> svc
        svc >> db
        svc >> Edge(label="opcional") >> drive


def build_detailed() -> None:
    graph_attr = {"fontsize": "10", "bgcolor": "white"}
    with Diagram(
        "PGR_fluxo_detalhado",
        filename=str(OUT_DIR / "pgr_fluxo_detalhado"),
        show=False,
        direction="TB",
        graph_attr=graph_attr,
    ):
        user = Client("Browser")

        with Cluster("frontend-react"):
            rq = Blank("React Query")
            pages = Blank("Páginas:\ndashboard, upload,\ncalendar, reports…")
            auth_ctx = Blank("AuthContext\nJWT localStorage")
            rq >> pages
            auth_ctx >> rq

        with Cluster("FastAPI api_sqlalchemy"):
            routes = Blank("Rotas REST\n/processes /api/*\n/deadlines /statistics")
            deps = Blank("Depends(auth)\nMulti-tenant\nowner_user_id")
            routes >> deps

        with Cluster("Serviços backend"):
            ingest = Python("ingestion\nspreadsheet_ingestion")
            sheets = Python("sheets_service\nwebhook_handler")
            drive = Python("drive_service\ngoogle_drive_utils")
            dl = Python("deadline_awareness\nalert_service")
            audit = Python("audit_service")

        with Cluster("Persistência"):
            orm = Blank("SQLAlchemy\nmodels_sqlalchemy")
            sqlite = Blank("SQLite +\npasta uploads/")

        ext = Blank("Google APIs\n(Drive / Sheets)")

        user >> Edge(label=":3000 dev\nou /assets prod") >> pages
        pages >> Edge(label="axios") >> routes
        deps >> ingest
        deps >> sheets
        deps >> drive
        deps >> dl
        deps >> audit
        ingest >> orm
        sheets >> orm
        drive >> orm
        dl >> orm
        audit >> orm
        orm >> sqlite
        sheets >> Edge(label="watch") >> ext
        drive >> Edge(label="ficheiros") >> ext


if __name__ == "__main__":
    build_general()
    build_detailed()
    print(f"Diagramas gravados em: {OUT_DIR}")
