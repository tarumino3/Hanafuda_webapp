# ベースとなる公式Pythonイメージを指定
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends gcc
RUN useradd -m appuser
COPY --chown=appuser:appuser requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=$PORT", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]