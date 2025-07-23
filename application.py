import tkinter as tk
from tkinter import ttk, Canvas
import google.generativeai as genai

# Gemini Configuration
API_Key = "AIzaSyCI7Du0Eyg5bHSGTdyqTboJAZ-ETmduIWY"  # Replace with your API key
genai.configure(api_key=API_Key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Session state
session_history = {}
current_session = "New Chat"
session_counter = 1

# Window setup
window = tk.Tk()
window.title("Saifullah The AI Assistant")
window.geometry("1000x700")
window.configure(bg="#1e1e1e")

# Sidebar
sidebar = tk.Frame(window, bg="#2a2a2a", width=200)
sidebar.pack(side=tk.LEFT, fill=tk.Y)

# Main area
main_area = tk.Frame(window, bg="#1e1e1e")
main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Header
header = tk.Label(main_area, text="💬 Saifi's AI Assistant", font=("Segoe UI", 20, "bold"), fg="cyan", bg="#1e1e1e")
header.pack(pady=10)

# Chat area with canvas & scrollbar
chat_frame = tk.Frame(main_area, bg="#1e1e1e")
chat_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(chat_frame, bg="#1e1e1e", highlightthickness=0)
scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Input section
bottom_frame = tk.Frame(main_area, bg="#1e1e1e")
bottom_frame.pack(pady=10, padx=20, fill=tk.X)

placeholder_text = "Ask me anything"

def on_focus_in(event):
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)
        entry.config(fg="white")

def on_focus_out(event):
    if entry.get() == "":
        entry.insert(0, placeholder_text)
        entry.config(fg="gray")

def auto_focus(event):
    if entry.get() == placeholder_text or entry.get() == "":
        entry.focus_set()

entry = tk.Entry(
    bottom_frame,
    font=("Segoe UI", 13),
    bg="#2a2a2a",
    fg="gray",
    relief=tk.FLAT,
    insertbackground="white"
)
entry.insert(0, placeholder_text)
entry.bind("<FocusIn>", on_focus_in)
entry.bind("<FocusOut>", on_focus_out)
window.bind("<Key>", auto_focus)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))

send_btn = ttk.Button(bottom_frame, text="Send ➤", command=lambda: send_message())
send_btn.pack(side=tk.RIGHT)

# Utilities
def scroll_to_bottom():
    window.update_idletasks()
    canvas.yview_moveto(1.0)

def add_bubble(sender, message, is_user=False):
    bubble_frame = tk.Frame(scrollable_frame, bg="#1e1e1e", pady=5)
    bubble_frame.pack(anchor='e' if is_user else 'w', fill=tk.X, padx=5)

    bubble_color = "#0084FF" if is_user else "#2f2f2f"
    text_color = "white"

    bubble = tk.Label(
        bubble_frame,
        text=f"{sender}:\n{message}",
        font=("Segoe UI", 11),
        bg=bubble_color,
        fg=text_color,
        wraplength=600,
        justify=tk.LEFT,
        padx=12,
        pady=8,
        anchor="w"
    )
    bubble.pack(anchor='e' if is_user else 'w', padx=10)

    scroll_to_bottom()

def clear_chat():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

def load_session(session_name):
    global current_session
    current_session = session_name
    clear_chat()
    for sender, msg in session_history.get(session_name, []):
        add_bubble(sender, msg, is_user=(sender == "You"))

def update_sidebar():
    for widget in sidebar.winfo_children():
        widget.destroy()

    tk.Label(sidebar, text="Sessions", bg="#2a2a2a", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=10)

    for session_name in session_history:
        btn = tk.Button(sidebar, text=session_name, width=20, anchor="w", bg="#333333", fg="white",
                        font=("Segoe UI", 10), relief=tk.FLAT,
                        command=lambda name=session_name: load_session(name))
        btn.pack(pady=2, padx=5)

    tk.Button(sidebar, text="+ New Chat", width=20, anchor="center", bg="#0084FF", fg="white",
              font=("Segoe UI", 10, "bold"), relief=tk.FLAT, command=start_new_chat).pack(pady=10, padx=5)

def start_new_chat():
    global session_counter, current_session
    current_session = f"Session {session_counter}"
    session_counter += 1
    session_history[current_session] = []
    clear_chat()
    update_sidebar()

def send_message():
    user_input = entry.get().strip()
    if user_input == "" or user_input == placeholder_text:
        return

    add_bubble("You", user_input, is_user=True)
    session_history.setdefault(current_session, []).append(("You", user_input))
    entry.delete(0, tk.END)
    add_bubble("Saifullah", "⏳ Saifullah is typing...", is_user=False)
    window.after(200, lambda: get_response(user_input))

def get_response(user_input):
    try:
        response = model.generate_content(user_input)
        reply = response.text
    except Exception as e:
        reply = f"Error: {str(e)}"

    # Remove typing bubble
    last_widget = scrollable_frame.winfo_children()[-1]
    last_widget.destroy()

    add_bubble("Saifullah", reply, is_user=False)
    session_history.setdefault(current_session, []).append(("Saifullah", reply))

# Enter key binding
window.bind("<Return>", lambda event: send_message())

# Start app
start_new_chat()
window.mainloop()
