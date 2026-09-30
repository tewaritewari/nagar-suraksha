# Nagar Suraksha MVP

Civic reporting MVP for suspected illegal-liquor/drug-related activity. Reports remain unverified until authorised review.

## Run backend
```bash
docker compose up --build
```
API: http://localhost:8000/docs

## Demo
POST `/reports` with JSON containing category, description, latitude, longitude.
GET `/reports/public` returns privacy-safe public reports.
GET `/reports/admin` returns reports for authorised dashboard use (MVP header auth).
PATCH `/reports/{id}/status` updates workflow status.
GET `/hotspots` returns simple spatial clusters.
