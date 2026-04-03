import time
import threading
import webbrowser
import hashlib

from config import *
from midi import MidiController, note_to_pad
from github_listener import GitHubListener
from utils import print_repo

# Init
try:
    midi = MidiController(PUSH_PORT_NAME)
except Exception as e:
    print(e)
    exit(1)

github = GitHubListener(GITHUB_TOKEN)

pad_repos = {}
grid_state = {}

def stable_hash(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

def decay():
    for key in list(grid_state.keys()):
        v = max(MIN_BRIGHTNESS, grid_state[key] - DECAY_STEP)
        grid_state[key] = v
        midi.light_pad(*key, v)

def listen():
    for msg in midi.inport:
        if msg.type == 'note_on' and msg.velocity > 0:
            row, col = note_to_pad(msg.note)
            if (row, col) in pad_repos:
                webbrowser.open(pad_repos[(row, col)])

threading.Thread(target=listen, daemon=True).start()

print("🌍 GlitchHub Active...")

while True:
    try:
        events = github.fetch_events()
        pushes = github.filter_push_events(events, DEDUP_SECONDS)

        for repo, event in pushes:
            h = stable_hash(repo)

            row = h % GRID_SIZE
            col = (h // GRID_SIZE) % GRID_SIZE

            url = f"https://github.com/{repo}"

            # brightness based on commit count
            commits = len(event.get("payload", {}).get("commits", []))
            velocity = min(127, max(20, commits * 20))

            pad_repos[(row, col)] = url
            grid_state[(row, col)] = velocity

            midi.light_pad(row, col, velocity)
            print_repo(repo)

        decay()
        time.sleep(POLL_INTERVAL)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
