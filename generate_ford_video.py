#!/usr/bin/env python3
"""
Ford animation generator — uses curl.exe for all HTTP calls to avoid Cloudflare blocks.
"""

import json, os, subprocess, sys, time
from pathlib import Path

API_BASE        = "https://api.kie.ai/api/v1"
CREATE_URL      = f"{API_BASE}/jobs/createTask"
STATUS_URL      = f"{API_BASE}/jobs/recordInfo"
UPLOAD_URL      = "https://api.kie.ai/api/file-stream-upload"
CURL            = "C:\\Windows\\System32\\curl.exe"
POLL_INTERVAL   = 12
TIMEOUT_SECONDS = 900

PROMPT = (
    "The scene opens on a detailed technical blueprint of a 2019 Ford Fusion Sedan "
    "laid flat on a drafting table — blue ink lines, dimension annotations, and "
    "multi-view diagrams visible. Additional sketch lines animate themselves onto the "
    "blueprint as if drawn by an invisible hand, crisp and precise. The camera slowly "
    "pushes in toward the large side-profile illustration. As it zooms in, the flat "
    "blueprint lines begin to gain depth and dimension, morphing into a fully "
    "photorealistic white Ford Fusion Sedan — paint, chrome, glass, and metallic "
    "details filling in progressively from the rear of the car toward the front, "
    "panel by panel, as if being built in real-time. "
    "Bold large white sans-serif text slides in smoothly from the left edge of the "
    "frame: 'Turn your dream into reality' — very large, dominant, occupying "
    "the center of the screen, remaining clearly visible long enough for the viewer "
    "to read it fully. "
    "The camera then slowly pulls back out, the photorealistic car dissolves back into "
    "blueprint lines and technical annotations, and the scene gently fades back into "
    "the original flat blueprint drawing on the drafting table. "
    "Cinematic, smooth motion, 16:9, high quality."
)


def load_api_key() -> str:
    key = os.environ.get("KIE_API_KEY", "")
    if not key:
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("KIE_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        sys.exit("ERROR: KIE_API_KEY not found in environment or .env file.")
    return key


def curl_json(args: list) -> dict:
    """Run curl.exe and return parsed JSON response."""
    result = subprocess.run(
        [CURL, "--silent", "--show-error", "--location", "--ssl-no-revoke"] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        sys.exit(f"curl error: {result.stderr}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.exit(f"Could not parse response: {result.stdout[:500]}")


def upload_asset(file_path: str, api_key: str) -> str:
    """Upload to litterbox.catbox.moe (anonymous, 72h retention) and return the URL."""
    path = Path(file_path)
    if not path.exists():
        sys.exit(f"File not found: {file_path}")

    print(f"  Uploading {path.name} ({path.stat().st_size / 1_048_576:.1f} MB) to litterbox...")
    result = subprocess.run(
        [CURL, "--silent", "--show-error", "--ssl-no-revoke",
         "-F", "reqtype=fileupload",
         "-F", "time=72h",
         "-F", f"fileToUpload=@{path}",
         "https://litterbox.catbox.moe/resources/internals/api.php"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        sys.exit(f"litterbox upload error: {result.stderr}")

    url = result.stdout.strip()
    if not url.startswith("https://"):
        sys.exit(f"Upload failed — unexpected response: {url}")

    print(f"  Uploaded -> {url}")
    return url


def create_task(first_frame_url: str, api_key: str) -> str:
    payload = {
        "model": "bytedance/seedance-2",
        "input": {
            "prompt": PROMPT,
            "first_frame_url": first_frame_url,
            "duration": 5,
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "generate_audio": False,
            "web_search": False,
        },
    }
    payload_str = json.dumps(payload)
    print("  Submitting task to Seedance 2.0...")
    resp = curl_json([
        "-X", "POST", CREATE_URL,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", payload_str,
    ])
    if resp.get("code") != 200:
        sys.exit(f"Task creation failed: {resp}")
    task_id = resp["data"]["taskId"]
    print(f"  Task ID: {task_id}")
    return task_id


def poll_task(task_id: str, api_key: str) -> dict:
    url = f"{STATUS_URL}?taskId={task_id}"
    deadline = time.time() + TIMEOUT_SECONDS
    last_state = None
    interval = POLL_INTERVAL

    print("  Waiting for generation to complete...")
    while time.time() < deadline:
        time.sleep(interval)
        resp = curl_json([
            "-X", "GET", url,
            "-H", f"Authorization: Bearer {api_key}",
        ])
        if resp.get("code") != 200:
            sys.exit(f"Status check failed: {resp}")
        data = resp["data"]
        state = data.get("state", "unknown")
        if state != last_state:
            progress = data.get("progress")
            prog_str = f" ({progress}%)" if progress is not None else ""
            print(f"  Status: {state}{prog_str}")
            last_state = state
        if state == "success":
            return data
        if state == "fail":
            sys.exit(f"Generation failed: {data.get('failMsg')} (code {data.get('failCode')})")
        interval = min(interval + 5, 30)

    sys.exit("Timed out waiting for generation.")


def download_video(task_data: dict, output_dir: str, task_id: str) -> str:
    result = json.loads(task_data.get("resultJson", "{}"))
    urls = result.get("resultUrls", [])
    if not urls:
        sys.exit(f"No result URLs in response: {result}")

    video_url = urls[0]
    out_file = Path(output_dir) / "FORDVIDEO.mp4"
    print(f"  Downloading video...")
    result = subprocess.run(
        [CURL, "--silent", "--show-error", "--location", "--ssl-no-revoke",
         "-H", "Referer: https://kie.ai/",
         "-o", str(out_file), video_url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.exit(f"Download failed: {result.stderr}")
    return str(out_file)


def main():
    project_dir = Path(__file__).parent
    image_path  = str(project_dir / "FORDIMAGE.jpg")
    video_path  = str(project_dir / "FORDVIDEO.mp4")
    output_dir  = str(project_dir)

    print("\n=== Ford Seedance Animation Generator ===\n")

    api_key = load_api_key()

    print("[1/4] Uploading reference image (FORDIMAGE.jpg)...")
    image_url = upload_asset(image_path, api_key)

    print("[2/4] Submitting generation task...")
    task_id = create_task(image_url, api_key)

    print("[3/4] Monitoring & downloading result...")
    task_data = poll_task(task_id, api_key)
    output_file = download_video(task_data, output_dir, task_id)

    print(f"\n=== Done! ===")
    print(f"Video saved to: {output_file}")
    print()
    print("Embed on your site with:")
    print('<video autoplay loop muted playsinline>')
    print(f'  <source src="{Path(output_file).name}" type="video/mp4">')
    print('</video>')


if __name__ == "__main__":
    main()
