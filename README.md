# Smart Attendance System

A production-ready **Smart Attendance System** using AI-powered Face Recognition with anti-spoofing, mask detection, and real-time performance optimization.

## 🎯 Features

### Core Functionality
- ✅ Real-time face recognition from webcam
- ✅ Fast face detection using OpenCV (HOG/Haar Cascade)
- ✅ Face embeddings using face_recognition library (dlib-based)
- ✅ Euclidean distance-based matching with configurable threshold
- ✅ Duplicate attendance prevention (one entry per day)
- ✅ SQLite database with indexed queries

### Security & Anti-Spoofing
- 🔒 Eye blink detection for liveness verification
- 🔒 Image quality checks (blur detection, color distribution)
- 🔒 Facial landmark-based authentication
- 😷 Optional mask detection support

### Performance
- ⚡ Low latency recognition (<300ms per frame)
- ⚡ Async FastAPI endpoints for concurrent requests
- ⚡ Thread pool execution for CPU-intensive tasks
- ⚡ GPU-ready architecture (auto-fallback to CPU)

### Web Application
- 🌐 Modern React.js frontend with Material-UI
- 🌐 Real-time webcam streaming using WebRTC
- 🌐 Clean dashboard with live feedback
- 🌐 RESTful API with comprehensive endpoints

### Export & Reporting
- 📊 Export to CSV and Excel formats
- 📊 Date-wise and person-wise filtering
- 📊 Real-time attendance statistics

---

## 📁 Project Structure

```
Smart Attendance System/
│
├── backend/
│   ├── main.py                          # FastAPI application
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_manager.py                # Database operations
│   ├── face_recognition/
│   │   ├── __init__.py
│   │   ├── recognizer.py                # Face recognition engine
│   │   ├── anti_spoofing.py             # Liveness detection
│   │   └── mask_detector.py             # Mask detection
│   ├── utils/
│   │   ├── __init__.py
│   │   └── export_utils.py              # CSV/Excel export
│   ├── scripts/
│   │   ├── capture_dataset.py           # Dataset capture tool
│   │   └── train_encodings.py           # Training script
│   ├── models/                          # Saved models & encodings
│   ├── dataset/                         # Training images
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.js                # App layout
│   │   │   └── WebcamCapture.js         # Webcam component
│   │   ├── pages/
│   │   │   ├── Dashboard.js             # Recognition page
│   │   │   ├── Register.js              # Registration page
│   │   │   └── Attendance.js            # Attendance records
│   │   ├── services/
│   │   │   └── api.js                   # API client
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
│
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- Webcam
- (Optional) CUDA-capable GPU for faster processing

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Download dlib shape predictor (optional for advanced anti-spoofing):**
```bash
# Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
# Extract to: backend/models/shape_predictor_68_face_landmarks.dat
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

---

## 📖 Usage

### 1. Capture Dataset

Capture face images for registration:

```bash
cd backend
python scripts/capture_dataset.py <person_name> [num_images]
```

**Example:**
```bash
python scripts/capture_dataset.py john_doe 50
```

**Instructions:**
- Position your face in the frame
- Press **SPACE** for manual capture
- Press **'a'** for auto-capture mode
- Capture from different angles and expressions
- Images are saved to `dataset/person_name/`

### 2. Train Face Encodings

Generate face encodings from captured images:

```bash
python scripts/train_encodings.py [dataset_path] [output_path]
```

**Example:**
```bash
python scripts/train_encodings.py dataset models/face_encodings.pkl
```

This processes all images in the dataset and creates face encodings for recognition.

### 3. Start Backend Server

```bash
cd backend
python main.py
```

Server runs on: `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### 4. Start Frontend Application

```bash
cd frontend
npm start
```

Application opens at: `http://localhost:3000`

---

## 🎮 Using the Application

### Dashboard (Recognition)
1. Navigate to **Dashboard**
2. Position your face in the webcam
3. Click **"Capture Photo"**
4. System will:
   - Detect liveness (anti-spoofing)
   - Detect mask (if present)
   - Recognize face
   - Mark attendance (if not already marked today)

### Register New Person
1. Navigate to **Register**
2. Enter **Full Name** and **Person ID**
3. Capture **5-10 images** from different angles
4. Click **"Register Person"**

**Tips for best results:**
- Good lighting conditions
- Look at different angles
- Vary facial expressions
- Keep face clearly visible

### View Attendance
1. Navigate to **Attendance**
2. Apply filters (date range, person)
3. View attendance records in table
4. Export to CSV or Excel

---

## 🔌 API Endpoints

### Health Check
```http
GET /
```

### Register Person
```http
POST /api/register
Content-Type: multipart/form-data

Parameters:
- name: string (person's full name)
- person_id: string (unique identifier)
- images: file[] (5-10 face images)
```

### Recognize Face
```http
POST /api/recognize
Content-Type: multipart/form-data

Parameters:
- image: file (face image)

Response:
{
  "success": bool,
  "person_id": string,
  "name": string,
  "confidence": float,
  "is_live": bool,
  "has_mask": bool,
  "message": string
}
```

### Get Attendance Records
```http
GET /api/attendance?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&person_id=ID

Response: Array of attendance records
```

### Export CSV
```http
GET /api/export/csv?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&person_id=ID
```

### Export Excel
```http
GET /api/export/excel?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&person_id=ID
```

### Get All Persons
```http
GET /api/persons
```

### Delete Person
```http
DELETE /api/person/{person_id}
```

---

## 🗄️ Database Schema

### Persons Table
```sql
CREATE TABLE persons (
    person_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(person_id, date)
);
```

---

## ⚙️ Configuration

### Backend Configuration

**Face Recognition Threshold** (`backend/face_recognition/recognizer.py`):
```python
threshold: float = 0.6  # Lower = stricter matching (0.0 - 1.0)
```

**Anti-Spoofing Sensitivity** (`backend/face_recognition/anti_spoofing.py`):
```python
ear_threshold: float = 0.25  # Eye Aspect Ratio threshold
```

**Face Detection Model** (`backend/face_recognition/recognizer.py`):
```python
model="hog"  # Options: "hog" (fast), "cnn" (accurate)
```

### Frontend Configuration

**API Base URL** (`frontend/src/services/api.js`):
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

**Webcam Resolution** (`frontend/src/components/WebcamCapture.js`):
```javascript
const videoConstraints = {
  width: 640,
  height: 480,
  facingMode: 'user',
};
```

---

## 🔧 Troubleshooting

### Webcam Not Detected
- Ensure webcam permissions are granted in browser
- Check if webcam is being used by another application
- Try different browsers (Chrome/Edge recommended)

### Low Recognition Accuracy
- Capture more training images (10+ recommended)
- Ensure good lighting during capture and recognition
- Adjust recognition threshold in `recognizer.py`
- Use CNN model instead of HOG for better accuracy

### Liveness Check Failing
- Download shape_predictor_68_face_landmarks.dat for advanced detection
- Ensure face is clearly visible and well-lit
- Adjust EAR threshold in `anti_spoofing.py`

### Slow Performance
- Reduce video resolution
- Use HOG instead of CNN for face detection
- Enable GPU acceleration (CUDA)
- Skip frames during processing

---

## 🚀 Performance Optimization

### For Production:

1. **Use CNN for face detection** (better accuracy):
```python
face_locations = face_recognition.face_locations(rgb_image, model="cnn")
```

2. **Enable GPU** (if available):
```python
# Install dlib with CUDA support
```

3. **Frame skipping** (process every Nth frame):
```python
if frame_count % 3 == 0:  # Process every 3rd frame
    recognize_face(frame)
```

4. **Batch processing** for multiple faces:
```python
face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
```

---

## 🔐 Security Best Practices

1. **Production Deployment:**
   - Use HTTPS for all endpoints
   - Implement authentication (JWT tokens)
   - Configure CORS properly
   - Add rate limiting

2. **Data Protection:**
   - Encrypt face encodings at rest
   - Use secure database connections
   - Implement access controls
   - Regular security audits

3. **Privacy:**
   - Comply with GDPR/local privacy laws
   - Obtain user consent for face data
   - Implement data deletion mechanisms
   - Anonymize exported reports

---

## 📦 Dependencies

### Backend
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `face-recognition` - Face recognition library
- `opencv-python` - Computer vision
- `dlib` - Face landmarks
- `numpy` - Numerical computing
- `pandas` - Data manipulation
- `openpyxl` - Excel export
- `scipy` - Scientific computing

### Frontend
- `react` - UI framework
- `react-router-dom` - Routing
- `@mui/material` - UI components
- `axios` - HTTP client
- `react-webcam` - Webcam integration
- `date-fns` - Date utilities

---

## 📝 License

This project is licensed under the MIT License.

---

## 👥 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Contact: [your-email@example.com]

---

## 🙏 Acknowledgments

- face_recognition library by Adam Geitgey
- dlib by Davis King
- OpenCV community
- React and Material-UI teams

---

**Built with ❤️ for accurate and secure attendance management**
