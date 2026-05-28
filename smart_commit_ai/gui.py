"""Tkinter desktop interface for Smart Commit AI."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from .config import LOCAL_ENV_PATH, load_api_key, save_api_key
from .service import SmartCommitService


class SmartCommitApp(tk.Tk):
    def __init__(self, service: SmartCommitService | None = None) -> None:
        super().__init__()
        self.title("Smart Commit AI")
        self.geometry("1120x720")
        self.minsize(900, 580)
        self.service = service or SmartCommitService()
        self.last_generation_source = ""
        self.last_generation_model = None
        self.last_generated_command = ""
        self.last_original_text = ""
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(14, 12, 14, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Provider").grid(row=0, column=0, padx=(0, 8), sticky="w")
        self.provider = tk.StringVar(value="auto")
        provider_box = ttk.Combobox(
            header,
            textvariable=self.provider,
            values=("auto", "gemini", "local"),
            width=10,
            state="readonly",
        )
        provider_box.grid(row=0, column=1, sticky="w")

        ttk.Label(header, text="Gemini API key").grid(row=0, column=2, padx=(20, 8), sticky="e")
        self.api_key = tk.StringVar(value=load_api_key())
        self.api_key_entry = ttk.Entry(header, textvariable=self.api_key, show="*", width=38)
        self.api_key_entry.grid(row=0, column=3, sticky="ew")

        self.save_examples = tk.BooleanVar(value=True)
        ttk.Checkbutton(header, text="Save training example", variable=self.save_examples).grid(
            row=0,
            column=4,
            padx=(16, 0),
            sticky="e",
        )

        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.grid(row=1, column=0, sticky="nsew", padx=14, pady=(4, 8))

        input_frame = ttk.Frame(main)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        ttk.Label(input_frame, text="Codex summary").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.input_text = tk.Text(input_frame, wrap="word", undo=True, height=20)
        self.input_text.grid(row=1, column=0, sticky="nsew")
        input_scroll = ttk.Scrollbar(input_frame, command=self.input_text.yview)
        input_scroll.grid(row=1, column=1, sticky="ns")
        self.input_text.configure(yscrollcommand=input_scroll.set)
        input_buttons = ttk.Frame(input_frame)
        input_buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(input_buttons, text="Paste", command=self.paste_input).pack(side=tk.LEFT)
        ttk.Button(input_buttons, text="Clear", command=self.clear_input).pack(side=tk.LEFT, padx=(8, 0))

        output_frame = ttk.Frame(main)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        ttk.Label(output_frame, text="Git commit command").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.output_text = tk.Text(output_frame, wrap="word", undo=True, height=20)
        self.output_text.grid(row=1, column=0, sticky="nsew")
        output_scroll = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        output_scroll.grid(row=1, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=output_scroll.set)
        output_buttons = ttk.Frame(output_frame)
        output_buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.create_button = ttk.Button(output_buttons, text="Create Commit", command=self.create_commit)
        self.create_button.pack(side=tk.LEFT)
        ttk.Button(output_buttons, text="Copy", command=self.copy_output).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(output_buttons, text="Save Example", command=self.save_current_example).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        main.add(input_frame, weight=1)
        main.add(output_frame, weight=1)

        self.status = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status, relief=tk.SUNKEN, anchor="w", padding=(10, 4))
        status_bar.grid(row=2, column=0, sticky="ew")

    def paste_input(self) -> None:
        try:
            value = self.clipboard_get()
        except tk.TclError:
            self.set_status("Clipboard is empty")
            return
        self.input_text.insert("insert", value)
        self.set_status("Pasted clipboard text")

    def clear_input(self) -> None:
        self.input_text.delete("1.0", tk.END)
        self.set_status("Input cleared")

    def create_commit(self) -> None:
        original = self.input_text.get("1.0", tk.END).strip()
        provider = self.provider.get()
        api_key = self.api_key.get().strip() or None
        save = self.save_examples.get()
        key_saved = False
        if api_key:
            try:
                save_api_key(api_key)
                key_saved = True
            except OSError as exc:
                self.show_message("Smart Commit AI", f"Could not save API key to {LOCAL_ENV_PATH}: {exc}")
                return

        self.set_status("Generating commit message...")
        self.create_button.configure(state=tk.DISABLED)
        self.update_idletasks()

        worker = threading.Thread(
            target=self._generate_in_background,
            args=(original, provider, api_key, save, key_saved),
            daemon=True,
        )
        worker.start()

    def _generate_in_background(
        self,
        original: str,
        provider: str,
        api_key: str | None,
        save: bool,
        key_saved: bool,
    ) -> None:
        try:
            result = self.service.generate(
                original,
                provider=provider,
                api_key=api_key,
                save=save,
            )
        except Exception as exc:  # GUI boundary: show actionable errors.
            self.after(0, lambda message=str(exc): self._generation_failed(message))
            return

        self.after(0, lambda: self._generation_finished(result, key_saved, original))

    def _generation_finished(self, result, key_saved: bool, original: str) -> None:
        self.create_button.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", result.command)
        self.last_generation_source = result.message.source
        self.last_generation_model = result.message.model
        self.last_generated_command = result.command
        self.last_original_text = original
        key_note = f" API key saved to {LOCAL_ENV_PATH}." if key_saved else ""
        if result.warning:
            self.set_status(result.warning + key_note)
        elif result.saved_path:
            self.set_status(f"Generated with {result.message.source}; saved {result.saved_path}.{key_note}")
        elif result.message.source != "gemini" and self.save_examples.get():
            self.set_status(f"Generated with {result.message.source}; not saved. Only Gemini outputs are saved.{key_note}")
        else:
            self.set_status(f"Generated with {result.message.source}.{key_note}")

    def _generation_failed(self, message: str) -> None:
        self.create_button.configure(state=tk.NORMAL)
        self.set_status("Generation failed")
        self.show_message("Smart Commit AI", message)

    def copy_output(self) -> None:
        command = self.output_text.get("1.0", tk.END).strip()
        if not command:
            self.set_status("Nothing to copy")
            return
        self.clipboard_clear()
        self.clipboard_append(command)
        self.set_status("Copied commit command")

    def save_current_example(self) -> None:
        original = self.input_text.get("1.0", tk.END).strip()
        output = self.output_text.get("1.0", tk.END).strip()
        if not original or not output:
            self.show_message("Smart Commit AI", "Input and output are required.")
            return
        if self.last_generation_source != "gemini":
            self.show_message("Smart Commit AI", "Only Gemini-generated commits can be saved.")
            return
        if output != self.last_generated_command or original != self.last_original_text:
            self.show_message("Smart Commit AI", "Only the unchanged Gemini-generated result can be saved.")
            return
        from .commit_message import parse_git_commit_command

        message = parse_git_commit_command(output)
        if message is None:
            self.show_message("Smart Commit AI", "Output must be a git commit command.")
            return
        path = self.service.store.save(original, message, source="gemini", model=self.last_generation_model)
        self.set_status(f"Saved {path}")

    def set_status(self, value: str) -> None:
        self.status.set(value)

    def show_message(self, title: str, message: str) -> None:
        dialog = SelectableMessageDialog(self, title=title, message=message)
        self.wait_window(dialog)


class SelectableMessageDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, title: str, message: str) -> None:
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.resizable(True, True)
        self.geometry("760x320")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        ttk.Label(container, text=title).grid(row=0, column=0, sticky="w", pady=(0, 8))

        text_frame = ttk.Frame(container)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text = tk.Text(text_frame, wrap="word", height=10)
        text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(text_frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.configure(yscrollcommand=scrollbar.set)
        text.insert("1.0", message)
        text.configure(state="disabled")

        buttons = ttk.Frame(container)
        buttons.grid(row=2, column=0, sticky="e", pady=(10, 0))

        def copy_message() -> None:
            parent.clipboard_clear()
            parent.clipboard_append(message)
            parent.update_idletasks()

        ttk.Button(buttons, text="Copy", command=copy_message).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(buttons, text="Close", command=self.destroy).pack(side=tk.LEFT)

        self.bind("<Escape>", lambda _event: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()


def main() -> None:
    app = SmartCommitApp()
    app.mainloop()


if __name__ == "__main__":
    main()
