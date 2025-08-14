FROM python:3.12-slim

WORKDIR /app

# 安裝依賴
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt

COPY . .


EXPOSE 8888


# Run with python
CMD ["python", "main.py"]
