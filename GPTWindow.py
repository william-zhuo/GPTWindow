import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyautogui
from PIL import Image, ImageTk
import io
import base64
import requests
import json
import threading
from datetime import datetime
from BlurWindow.blurWindow import blur
import re

class ScreenshotTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPTWindow")
        self.root.geometry("450x300")
        self.root.wm_attributes("-alpha", 1)
        self.root.wm_attributes("-transparentcolor", "red")
        self.root.attributes('-topmost', True)
        self.root.resizable(True, True)

        self.api_key = # API key 
        self.api_url = "https://api.openai.com/v1/chat/completions"

        self.current_image = None
        self.current_image_b64 = None
        self.mode = "screenshot"

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        self.root.configure(bg='gray50')
        self.main_frame = tk.Frame(self.root, bg='gray50')
        self.main_frame.pack(fill='both', expand=True)
        self.top_frame = tk.Frame(self.main_frame, bg='lightgray', relief='raised', bd=1)
        self.top_frame.pack(fill='x', padx=8, pady=(8, 0))

        self.screenshot_btn = tk.Button(self.top_frame, text="Take Screenshot", 
                                       command=self.take_screenshot, 
                                       bg='lightblue', fg='black',
                                       font=('Arial', 10, 'bold'),
                                       relief='raised', bd=2)

        self.ask_gpt_btn = tk.Button(self.top_frame, text="Ask GPT", 
                                    command=self.switch_to_chat, 
                                    bg='lightgreen', fg='black',
                                    font=('Arial', 10, 'bold'),
                                    relief='raised', bd=2)

        self.delete_btn = tk.Button(self.top_frame, text="Delete Screenshot", 
                                   command=self.delete_screenshot, 
                                   bg='lightcoral', fg='black',
                                   font=('Arial', 10, 'bold'),
                                   relief='raised', bd=2)

        self.spacing_frame = tk.Frame(self.main_frame, bg='gray50', height=10)
        self.spacing_frame.pack(fill='x')
        self.spacing_frame.pack_propagate(False)

        self.screenshot_container = tk.Frame(self.main_frame, bg='gray50')
        self.screenshot_container.pack(fill='both', expand=True, padx=0, pady=0)

        self.screenshot_display_frame = tk.Frame(self.screenshot_container, bg='gray50')
        self.screenshot_display_frame.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        self.main_display = tk.Label(self.screenshot_display_frame, 
                                    text="", 
                                    relief='flat', borderwidth=0, 
                                    font=('Arial', 10, 'bold'))
        self.main_display.pack(fill='both', expand=True)

        self.chat_frame = tk.Frame(self.main_frame, bg='gray50')
        chat_content_frame = tk.Frame(self.chat_frame, bg='white', relief='raised', bd=2)
        chat_content_frame.pack(fill='both', expand=True, padx=8, pady=(0, 8))
        chat_top_frame = tk.Frame(chat_content_frame, bg='lightgray', height=50, relief='raised', bd=1)
        chat_top_frame.pack(fill='x', padx=0, pady=(0, 5))
        chat_top_frame.pack_propagate(False)

        self.back_btn = tk.Button(chat_top_frame, text="← Back to Screenshot", 
                                 command=self.switch_to_screenshot, 
                                 bg='lightblue', fg='black',
                                 font=('Arial', 10, 'bold'),
                                 relief='raised', bd=2)
        self.back_btn.pack(side='left', padx=5, pady=10)

        self.delete_btn_chat = tk.Button(chat_top_frame, text="Delete Screenshot", 
                                        command=self.delete_screenshot, 
                                        bg='lightcoral', fg='black',
                                        font=('Arial', 10, 'bold'),
                                        relief='raised', bd=2)
        self.delete_btn_chat.pack(side='right', padx=10, pady=10)

        chat_input_frame = tk.Frame(chat_content_frame, bg='white')
        chat_input_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(chat_input_frame, text="Ask about the screenshot:", 
                bg='white', fg='black', font=('Arial', 10, 'bold')).pack(anchor='w')

        self.chat_entry = tk.Entry(chat_input_frame, font=('Arial', 10), 
                                  bg='white', fg='black', relief='sunken', bd=2)
        self.chat_entry.pack(fill='x', pady=2)
        self.chat_entry.bind('<Return>', lambda e: self.send_to_chatgpt())

        self.chat_btn = tk.Button(chat_input_frame, text="Ask ChatGPT", 
                                 command=self.send_to_chatgpt, 
                                 bg='lightgreen', fg='black',
                                 font=('Arial', 10, 'bold'),
                                 relief='raised', bd=2)
        self.chat_btn.pack(pady=5)

        response_frame = tk.Frame(chat_content_frame, bg='white')
        response_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tk.Label(response_frame, text="ChatGPT Response:", 
                bg='white', fg='black', font=('Arial', 10, 'bold')).pack(anchor='w')

        self.response_text = tk.Text(response_frame, height=8, wrap='word',
                                   bg='white', fg='black', relief='sunken', bd=2,
                                   font=('Segoe UI', 11))

        scrollbar = tk.Scrollbar(response_frame, orient='vertical', command=self.response_text.yview)
        self.response_text.configure(yscrollcommand=scrollbar.set)

        self.response_text.pack(side='left', fill='both', expand=True, pady=2)
        scrollbar.pack(side='right', fill='y', pady=2)

        self.setup_text_tags()
        self.show_screenshot_mode()

    def setup_text_tags(self):
        self.response_text.tag_configure("bold", font=('Segoe UI', 11, 'bold'))
        self.response_text.tag_configure("italic", font=('Segoe UI', 11, 'italic'))
        self.response_text.tag_configure("bold_italic", font=('Segoe UI', 11, 'bold italic'))
        self.response_text.tag_configure("code", font=('Consolas', 10), background='#f5f5f5', relief='solid', borderwidth=1)
        self.response_text.tag_configure("header1", font=('Segoe UI', 16, 'bold'), spacing3=10)
        self.response_text.tag_configure("header2", font=('Segoe UI', 14, 'bold'), spacing3=8)
        self.response_text.tag_configure("header3", font=('Segoe UI', 12, 'bold'), spacing3=6)

    def show_screenshot_mode(self):
        self.mode = "screenshot"
        self.chat_frame.pack_forget()
        self.top_frame.pack(fill='x', padx=8, pady=(8, 0))
        self.spacing_frame.pack(fill='x')
        self.screenshot_container.pack(fill='both', expand=True, padx=0, pady=0)

        if self.current_image is None:
            self.screenshot_btn.pack(side='left', padx=5, pady=10)
            self.ask_gpt_btn.pack_forget()
            self.delete_btn.pack_forget()
            self.main_display.config(text="", bg='red', fg='white', relief='flat', borderwidth=0)
        else:
            self.screenshot_btn.pack_forget()
            self.ask_gpt_btn.pack(side='left',  padx=10, pady=10)
            self.delete_btn.pack(side='right', padx=10, pady=10)
            self.main_display.config(bg='white', fg='black', relief='sunken', borderwidth=2)

    def show_chat_mode(self):
        self.mode = "chat"
        self.screenshot_container.pack_forget()
        self.spacing_frame.pack_forget()
        self.top_frame.pack_forget()
        self.chat_frame.pack(fill='both', expand=True, padx=8, pady=8)

    def switch_to_chat(self):
        if self.current_image is None:
            messagebox.showwarning("No Screenshot", "Please take a screenshot first!")
            return
        self.root.geometry("800x500")
        self.show_chat_mode()

    def switch_to_screenshot(self):
        if self.current_image is not None:
            img_width, img_height = self.current_image.size
            ui_height_padding = 78
            ui_width_padding = 26
            new_width = img_width + ui_width_padding
            new_height = img_height + ui_height_padding
            new_width = max(new_width, 450)
            new_height = max(new_height, 300)
            self.root.geometry(f"{new_width}x{new_height}")
        self.show_screenshot_mode()

    def delete_screenshot(self):
        if not messagebox.askyesno("Delete Screenshot", "Are you sure you want to delete the screenshot?"):
            return
        self.current_image = None
        self.current_image_b64 = None
        self.main_display.config(image='', text="", bg='red', fg='white',
                                 relief='flat', borderwidth=0)
        self.ask_gpt_btn.pack_forget()
        self.delete_btn.pack_forget()
        self.show_screenshot_mode()

    def take_screenshot(self):
        try:
            self.root.update_idletasks()
            display_x = self.main_display.winfo_rootx()
            display_y = self.main_display.winfo_rooty()
            display_width = self.main_display.winfo_width()
            display_height = self.main_display.winfo_height()
            self.root.after(100, self.capture_screen, display_x, display_y, 
                           display_width, display_height)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {str(e)}")

    def capture_screen(self, x, y, width, height):
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            self.current_image = screenshot
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            self.current_image_b64 = base64.b64encode(buffer.getvalue()).decode()
            self.display_screenshot(screenshot)
            self.show_screenshot_mode()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screen: {str(e)}")

    def display_screenshot(self, image):
        try:
            self.photo = ImageTk.PhotoImage(image)
            self.main_display.config(image=self.photo, text="", bg='white', relief='sunken', bd=2)
        except Exception as e:
            self.main_display.config(text=f"Error displaying image: {str(e)}", bg='white')

    def send_to_chatgpt(self):
        if self.current_image_b64 is None:
            messagebox.showwarning("No Screenshot", "Please take a screenshot first!")
            return

        question = self.chat_entry.get().strip()
        if not question:
            messagebox.showwarning("No Question", "Please enter a question about the screenshot!")
            return

        self.chat_btn.config(state='disabled', text='Sending...')
        thread = threading.Thread(target=self.call_chatgpt_api, args=(question,))
        thread.daemon = True
        thread.start()

    def call_chatgpt_api(self, question):
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": question
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{self.current_image_b64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                self.root.after(0, self.display_response, answer)
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                self.root.after(0, self.display_error, error_msg)

        except Exception as e:
            self.root.after(0, self.display_error, f"Request failed: {str(e)}")

    def parse_markdown(self, text):
        self.response_text.delete(1.0, tk.END)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_start = self.response_text.index(tk.END + "-1c")
            if line.startswith('### '):
                content = line[4:].strip()
                self.response_text.insert(tk.END, content)
                line_end = self.response_text.index(tk.END + "-1c")
                self.response_text.tag_add("header3", line_start, line_end)
            elif line.startswith('## '):
                content = line[3:].strip()
                self.response_text.insert(tk.END, content)
                line_end = self.response_text.index(tk.END + "-1c")
                self.response_text.tag_add("header2", line_start, line_end)
            elif line.startswith('# '):
                content = line[2:].strip()
                self.response_text.insert(tk.END, content)
                line_end = self.response_text.index(tk.END + "-1c")
                self.response_text.tag_add("header1", line_start, line_end)
            else:
                self.process_inline_formatting(line)
            if i < len(lines) - 1:
                self.response_text.insert(tk.END, '\n')

    def process_inline_formatting(self, line):
        import re
        current_pos = 0
        line_start_index = self.response_text.index(tk.END + "-1c")
        patterns = [
            (r'\*\*(.*?)\*\*', 'bold'),
            (r'\*(.*?)\*', 'italic'),
            (r'`(.*?)`', 'code'),
        ]
        matches = []
        for pattern, tag in patterns:
            for match in re.finditer(pattern, line):
                matches.append((match.start(), match.end(), match.group(1), tag))
        matches.sort()
        last_end = 0
        for start, end, content, tag in matches:
            if start > last_end:
                plain_text = line[last_end:start]
                self.response_text.insert(tk.END, plain_text)
            format_start = self.response_text.index(tk.END + "-1c")
            self.response_text.insert(tk.END, content)
            format_end = self.response_text.index(tk.END + "-1c")
            self.response_text.tag_add(tag, format_start, format_end)
            last_end = end
        if last_end < len(line):
            remaining_text = line[last_end:]
            self.response_text.insert(tk.END, remaining_text)

    def display_response(self, response):
        self.parse_markdown(response)
        self.chat_btn.config(state='normal', text='Ask ChatGPT')
        self.chat_entry.delete(0, tk.END)

    def display_error(self, error):
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, f"Error: {error}")
        self.chat_btn.config(state='normal', text='Ask ChatGPT')

    def on_closing(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ScreenshotTool()
        app.run()
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages with:")
        print("pip install pyautogui pillow requests")
    except Exception as e:
        print(f"Error starting application: {e}")