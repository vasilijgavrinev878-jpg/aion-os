FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aion_engine.py server.py ./
COPY templates/ templates/
COPY static/ static/

ENV PORT=5000
ENV ADMIN_PASSWORD=admin123
ENV SECRET_KEY=change-this-in-production

EXPOSE 5000

CMD ["python", "server.py"]
