# ໃຊ້ Python Image ທີ່ເບົາ
FROM python:3.10-slim

# ຕັ້ງຄ່າ Working Directory
WORKDIR /app

# ຕິດຕັ້ງ System Dependencies ທີ່ຈຳເປັນ (ບາງເທື່ອ psycopg2 ຕ້ອງການ)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements ແລະ ຕິດຕັ້ງ
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Code ທັງໝົດເຂົ້າ Container
COPY . .

# Cloud Run ຈະສົ່ງ PORT ມາໃຫ້ຜ່ານ Environment Variable (Default 8080)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}