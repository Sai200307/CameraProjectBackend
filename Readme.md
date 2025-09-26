# 📹 Camera Streaming Backend (FastAPI + FFmpeg + Ngrok)

This project provides a **FastAPI backend** for streaming RTSP cameras to **HLS (`.m3u8`) format**.  
It uses **FFmpeg** for transcoding and **Ngrok** for exposing the server publicly.

---

## 🚀 Quick Start

### 1️⃣ Create Virtual Environment
```bash
python -m venv venv
```

### 2️⃣ Activate Virtual Environment
- On **Windows (PowerShell)**:
  ```bash
  .\venv\Scripts\Activate.ps1
  ```
- On **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Cameras
Edit `config/cameras.json` and replace the `rtsp_url` with your streaming webcam RTSP link.  

Example:
```json
{
  "title": "Camera Config",
  "version": 1.0,
  "data": [
    {
         "cam_name": "Probe Cam",
            "stream_url": "http://localhost:8000/streams/Probe_Cam.m3u8",
            "sequence": 1,
            "active": true,
            "rtsp_url": "rtsp://localhost:8554/testvideo"
    }
  ]
}
```

### 5️⃣ Run FastAPI App
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The backend will:
- Start **FFmpeg** for each active camera
- Generate `.m3u8` HLS playlists & `.ts` segments under `/streams/`

Example local stream URL:
```
http://localhost:8000/streams/My_Camera.m3u8
```

---

## 🌍 Expose Publicly with Ngrok
To make the stream accessible outside localhost:

```bash
ngrok http 8000
```

Ngrok will generate a public forwarding URL like:
```
https://abcd1234.ngrok-free.app -> http://localhost:8000
```

Your camera stream will then be available at:
```
https://abcd1234.ngrok-free.app/streams/My_Camera.m3u8
```

---

## 📂 Project Structure
```
├── app.py                # FastAPI application
├── config/
│   └── cameras.json      # Camera configuration file
├── streams/              # Generated HLS files (.m3u8 + .ts)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🔗 API Endpoints
- `GET /cameras` → Fetch all configured cameras  
- `POST /add_camera` → Add a new camera (starts FFmpeg automatically)  

Example `POST /add_camera` request:
```json
{
  "cam_name": "Lobby Camera",
  "rtsp_url": "rtsp://192.168.0.50:554/stream",
  "sequence": 2,
  "active": true
}
```

---

## 📦 Requirements (`requirements.txt`)
Your `requirements.txt` should contain:
```
fastapi
uvicorn
python-multipart
```

⚠️ **Note:**  
- Make sure **FFmpeg** is installed and added to your system `PATH`.  
- Ngrok must also be installed (`npm i -g ngrok` or [download here](https://ngrok.com/download)).  

---

## ⚡ Notes
- Ensure **FFmpeg** is available in your system before running.  
- Use **Ngrok** only for testing/sharing — for production, deploy on a proper server.  
- Recommended to use a **process manager** (e.g., `supervisor`, `pm2`, or `systemd`) to keep FFmpeg processes alive.  

---
✅ You’re now ready to stream your RTSP cameras over HTTP with FastAPI + FFmpeg + Ngrok! 🚀
