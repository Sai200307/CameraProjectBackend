import os, json, subprocess, threading, requests
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

CONFIG_FILE = "config/cameras.json"
OUTPUT_DIR = "streams"

app = FastAPI()

# Allow React frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for ngrok/public
    allow_methods=["*"],
    allow_headers=["*"],
)

# Detect ngrok public URL
def get_public_url():
    try:
        resp = requests.get("http://127.0.0.1:4040/api/tunnels")
        tunnels = resp.json()["tunnels"]
        for t in tunnels:
            if t["proto"] == "https":  # Prefer HTTPS tunnel
                return t["public_url"]
        return tunnels[0]["public_url"] if tunnels else "http://localhost:8000"
    except Exception:
        return "http://localhost:8000"

BASE_URL = get_public_url()

# Load/save camera config
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"data": []}
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

os.makedirs(OUTPUT_DIR, exist_ok=True)
cameras = load_config()

# Serve streams without caching
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.mount("/streams", NoCacheStaticFiles(directory=OUTPUT_DIR), name="streams")

# FFmpeg worker to generate HLS
def start_ffmpeg(cam_name: str, input_path: str):
    safe_name = cam_name.replace(" ", "_")
    hls_file = os.path.join(OUTPUT_DIR, f"{safe_name}.m3u8")
    cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1", "-i", input_path,
        "-c:v", "copy", "-c:a", "aac", "-f", "hls",
        "-hls_time", "2", "-hls_list_size", "10", "-hls_flags", "delete_segments",
        hls_file
    ]
    subprocess.Popen(cmd)
    # Update camera config with public URL
    for cam in cameras["data"]:
        if cam["cam_name"] == cam_name:
            cam["stream_url"] = f"{BASE_URL}/streams/{safe_name}.m3u8"
    save_config(cameras)

# Start FFmpeg for all active cameras
for cam in cameras["data"]:
    if cam["active"] and cam["rtsp_url"]:
        threading.Thread(target=start_ffmpeg, args=(cam["cam_name"], cam["rtsp_url"]), daemon=True).start()

# API Endpoints
@app.get("/cameras", response_class=JSONResponse)
async def get_cameras():
    return cameras

@app.post("/add_camera")
async def add_camera(
    cam_name: str = Body(...),
    rtsp_url: str = Body(...),
    sequence: int = Body(...),
    active: bool = Body(default=True)
):
    safe_name = cam_name.replace(" ", "_")
    new_cam = {
        "cam_name": cam_name,
        "rtsp_url": rtsp_url,
        "sequence": sequence,
        "active": active,
        "stream_url": f"{BASE_URL}/streams/{safe_name}.m3u8"
    }
    cameras["data"].append(new_cam)
    save_config(cameras)
    if active:
        threading.Thread(target=start_ffmpeg, args=(cam_name, rtsp_url), daemon=True).start()
    return {"status": "success", "camera": new_cam}
