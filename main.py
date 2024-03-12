import platform
import subprocess
import pathlib

import tkinter as tk
from tkinter import filedialog, messagebox

from synchronize import offset_in_ms

TITLE = "VLC Subtitle Syncronizer"

ALLOWED_VIDEO_EXTENSIONS = [
    ("Video Files", "*.mp4;*.mkv;*.avi;*.flv;*.mov;*.wmv;*.webm;*.mpg;*.mpeg;*.m4v;*.3gp;*.3g2")
]
ALLOWED_SUBTITLES_EXTENSIONS = [
    ("Subtitles Files", "*.ass;*.ssa;*.srt;*.sub;*.txt")
]

if platform.system() == "Windows":
    VLC_PATH = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
else:
    VLC_PATH = "vlc"


def launch_vlc(video_file, subtitles_file, vlc_path=VLC_PATH):
    try:
        video_file_path = video_file.get()
        subtitles_file_path = subtitles_file.get()
        offset = offset_in_ms(video_file_path, subtitles_file_path)

        vlc_cmd = [vlc_path, pathlib.Path(video_file_path)]
        vlc_cmd.extend(["--sub-file", pathlib.Path(subtitles_file_path)])
        vlc_cmd.extend(["--sub-delay", str(offset // 100)])

        subprocess.Popen(vlc_cmd)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def init_gui() -> tk.Tk:
    root = tk.Tk()
    root.title(TITLE)
    root.resizable(False, False)

    video_file = add_file_input(root, "Video File:", 0, ALLOWED_VIDEO_EXTENSIONS)
    subtitles_file = add_file_input(root, "Subtitles File:", 1, ALLOWED_SUBTITLES_EXTENSIONS)

    button_open_vlc = tk.Button(
        root, text="Calculate the delay and open in VLC",
        command=lambda: launch_vlc(video_file, subtitles_file)
    )
    button_open_vlc.grid(row=2, column=0, columnspan=3, pady=5)

    return root


def add_file_input(root: tk.Tk, label: str, row: int, filetypes: list):
    label = tk.Label(root, text=label)
    label.grid(row=row, column=0, padx=10, pady=5)
    file = tk.Entry(root, width=100)
    file.grid(row=row, column=1, padx=10, pady=5)
    button_browse_video_file = tk.Button(
        root, text="Browse",
        command=lambda: browse_file(file, filetypes=filetypes)
    )
    button_browse_video_file.grid(row=row, column=2, padx=5, pady=5)
    return file


def browse_file(entry: tk.Entry, filetypes: list) -> None:
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    entry.delete(0, tk.END)
    entry.insert(0, file_path)


if __name__ == '__main__':
    root = init_gui()
    root.mainloop()
