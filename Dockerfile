FROM python:3.11.18-slim
WORKDIR /app
RUN mkdir -p /app/data
COPY app.py .
CMD ["python", "app.py"]