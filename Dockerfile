FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002","--reaload"]