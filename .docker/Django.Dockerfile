FROM python:3.12-slim as base

# Impedir que o Python gere arquivos .pyc e garantir log em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
	gcc \
	curl \
	git \
	procps \
	gettext \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN echo 'alias dj="python /workspace/src/manage.py"' >> ~/.bashrc

# --- Estágio de Desenvolvimento ---
FROM base as development
COPY src/ .
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]

# --- Estágio de Produção ---
FROM base as production
COPY src/ .
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "src", "core.wsgi:application"]
