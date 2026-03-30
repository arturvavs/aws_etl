FROM python:3.12-slim-bookworm as builder

# Instalar dependências de build e pacotes necessários
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpcre3 \
    libssl-dev \
    libffi-dev \
    curl \
    tzdata && \
    ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    echo "America/Sao_Paulo" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Criar e ativar ambiente virtual
WORKDIR /app
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copiar requirements e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Etapa Final
FROM python:3.12-slim-bookworm

# Copiar o ambiente virtual da etapa de build
COPY --from=builder /app/venv /venv

# Configurar o contêiner
ENV PATH="/venv/bin:$PATH"
WORKDIR /app

# Instalar dependências de build e pacotes necessários
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpcre3 \
    libssl-dev \
    libffi-dev \
    curl \
    tzdata && \
    ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    echo "America/Sao_Paulo" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Adicionar usuário sem privilégios para melhorar a segurança
RUN adduser --disabled-password --gecos '' nonroot && chown -R nonroot:nonroot /app
USER nonroot


# Copiar o código da aplicação
COPY --chown=nonroot:nonroot . .

# Configurar a aplicação
EXPOSE 6019
#HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:6013/health || exit 1

# Iniciar a aplicação
CMD ["python", "main.py"]