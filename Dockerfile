FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    PORT=8080

WORKDIR /app

COPY requirements.deploy.txt ./
RUN pip install --no-cache-dir -r requirements.deploy.txt

COPY local_web_calculator.py ./
COPY m-johnson2-aqueous-outflow-8fb729748300_Modified/offline/ \
     m-johnson2-aqueous-outflow-8fb729748300_Modified/offline/

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["python", "local_web_calculator.py"]
