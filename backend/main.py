import os
import shutil
import subprocess
import tempfile
import logging
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Configuración de logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Conversor Office a PDF", version="1.0.0")

# CORS dinámico: en producción restringir a tu dominio real
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← Permite TODOS los orígenes durante desarrollo
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {
        "message": "Conversor PDF API",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

# Compresión gzip para respuestas grandes
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Constantes unificadas
ALLOWED_EXTS = {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp", ".rtf"}
ALLOWED_MIMES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.presentation",
    "application/rtf",
    "application/octet-stream",  # fallback para algunos navegadores
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@app.get("/health")
async def health_check():
    """Endpoint para monitoreo y evitar sleep en Render free tier"""
    try:
        result = subprocess.run(
            ["libreoffice", "--version"],
            capture_output=True, text=True, timeout=10
        )
        lo_version = result.stdout.strip().split("\n")[0] if result.returncode == 0 else "not found"
        return JSONResponse({"status": "ok", "libreoffice": lo_version})
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=503)


from fastapi.responses import Response  # ← Asegúrate de tener este import arriba


@app.post("/convert")
async def convert_to_pdf(file: UploadFile):
    if not file.filename:
        raise HTTPException(400, detail="El archivo no tiene nombre")

    ext = os.path.splitext(file.filename)[1].lower()
    base_name = os.path.splitext(file.filename)[0]

    logger.info(f"📥 Recibido: {file.filename} | Ext: {ext}")

    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, detail=f"Extensión '{ext}' no soportada")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, detail="Archivo > 50 MB")

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file.filename)  # Nombre original

    try:
        # 1. Guardar archivo subido
        with open(input_path, "wb") as f:
            f.write(content)

        # 2. Ejecutar LibreOffice
        result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_path],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            logger.error(f"❌ LibreOffice: {result.stderr[:200]}")
            raise HTTPException(500, detail="Error en conversión")

        # 3. Buscar el PDF generado (LibreOffice usa: nombre_original.pdf)
        expected_pdf = f"{base_name}.pdf"
        pdf_path = os.path.join(temp_dir, expected_pdf)

        # Fallback: buscar cualquier .pdf si el nombre no coincide
        if not os.path.exists(pdf_path):
            pdf_files = [f for f in os.listdir(temp_dir) if f.endswith(".pdf")]
            if not pdf_files:
                raise HTTPException(500, detail="LibreOffice no generó PDF")
            pdf_path = os.path.join(temp_dir, pdf_files[0])
            logger.info(f"🔍 PDF encontrado: {pdf_files[0]}")

        # 4. ⚠️ CLAVE: Leer a memoria ANTES de borrar temp_dir
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        logger.info(f"✅ PDF leído a memoria ({len(pdf_bytes)} bytes)")

        # 5. Devolver como Response (sin depender del sistema de archivos)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{os.path.basename(pdf_path)}"',
                "X-Converted-From": file.filename
            }
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(504, detail="Timeout en conversión")
    except Exception as e:
        logger.exception(f"💥 Error: {e}")
        raise HTTPException(500, detail=str(e))
    finally:
        # 6. Limpiar temp_dir (ya no importa, el PDF está en memoria)
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)