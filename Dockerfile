FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the Space-friendly port
ENV PORT 7860
EXPOSE 7860

# Use the PORT env var at runtime
CMD ["sh","-c","uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
