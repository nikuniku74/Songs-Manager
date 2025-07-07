from flask import Flask, render_template, request, redirect, url_for
import os
import socket
import sys
import threading
import time
import webbrowser
import requests

def open_browser(port):
    url = f"http://127.0.0.1:{port}"
    def _open():
        webbrowser.open(url)
    threading.Timer(1.0, _open).start()  # leggero delay per assicurarsi che il server sia partito

def get_external_file(filename):
    if getattr(sys, 'frozen', False):
        app_path = os.path.abspath(os.path.join(sys.argv[0], "../../../.."))
    else:
        app_path = os.path.abspath(".")

    full_path = os.path.join(app_path, filename)
    print(f"[DEBUG] Caricamento file da: {full_path}")
    return full_path

app = Flask(__name__)
FILE_PATH = get_external_file("songs.txt")
PAGE_SIZE = 50

def find_free_port(default=5050):
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def parse_line(line):
    parts = line.strip().rsplit("(", 1)
    if len(parts) == 2:
        title = parts[0].strip()
        author_and_color = parts[1].strip().rstrip(")")
        if "^C" in author_and_color:
            author, color = author_and_color.split("^C")
        else:
            author, color = author_and_color, ""
        author = author.strip()
        if author.endswith(")"):
            author = author[:-1].strip()
        return {"title": title, "author": author, "color": color.strip()}
    return {"title": line.strip(), "author": "", "color": ""}

def format_line(entry):
    base = f"{entry['title']} ({entry['author']})"
    if entry['color']:
        base += f" ^C{entry['color']}"
    return base

def load_songs():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [parse_line(line) for line in lines if line.strip()]

def save_songs(songs):
    lines = [format_line(entry) for entry in songs]
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def get_colors():
    songs = load_songs()
    return sorted(set(s['color'] for s in songs if s['color']))

@app.route("/")
def index():
    query = request.args.get("q", "").lower()
    page = int(request.args.get("page", 1))
    songs = load_songs()
    songs.reverse()

    if query:
        songs = [s for s in songs if query in s['title'].lower() or query in s['author'].lower() or query in s['color'].lower()]

    total_pages = (len(songs) + PAGE_SIZE - 1) // PAGE_SIZE
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    paginated = songs[start:end]
    colors = get_colors()

    return render_template("index.html", songs=paginated, page=page, total_pages=total_pages, query=query, colors=colors)

@app.route("/add", methods=["POST"])
def add_song():
    title = request.form["title"].strip()
    author = request.form["author"].strip()
    color = request.form["color"].strip()
    songs = load_songs()
    songs.append({"title": title, "author": author, "color": color})
    save_songs(songs)
    return redirect(url_for("index"))

@app.route("/update/<int:index>", methods=["POST"])
def update_song(index):
    songs = load_songs()
    songs.reverse()
    if 0 <= index < len(songs):
        songs[index] = {
            "title": request.form["title"].strip(),
            "author": request.form["author"].strip(),
            "color": request.form["color"].strip()
        }
        songs.reverse()
        save_songs(songs)
    return redirect(url_for("index"))

@app.route("/delete/<int:index>", methods=["POST"])
def delete_song(index):
    songs = load_songs()
    songs.reverse()
    if 0 <= index < len(songs):
        del songs[index]
        songs.reverse()
        save_songs(songs)
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = find_free_port()
    print(f"Applicazione avviata su http://127.0.0.1:{port}")
    open_browser(port)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", port)))

