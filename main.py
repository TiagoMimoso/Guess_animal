import tkinter as tk
from tkinter import ttk
import requests
import subprocess
import platform

def start_ollama():
    system = platform.system()

    if system == "Windows":
        subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(["ollama", "serve"])

def ask_local_llm(prompt, model="qwen2.5:14b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 2,
                "top_p": 0.9,
                "top_k": 80,
                "repetition_penalty": 1.2,
            }
        }
    )
    data = response.json()
    return data["response"]


def generate_animal():
    prompt = "Pick a random animal from the entire world. Respond ONLY with the name of the animal."
    animal = ask_local_llm(prompt).strip()
    print(animal)
    return animal

def answer_question(secret_animal, question):
    prompt = f"""
    You are playing a guessing game. You must NEVER reveal the secret animal directly, even if the user asks.
    Only answer with "Yes", "No", don't use the secret animal's name.

    Secret animal (DO NOT REVEAL): {secret_animal}

    User question: "{question}"
    """
    return ask_local_llm(prompt).strip()


class AnimalGuessGUI:
    def __init__(self, master):
        self.master = master
        self.secret_animal = None
        master.title("Guess the Animal")
        master.geometry("700x500")
        master.minsize(700, 500)

        # Title
        self.title_label = ttk.Label(
            master,
            text="Guess the Animal",
            font=("Segoe UI", 15, "bold"),
            anchor="center"
        )
        self.title_label.pack(pady=10)
        # Frames

        self.top_frame = tk.Frame(master)
        self.bottom_frame = tk.Frame(master)
        self.bottom_frame.pack(side="bottom", fill="x")
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.bottom_frame.pack_propagate(False)
        self.bottom_frame.configure(height=50)

        # Scrollbar + Chat
        self.scrollbar = tk.Scrollbar(self.top_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat = tk.Text(
            self.top_frame,
            wrap="word",
            yscrollcommand=self.scrollbar.set,
            font=("Segoe UI", 12),
            bg="#f7f7f7",
            fg="#333",
            bd=2,
            relief="groove"
        )
        self.chat.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrollbar.config(command=self.chat.yview)

        # Entry + Buttons
        self.entry = ttk.Entry(self.bottom_frame, width=50, font=("Segoe UI", 12))
        self.entry.pack(side=tk.LEFT, padx=10, pady=10)

        self.entry.bind("<Return>", self.send_question_event)

        self.send_button = ttk.Button(self.bottom_frame, text="Send", command=self.send_question)
        self.send_button.pack(side=tk.LEFT, padx=5, pady=10)

        self.new_game_button = ttk.Button(self.bottom_frame, text="New Game", command=self.start_new_game)
        self.new_game_button.pack(side=tk.LEFT, padx=5, pady=10)


    def send_question_event(self, event):
        self.send_question()

    def send_question(self):
        if not self.secret_animal:
            self.chat.insert(tk.END, "Start a new game first!\n")
            return

        user_text = self.entry.get()
        self.chat.insert(tk.END, f"You: {user_text}\n")
        self.entry.delete(0, tk.END)
        self.entry.focus()

        guess = user_text.lower().strip()

        # remove punctuation
        guess = guess.replace("?", "").replace("!", "").replace(".", "")

        # check if the animal name appears anywhere in the guess
        if self.secret_animal.lower() in guess:
            self.chat.insert(tk.END, "🎉 Correct! You guessed the animal!\n")
            return

        # Otherwise, ask the LLM
        response = answer_question(self.secret_animal, user_text)
        self.chat.insert(tk.END, f"AI: {response}\n")

    def start_new_game(self):
        self.chat.insert(tk.END, "Starting a new game...\n")
        self.secret_animal = generate_animal()
        self.chat.insert(tk.END, "I picked an animal. Start asking questions!\n")


root = tk.Tk()
gui = AnimalGuessGUI(root)
root.mainloop()