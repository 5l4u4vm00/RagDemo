FROM python:3.12-slim

WORKDIR /app

# 安裝依賴
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt

# Pre-download embedding model into image so cold starts are fast
ENV HF_HOME=/app/.cache/huggingface
RUN python -c "from transformers import AutoTokenizer, AutoModel; \
    AutoTokenizer.from_pretrained('intfloat/multilingual-e5-large'); \
    AutoModel.from_pretrained('intfloat/multilingual-e5-large')"

COPY . .


EXPOSE 8888


# Run with python
CMD ["python", "main.py"]
