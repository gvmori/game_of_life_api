FROM python:3.13

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./main.py /app/
COPY ./lib /app/lib/

RUN groupadd -r app && useradd -r -g app -s /bin/false app \
    && chown -R app:app /app \
    && find /app -type d -exec chmod 0755 {} + \
    && find /app -type f -exec chmod 0644 {} +

USER app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
