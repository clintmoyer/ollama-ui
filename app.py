"""
Copyright 2024 Clint Moyer

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
"""
import json
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Rsvg", "2.0")
from gi.repository import Gtk, Rsvg, GdkPixbuf

class ChatApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Local ChatGPT")
        
        self.set_default_size(1400, 800)
        self.sidebar_expanded = True  # Track sidebar state

        # Conversation data
        self.conversations = {}
        self.current_conversation = None
        self.llm_choice = None  # Selected model choice
        self.load_conversations()

        # Main layout (horizontal box)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(hbox)

        # Sidebar setup
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.sidebar.set_size_request(200, -1)
        hbox.pack_start(self.sidebar, False, False, 0)

        # Icon box for buttons
        self.icon_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.sidebar.pack_start(self.icon_hbox, False, False, 0)

        # Load SVG images for the buttons
        collapse_image = self.load_svg_image("collapse.svg", 24, 24)
        convo_image = self.load_svg_image("convo.svg", 24, 24)

        # Collapse button with SVG icon
        self.collapse_icon = Gtk.Button()
        self.collapse_icon.set_image(collapse_image)
        self.collapse_icon.connect("clicked", self.toggle_sidebar)
        self.icon_hbox.pack_start(self.collapse_icon, False, False, 0)

        # New conversation button with SVG icon
        self.new_convo_icon = Gtk.Button()
        self.new_convo_icon.set_image(convo_image)
        self.new_convo_icon.connect("clicked", self.on_new_conversation)
        self.icon_hbox.pack_end(self.new_convo_icon, False, False, 0)

        # Render initial conversation buttons
        self.render_conversations()
        
        # Chat area setup
        chat_area_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        hbox.pack_start(chat_area_box, True, True, 0)

        # Model dropdown
        self.dropdown_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        chat_area_box.pack_start(self.dropdown_hbox, False, False, 0)

        self.model_dropdown = Gtk.ComboBoxText()
        self.populate_model_dropdown()  
        self.model_dropdown.connect("changed", self.on_model_changed)
        self.dropdown_hbox.pack_start(self.model_dropdown, False, False, 0)

        # Chat display area
        chat_scroll = Gtk.ScrolledWindow()
        self.chat_text_view = Gtk.TextView()
        self.chat_text_view.set_editable(False)
        self.chat_text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.chat_text_buffer = self.chat_text_view.get_buffer()
        chat_scroll.add(self.chat_text_view)
        chat_area_box.pack_start(chat_scroll, True, True, 0)

        # Chat entry and send button
        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.chat_entry = Gtk.Entry()
        self.chat_entry.set_placeholder_text("Message GPT")  # Placeholder text
        self.chat_entry.connect("activate", self.on_send_message)
        entry_box.pack_start(self.chat_entry, True, True, 0)

        # Send button
        send_button = Gtk.Button(label="C")
        send_button.connect("clicked", self.on_send_message)
        entry_box.pack_start(send_button, False, False, 0)

        chat_area_box.pack_start(entry_box, False, False, 10)

        # Start a new conversation automatically on startup
        self.on_new_conversation(None)

    def load_svg_image(self, filename, width, height):
        """Load an SVG file and return a Gtk.Image scaled to the specified size."""
        handle = Rsvg.Handle.new_from_file(filename)
        svg_width = handle.get_dimensions().width
        svg_height = handle.get_dimensions().height
        scale_factor = min(width / svg_width, height / svg_height)

        pixbuf = handle.get_pixbuf()
        scaled_pixbuf = pixbuf.scale_simple(
            int(svg_width * scale_factor), int(svg_height * scale_factor), GdkPixbuf.InterpType.BILINEAR
        )
        image = Gtk.Image.new_from_pixbuf(scaled_pixbuf)
        return image

    def toggle_sidebar(self, widget):
        """Toggle the sidebar's visibility, move icons, and position them to the left of the dropdown."""
        self.sidebar_expanded = not self.sidebar_expanded
        self.sidebar.set_visible(self.sidebar_expanded)

        # Remove icons from their current parent before re-adding
        self.collapse_icon.get_parent().remove(self.collapse_icon)
        self.new_convo_icon.get_parent().remove(self.new_convo_icon)

        if self.sidebar_expanded:
            # Move icons back to the sidebar and expand it
            self.icon_hbox.pack_start(self.collapse_icon, False, False, 0)
            self.icon_hbox.pack_end(self.new_convo_icon, False, False, 0)
            self.sidebar.show_all()
        else:
            # Move icons to the left of the dropdown in dropdown_hbox and collapse the sidebar
            self.sidebar.hide()
            self.dropdown_hbox.remove(self.model_dropdown)
            self.dropdown_hbox.pack_start(self.collapse_icon, False, False, 0)
            self.dropdown_hbox.pack_start(self.new_convo_icon, False, False, 0)
            self.dropdown_hbox.pack_start(self.model_dropdown, False, False, 0)

        # Refresh visibility and layout to ensure the icons appear in the new location
        self.dropdown_hbox.show_all()
        print("Sidebar toggled:", "Expanded" if self.sidebar_expanded else "Collapsed")  # Debugging line

    def on_new_conversation(self, widget):
        """Start a new conversation, reset the model choice, and handle sidebar state."""
        # Check if the sidebar is collapsed
        if not self.sidebar_expanded:
            # Move icons back to the sidebar and expand it
            self.collapse_icon.get_parent().remove(self.collapse_icon)
            self.new_convo_icon.get_parent().remove(self.new_convo_icon)
            self.icon_hbox.pack_start(self.collapse_icon, False, False, 0)
            self.icon_hbox.pack_end(self.new_convo_icon, False, False, 0)
            self.sidebar_expanded = True
            self.sidebar.set_visible(True)
            self.sidebar.show_all()

        # Set initial title to "New chat"
        self.current_conversation = "New chat"
        self.conversations[self.current_conversation] = []  # Initialize new conversation list
        self.chat_text_buffer.set_text("")  # Clear the chat display

        # Reset model selection to the default
        if self.model_dropdown.get_active_text():
            self.llm_choice = self.model_dropdown.get_active_text()

        self.render_conversations()

    def on_send_message(self, widget):
        """Send a message, get a response, save the conversation, and update the sidebar."""
        user_message = self.chat_entry.get_text().strip()
        if not user_message:
            return

        self.chat_entry.set_text("")
        self.append_message("User", user_message)

        if self.current_conversation and self.current_conversation not in self.conversations:
            self.conversations[self.current_conversation] = []

        self.conversations[self.current_conversation].append({"role": "user", "content": user_message})

        response = self.query_llm(user_message)
        self.append_message("Assistant", response)

        self.conversations[self.current_conversation].append({"role": "assistant", "content": response})
        self.save_conversations()

        # Query for the conversation title
        self.query_conversation_title(user_message)

    def query_conversation_title(self, user_message):
        """Send a query to the model to summarize and rename the conversation title."""
        summary_query = f"Summarize this GPT chat request in 3-5 words:\n{user_message}"
        url = "http://localhost:11434/api/chat"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = json.dumps({
            "model": self.llm_choice,
            "messages": [{"role": "user", "content": summary_query}],
            "stream": False
        }).encode("utf-8")

        req = Request(url, data=data, headers=headers, method="POST")

        try:
            with urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                new_title = result["message"]["content"]

                # Update title in the sidebar and in conversations dictionary without saving to conversations.json
                self.conversations[new_title] = self.conversations.pop(self.current_conversation)
                self.current_conversation = new_title
                self.render_conversations()
        except (HTTPError, URLError) as e:
            self.show_error_dialog(f"Error: {e.reason}")
        except Exception as e:
            self.show_error_dialog(str(e))

    def render_conversations(self):
        """Display conversation buttons in the sidebar."""
        # Clear all conversation buttons, but leave icon_hbox intact
        for widget in self.sidebar.get_children():
            if widget != self.icon_hbox:
                widget.destroy()

        # Add conversation buttons only (icon row already in place)
        for name in self.conversations.keys():
            button = Gtk.Button(label=name)
            button.connect("clicked", self.on_conversation_selected, name)
            self.sidebar.pack_start(button, False, False, 0)

        # Ensure sidebar visibility matches `sidebar_expanded`
        self.sidebar.set_visible(self.sidebar_expanded)
        self.sidebar.show_all()

    def on_conversation_selected(self, widget, name):
        """Load a conversation into the main chat window."""
        self.current_conversation = name
        self.chat_text_buffer.set_text("")
        for message in self.conversations[name]:
            self.append_message(message['role'], message['content'])

    def append_message(self, role, message):
        end_iter = self.chat_text_buffer.get_end_iter()
        self.chat_text_buffer.insert(end_iter, f"{role}: {message}\n")

    def query_llm(self, user_message):
        url = "http://localhost:11434/api/chat"
        headers = {
            "Content-Type": "application/json"
        }

        messages = self.conversations[self.current_conversation]
        data = json.dumps({
            "model": self.llm_choice,
            "messages": messages,
            "stream": False
        }).encode("utf-8")

        req = Request(url, data=data, headers=headers, method="POST")

        try:
            with urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["message"]["content"]
        except (HTTPError, URLError) as e:
            self.show_error_dialog(f"Error: {e.reason}")
        except Exception as e:
            self.show_error_dialog(str(e))
        return "An error occurred while querying the LLM."

    def load_conversations(self):
        """Load saved conversations."""
        try:
            with open("conversations.json", "r") as f:
                self.conversations = json.load(f)
        except FileNotFoundError:
            self.conversations = {}

    def save_conversations(self):
        """Save conversations to a JSON file."""
        with open("conversations.json", "w") as f:
            json.dump(self.conversations, f)

    def populate_model_dropdown(self):
        """Fetch the list of available models from the API and populate the dropdown."""
        url = "http://localhost:11434/api/tags"
        req = Request(url, method="GET")

        try:
            with urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
                for model in data.get("models", []):
                    self.model_dropdown.append_text(model["name"])
                self.model_dropdown.set_active(0)  # Select the first model by default
                self.llm_choice = self.model_dropdown.get_active_text()
        except (HTTPError, URLError) as e:
            error_message = f"Error fetching models: {e.reason}"
            self.show_error_dialog(error_message)
        except Exception as e:
            self.show_error_dialog(str(e))

    def on_model_changed(self, widget):
        """Update the model choice when the dropdown changes."""
        self.llm_choice = widget.get_active_text()

    def show_error_dialog(self, message):
        """Display an error message dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


def main():
    app = ChatApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

