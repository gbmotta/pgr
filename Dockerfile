# Build do React → frontend-dist na raiz (ver vite.config.js)
FROM node:20-alpine AS frontend-build
WORKDIR /src/frontend-react
COPY frontend-react/package.json frontend-react/package-lock.json ./
RUN npm ci
COPY frontend-react/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY start_app.py .
COPY --from=frontend-build /src/frontend-dist ./frontend-dist

RUN mkdir -p data uploads reports

EXPOSE 8001
CMD ["python", "start_app.py"]
