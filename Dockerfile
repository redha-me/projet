FROM python:3.11-slim

WORKDIR /app

COPY webapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "webapp/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
