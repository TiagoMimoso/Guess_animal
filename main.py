import tkinter as tk
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

        self.chat = tk.Text(master, height=20, width=50)
        self.chat.pack()

        self.entry = tk.Entry(master, width=40)
        self.entry.pack(side=tk.LEFT, padx=5, pady=5)

        self.entry.bind("<Return>", self.send_question_event)

        self.send_button = tk.Button(master, text="Send", command=self.send_question)
        self.send_button.pack(side=tk.LEFT)

        self.new_game_button = tk.Button(master, text="New Game", command=self.start_new_game)
        self.new_game_button.pack(side=tk.LEFT)

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