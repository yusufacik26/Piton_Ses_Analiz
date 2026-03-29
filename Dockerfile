FROM python:3.10

WORKDIR /app

COPY . .

# ffmpeg gerekli (senin audio processing için)
RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]