FROM python:3.12-slim

WORKDIR /app
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 4190

CMD ["python", "outputs/agent-network-server.py"]
