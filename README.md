![ollama](https://github.com/user-attachments/assets/1157ac74-e63b-4403-b476-512ed86401ef)

# Ollama-UI

A GTK-based user interface for Ollama.

https://github.com/ollama/ollama

![screenshot 1](https://github.com/user-attachments/assets/8e92db81-ade5-4fd6-95ba-d0077ffc094f)

![screenshot 2](https://github.com/user-attachments/assets/57df28a6-9900-486b-b643-6f7b78e72ae1)

## Features

- **Conversation Management**: Start new conversations and manage past conversations with quick access via a sidebar.
- **Model Selection**: Choose from available LLM models using a dropdown for customized responses.
- **Collapsible Sidebar**: Toggle the sidebar to save space or expand it to view more options.
- **SVG Icon Integration**: Buttons with SVG icons for a polished interface.
- **Auto-saving**: Automatically saves conversations to `conversations.json` for easy access upon relaunch.

## Requirements

- **Python 3.x**
- **GTK+ 3** with PyGObject
- **Local LLM API Endpoint** running on `http://localhost:11434`
  - This should expose a `/api/chat` endpoint for querying responses and a `/api/tags` endpoint for available models.

## Installation

1. **Install dependencies**:
   - For Ubuntu:
     ```bash
     sudo apt update
     sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-rsvg-2.0
     ```
   - For macOS, using Homebrew:
     ```bash
     brew install pygobject3 gtk+3 librsvg
     ```
   - Ensure you have a local LLM API available on `localhost:11434`.

2. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ollama-ui.git
   cd ollama-ui
   ```

3. **Run the application**:
   ```bash
   python3 main.py
   ```

## Usage

- **Starting a Conversation**: Click the "New Conversation" button to begin a new chat. 
- **Model Selection**: Use the dropdown to select the LLM model. The model list is populated from your local API endpoint.
- **Sending Messages**: Type your message in the entry box and press Enter or click the "Send" button.
- **Sidebar Toggle**: Collapse or expand the sidebar by clicking the sidebar toggle button for better screen utilization.

## Project Structure

- **main.py**: The main application file, containing the `ChatApp` class and program logic.
- **SVG Assets**: SVG icons like `collapse.svg` and `convo.svg` for UI buttons.
- **Data Storage**: `conversations.json` file to store chat history for seamless continuity between sessions.

## API Requirements

The application expects two endpoints on a local server:

1. **Chat Endpoint**: `POST http://localhost:11434/api/chat`
   - **Payload**: `{ "model": "model_name", "messages": [{"role": "user", "content": "message"}] }`
2. **Model List Endpoint**: `GET http://localhost:11434/api/tags`
   - **Response**: `{ "models": [{"name": "model_name"}, ...] }`

## Notes

- **Error Handling**: Alerts are provided for API failures or connectivity issues.
- **Local Storage**: Conversations are saved in a JSON file, `conversations.json`, located in the project directory.

