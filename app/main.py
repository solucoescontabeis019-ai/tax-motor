"""
FastAPI Application Main - Etapa 2: Motor de Decisão Tributária
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Motor de Decisão Tributária - Simples vs. Híbrido vs. Lucro Real",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Inicializar banco de dados na startup"""
    print("Inicializando banco de dados...")
    init_db()
    print(f"✓ Aplicação iniciada: {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")


@app.get("/")
def read_root():
    """Raiz da API"""
    return {
        "nome": settings.PROJECT_NAME,
        "versao": settings.PROJECT_VERSION,
        "status": "Em desenvolvimento",
        "etapa": "Etapa 2: PostgreSQL Data Model",
    }


@app.get("/health")
def health_check():
    """Health check da aplicação"""
    return {"status": "ok", "projeto": settings.PROJECT_NAME}


# Importar routers aqui quando criados
# from app.api.v1 import api_router
# app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
