FROM python:3.12-slim

WORKDIR /app

# 安裝依賴
COPY requirement.txt ./
RUN pip install -r requirement.txt

COPY . .


EXPOSE 8888


# Run with uvicorn
CMD ["python", "main.py"]
