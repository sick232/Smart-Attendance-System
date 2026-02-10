# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required. For production deployment, implement JWT-based authentication.

---

## Endpoints

### 1. Health Check

**GET** `/`

Check if the API server is running.

**Response:**
```json
{
  "status": "online",
  "system": "Smart Attendance System",
  "version": "1.0.0"
}
```

---

### 2. Register Person

**POST** `/api/register`

Register a new person with face images.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `name` (string, required): Full name of the person
  - `person_id` (string, required): Unique identifier
  - `images` (file[], required): 5-10 face images

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/register \
  -F "name=John Doe" \
  -F "person_id=john_doe_001" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "images=@image3.jpg" \
  -F "images=@image4.jpg" \
  -F "images=@image5.jpg"
```

**Response (Success):**
```json
{
  "success": true,
  "person_id": "john_doe_001",
  "name": "John Doe",
  "confidence": null,
  "is_live": null,
  "has_mask": null,
  "message": "Successfully registered John Doe with 5 face encodings"
}
```

**Response (Error):**
```json
{
  "detail": "Person ID already registered"
}
```

---

### 3. Recognize Face

**POST** `/api/recognize`

Recognize face from uploaded image and mark attendance.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `image` (file, required): Face image

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/recognize \
  -F "image=@face_capture.jpg"
```

**Response (Success - New Attendance):**
```json
{
  "success": true,
  "person_id": "john_doe_001",
  "name": "John Doe",
  "confidence": 0.87,
  "is_live": true,
  "has_mask": false,
  "message": "Attendance marked successfully for John Doe"
}
```

**Response (Already Marked):**
```json
{
  "success": false,
  "person_id": "john_doe_001",
  "name": "John Doe",
  "confidence": 0.89,
  "is_live": true,
  "has_mask": false,
  "message": "Attendance already marked for John Doe today"
}
```

**Response (Not Recognized):**
```json
{
  "success": false,
  "person_id": null,
  "name": null,
  "confidence": null,
  "is_live": true,
  "has_mask": false,
  "message": "Face not recognized"
}
```

**Response (Liveness Failed):**
```json
{
  "success": false,
  "person_id": null,
  "name": null,
  "confidence": null,
  "is_live": false,
  "has_mask": null,
  "message": "Liveness check failed. Please ensure you are a real person."
}
```

---

### 4. Get Attendance Records

**GET** `/api/attendance`

Retrieve attendance records with optional filtering.

**Query Parameters:**
- `start_date` (string, optional): Start date in YYYY-MM-DD format
- `end_date` (string, optional): End date in YYYY-MM-DD format
- `person_id` (string, optional): Filter by person ID

**Example:**
```bash
curl "http://localhost:8000/api/attendance?start_date=2026-02-01&end_date=2026-02-06"
```

**Response:**
```json
[
  {
    "id": 1,
    "person_id": "john_doe_001",
    "name": "John Doe",
    "date": "2026-02-06",
    "time": "09:15:32"
  },
  {
    "id": 2,
    "person_id": "jane_smith_002",
    "name": "Jane Smith",
    "date": "2026-02-06",
    "time": "09:18:45"
  }
]
```

---

### 5. Get All Persons

**GET** `/api/persons`

Get list of all registered persons.

**Example:**
```bash
curl http://localhost:8000/api/persons
```

**Response:**
```json
[
  {
    "person_id": "john_doe_001",
    "name": "John Doe"
  },
  {
    "person_id": "jane_smith_002",
    "name": "Jane Smith"
  }
]
```

---

### 6. Delete Person

**DELETE** `/api/person/{person_id}`

Delete a registered person and their attendance records.

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/person/john_doe_001
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Person john_doe_001 deleted successfully"
}
```

**Response (Not Found):**
```json
{
  "detail": "Person not found"
}
```

---

### 7. Export to CSV

**GET** `/api/export/csv`

Export attendance records to CSV format.

**Query Parameters:**
- `start_date` (string, optional): Start date in YYYY-MM-DD format
- `end_date` (string, optional): End date in YYYY-MM-DD format
- `person_id` (string, optional): Filter by person ID

**Example:**
```bash
curl "http://localhost:8000/api/export/csv?start_date=2026-02-01" \
  --output attendance.csv
```

**Response:**
- Content-Type: `text/csv`
- Downloads CSV file

---

### 8. Export to Excel

**GET** `/api/export/excel`

Export attendance records to Excel format.

**Query Parameters:**
- `start_date` (string, optional): Start date in YYYY-MM-DD format
- `end_date` (string, optional): End date in YYYY-MM-DD format
- `person_id` (string, optional): Filter by person ID

**Example:**
```bash
curl "http://localhost:8000/api/export/excel?start_date=2026-02-01" \
  --output attendance.xlsx
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Downloads Excel file

---

## Error Responses

All endpoints may return standard HTTP error responses:

**400 Bad Request:**
```json
{
  "detail": "Validation error message"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error message"
}
```

---

## Response Fields

### RecognitionResponse
- `success` (boolean): Whether the operation was successful
- `person_id` (string|null): Unique identifier of recognized person
- `name` (string|null): Name of recognized person
- `confidence` (float|null): Recognition confidence score (0.0-1.0)
- `is_live` (boolean|null): Liveness detection result
- `has_mask` (boolean|null): Mask detection result
- `message` (string): Human-readable message

### AttendanceRecord
- `id` (integer): Unique record ID
- `person_id` (string): Person's unique identifier
- `name` (string): Person's name
- `date` (string): Date in YYYY-MM-DD format
- `time` (string): Time in HH:MM:SS format

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:
- Implement rate limiting per IP address
- Add request throttling for resource-intensive endpoints
- Use Redis for distributed rate limiting

---

## CORS

CORS is currently configured to allow all origins (`*`). For production:
- Configure specific allowed origins
- Set appropriate credentials and headers
- Implement proper security policies

---

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to test all endpoints directly from the browser.
