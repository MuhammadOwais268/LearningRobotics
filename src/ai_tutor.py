# File: client/src/ai_tutor.py

import ollama
import logging
import threading
import queue

class AITutor:
    def __init__(self, controller):
        self.controller = controller
        self.response_queue = queue.Queue()
        
        # Check if the Ollama server is reachable on startup.
        try:
            ollama.ps() 
            self.is_available = True
            logging.info("Local Ollama AI engine detected.")
        except Exception:
            self.is_available = False
            logging.warning("Local Ollama AI engine not found. AI Tutor will be disabled.")
            logging.warning("Please ensure the 'ollama serve' command is running in a terminal.")

    def _get_explanation_in_thread(self, question, code_snippet=None, full_code_context=None):
        """
        This function runs in a separate thread to avoid freezing the GUI.
        It communicates with Ollama and puts the response in a queue.
        """
        if not self.is_available:
            self.response_queue.put("Error: The local AI engine (Ollama) is not running.")
            return

        system_prompt = (
            "You are an AI Tutor named Robo-Tutor for a beginner's robotics application. "
            "Your audience is new to both C++ programming and robotics. "
            "Explain concepts clearly and simply, using helpful analogies related to the "
            "ESP32 robot car they are working on. Keep your answers concise."
        )

        if code_snippet and full_code_context:
            user_prompt = (
                f"The user is working on the following C++ code for their robot:\n---\n"
                f"{full_code_context}\n---\n"
                f"They have highlighted this specific snippet:\n---\n"
                f"{code_snippet}\n---\n"
                f"Their question about this snippet is: {question}"
            )
        else:
            user_prompt = (
                f"The user is working on a C++ program for an ESP32 robot car.\n"
                f"They have asked the following general question: \"{question}\"\n"
                f"Please answer their question. Where possible, relate your answer back to the "
                f"context of their robot car project (e.g., mention the VL53L0X sensor, motors, OLED display)."
            )

        try:
            response = ollama.chat(
                model='phi3',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                stream=False
            )
            self.response_queue.put(response['message']['content'])
        except Exception as e:
            logging.error(f"Error communicating with local Ollama engine: {e}")
            self.response_queue.put("An error occurred while talking to the local AI engine.")

    def get_ai_explanation(self, question, code_snippet=None, full_code_context=None):
        """
        Starts the AI explanation process in a background thread.
        """
        thread = threading.Thread(
            target=self._get_explanation_in_thread,
            args=(question, code_snippet, full_code_context),
            daemon=True
        )
        thread.start()