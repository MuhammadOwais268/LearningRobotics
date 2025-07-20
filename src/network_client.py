# File: src/network_client.py

import requests
import logging
import threading
import time
from src.config import SERVER_URL

class NetworkClient:
    """
    Handles all HTTP communication with the central server.
    """
    def __init__(self, controller):
        self.controller = controller
        self.session_token = None
        self._live_feed_active = False
        self._polling_thread = None

    def _make_request(self, method, endpoint, data=None, requires_auth=False):
        """Helper function to make requests to the server."""
        url = f"{SERVER_URL}/{endpoint}"
        headers = {}
        if requires_auth:
            if not self.session_token:
                logging.error("Request requires auth, but no session token is available.")
                return None
            headers['Authorization'] = f"Bearer {self.session_token}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data)
            else: # POST
                response = requests.post(url, headers=headers, json=data)
            
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error communicating with {url}: {e}")
            return {"success": False, "message": str(e)}

    # --- User and Session Management ---
    def signup_user(self, email, password, role, dev_key=None):
        payload = {"email": email, "password": password, "role": role, "developer_key": dev_key}
        return self._make_request('POST', 'signup', data=payload)

    def login_user(self, email, password):
        payload = {"email": email, "password": password}
        response = self._make_request('POST', 'login', data=payload)
        if response and response.get("success"):
            self.session_token = response.get("token")
            logging.info(f"Successfully logged in. Session token acquired.")
        return response

    def logout_user(self):
        self.session_token = None
        self.stop_live_feed()
        logging.info("User logged out and session token cleared.")

    # --- Class Data Management ---
    def create_class(self, curriculum_data):
        return self._make_request('POST', 'class/create', data={"curriculum": curriculum_data}, requires_auth=True)
        
    def get_class_data(self, class_code):
        return self._make_request('GET', f'class/{class_code}', requires_auth=True)

    def update_class_data(self, class_code, new_data):
        payload = {"curriculum": new_data}
        return self._make_request('POST', f'class/{class_code}/update', data=payload, requires_auth=True)
    
    # --- Live Feed for Student Count ---
    def _poll_student_count(self):
        """The function that runs in a loop in the background."""
        while self._live_feed_active:
            endpoint = f"class/{self.controller.current_class_code}/student_count"
            response = self._make_request('GET', endpoint, requires_auth=True)
            if response and response.get("success"):
                count = response.get("student_count", 0)
                # Use the controller's method to update the UI safely
                self.controller.update_student_count_display(count)
            # Wait for some time before polling again
            time.sleep(5) # Poll every 5 seconds

    def start_live_feed(self):
        """Starts the background thread to poll for student count."""
        if self._polling_thread and self._polling_thread.is_alive():
            return # Already running
        
        self._live_feed_active = True
        self._polling_thread = threading.Thread(target=self._poll_student_count, daemon=True)
        self._polling_thread.start()
        logging.info("Live student count feed started.")

    def stop_live_feed(self):
        """Stops the background polling."""
        self._live_feed_active = False
        logging.info("Live student count feed stopped.")