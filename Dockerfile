FROM python:3.12-slim

WORKDIR /app

ENV TZ=US/Eastern

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir tzdata

COPY . .

CMD ["python", "-m", "moana"]