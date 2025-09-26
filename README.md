
1. python -m venv venv
2. .\venv\Scripts\Activate.ps1
3.pip install -r requirements.txt
4.go to config/cameras.json and replace the rtsp url with the streaming web cam rtsp
###run the app with
uvicorn app:app --host 0.0.0.0 --port 8000
