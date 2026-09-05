# LensRAG API image. Deliberately light: the heavy ML extras (bge/colpali) are NOT
# installed — generation uses the Gemini REST API + the offline mock, so the image
# stays small and boots fast. Enable [colpali]/[bge] on a GPU host if desired.
FROM python:3.12-slim

WORKDIR /app

# Editable install keeps app/ and data/ in their source layout, so the eval summary
# and corpus resolve relative to the backend dir at runtime. [postgres] adds the
# asyncpg driver used in production.
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir -e ".[postgres]"

COPY data ./data

ENV LENSRAG_STORAGE_DIR=/app/storage \
    PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
