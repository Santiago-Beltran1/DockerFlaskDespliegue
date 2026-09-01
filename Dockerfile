# ==========================================
# ETAPA 1: Builder (Compilacion de dependencias)
# ==========================================
FROM python:3.10-alpine AS builder

RUN apk update && apk upgrade --no-cache
RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app

COPY requirements.txt .

# Crear entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Actualizar herramientas en el venv e instalar requerimientos
RUN pip install --no-cache-dir --upgrade pip "setuptools>=79.0.0" "wheel>=0.46.2"
RUN pip install --no-cache-dir -r requirements.txt


# ==========================================
# ETAPA 2: Runtime (Imagen final sin vulnerabilidades)
# ==========================================
FROM python:3.10-alpine AS runner

WORKDIR /app

# 1. Parchear librerías Alpine (libcrypto3/libssl3)
RUN apk update && apk upgrade --no-cache

# 2. ELIMINAR LAS 2 ALERTAS RESTANTES:
# Actualizamos setuptools/wheel directamente en el Python global (/usr/local)
# para que reemplace las versiones vulnerables en setuptools/_vendor/
RUN pip install --no-cache-dir --upgrade "setuptools>=79.0.0" "wheel>=0.46.2"

# 3. Copiar el venv optimizado desde el builder
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 4. Usuario sin privilegios
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]