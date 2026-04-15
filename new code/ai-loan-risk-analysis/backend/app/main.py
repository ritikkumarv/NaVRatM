from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.verify_user import router as verify_user_router

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"

app = FastAPI(
    title="AI Loan Risk Analysis API",
    version="1.0.0",
    description="Minimal backend for loan verification and risk analysis workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict):
                operation.get("responses", {}).pop("422", None)

    components = openapi_schema.get("components", {})
    schemas = components.get("schemas", {})
    schemas.pop("HTTPValidationError", None)
    schemas.pop("ValidationError", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(verify_user_router)

if FRONTEND_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="assets")


@app.get("/", include_in_schema=False)
def read_root():
    if FRONTEND_DIST_DIR.exists():
        return FileResponse(FRONTEND_DIST_DIR / "index.html")
    return {"message": "Frontend build not found. Run the frontend build first."}


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    if full_path.startswith(("verify-user", "health", "docs", "openapi.json", "redoc", "assets")):
        return {"detail": "Not Found"}

    target_file = FRONTEND_DIST_DIR / full_path
    if target_file.is_file():
        return FileResponse(target_file)

    if FRONTEND_DIST_DIR.exists():
        return FileResponse(FRONTEND_DIST_DIR / "index.html")

    return {"message": "Frontend build not found. Run the frontend build first."}
