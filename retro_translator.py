from tkinter import *
from tkinter import filedialog, ttk, messagebox
from googletrans import Translator
import xml.etree.ElementTree as ET
from tqdm import tqdm
import os
import time
import threading
import json

# Localizations for the interface
LOCALES = {
    'en': {
        'title': "Retro XML Translator",
        'select_file': "Select XML File",
        'no_file': "No file selected",
        'translate': "Translate",
        'status_ready': "Ready",
        'status_processing': "Processing...",
        'status_complete': "Translation complete!",
        'error_file': "Error: Select file first!",
        'language': "Interface Language",
        'src_lang': "Source Language",
        'trg_lang': "Target Language",
        'auto': "Auto Detect"
    },
    'ru': {
        'title': "Ретро Переводчик XML",
        'select_file': "Выбрать XML файл",
        'no_file': "Файл не выбран",
        'translate': "Перевести",
        'status_ready': "Готов",
        'status_processing': "Обработка...",
        'status_complete': "Перевод завершен!",
        'error_file': "Ошибка: Сначала выберите файл!",
        'language': "Язык интерфейса",
        'src_lang': "Исходный язык",
        'trg_lang': "Целевой язык",
        'auto': "Автоопределение"
    },
    'de': {
        'title': "Retro XML Übersetzer",
        'select_file': "XML-Datei auswählen",
        'no_file': "Keine Datei ausgewählt",
        'translate': "Übersetzen",
        'status_ready': "Bereit",
        'status_processing': "Wird verarbeitet...",
        'status_complete': "Übersetzung abgeschlossen!",
        'error_file': "Fehler: Zuerst Datei auswählen!",
        'language': "Oberflächensprache",
        'src_lang': "Ausgangssprache",
        'trg_lang': "Zielsprache",
        'auto': "Automatisch erkennen"
    },
    'it': {
        'title': "Traduttore XML Retro",
        'select_file': "Seleziona file XML",
        'no_file': "Nessun file selezionato",
        'translate': "Traduci",
        'status_ready': "Pronto",
        'status_processing': "Elaborazione...",
        'status_complete': "Traduzione completata!",
        'error_file': "Errore: Seleziona prima il file!",
        'language': "Lingua dell'interfaccia",
        'src_lang': "Lingua sorgente",
        'trg_lang': "Lingua di destinazione",
        'auto': "Rileva automaticamente"
    },
    'fr': {
        'title': "Traducteur XML Rétro",
        'select_file': "Sélectionner fichier XML",
        'no_file': "Aucun fichier sélectionné",
        'translate': "Traduire",
        'status_ready': "Prêt",
        'status_processing': "Traitement...",
        'status_complete': "Traduction terminée!",
        'error_file': "Erreur: Sélectionnez d'abord un fichier!",
        'language': "Langue de l'interface",
        'src_lang': "Langue source",
        'trg_lang': "Langue cible",
        'auto': "Détection automatique"
    }
}

LANGUAGE_FLAGS = {
    'en': '🇬🇧', 'ru': '🇷🇺', 'de': '🇩🇪', 'it': '🇮🇹', 'fr': '🇫🇷'
}

COLORS = {
    'background': '#000000',
    'foreground': '#00FF00',
    'widget_bg': '#002200',
    'active_bg': '#004400',
    'text': '#00FF00',
    'disabled': '#555555'
}

FONTS = {
    'title': ('Courier New', 18, 'bold'),
    'normal': ('Courier New', 12),
    'small': ('Courier New', 10)
}


class RetroTranslator:
    def __init__(self, master):
        self.master = master
        self.translator = Translator()
        self.current_ui_lang = 'en'
        self.target_lang = 'en'
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.master.configure(bg=COLORS['background'])
        self.master.geometry("800x600")

        # Language selection menu
        self.lang_menu = ttk.Combobox(self.master, values=self.get_language_options(),
                                      state='readonly', font=FONTS['normal'])
        self.lang_menu.set(f"{LANGUAGE_FLAGS[self.current_ui_lang]} {LOCALES[self.current_ui_lang]['language']}")
        self.lang_menu.pack(pady=10)
        self.lang_menu.bind('<<ComboboxSelected>>', self.change_ui_language)

        self.create_widgets()
        self.update_ui_texts()

    def create_widgets(self):
        # Title
        self.title_label = Label(
            self.master,
            font=FONTS['title'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        self.title_label.pack(pady=20)

        # Translation settings
        settings_frame = Frame(self.master, bg=COLORS['background'])
        settings_frame.pack(pady=10)

        # Source language selection
        self.src_lang = StringVar(value='auto')
        Label(settings_frame, font=FONTS['normal'],
              bg=COLORS['background'], fg=COLORS['text']).pack(side=LEFT)

        self.src_menu = ttk.Combobox(settings_frame, textvariable=self.src_lang,
                                     values=[LOCALES[self.current_ui_lang]['auto']] +
                                            [f"{flag} {name}" for code, (flag, name) in
                                             self.get_translate_language_options().items()],
                                     state='readonly')
        self.src_menu.pack(side=LEFT, padx=10)
        self.src_menu.current(0)

        # Target language selection
        self.trg_lang = StringVar(value='en')
        Label(settings_frame, font=FONTS['normal'],
              bg=COLORS['background'], fg=COLORS['text']).pack(side=LEFT)

        self.trg_menu = ttk.Combobox(settings_frame, textvariable=self.trg_lang,
                                     values=[f"{flag} {name}" for code, (flag, name) in
                                             self.get_translate_language_options().items()],
                                     state='readonly')
        self.trg_menu.pack(side=LEFT, padx=10)
        self.trg_menu.current(0)

        # File selection
        file_frame = Frame(self.master, bg=COLORS['background'])
        file_frame.pack(pady=20)

        self.select_btn = self.create_retro_button(
            file_frame,
            LOCALES[self.current_ui_lang]['select_file'],
            self.select_file,
            width=20
        )
        self.select_btn.pack(side=LEFT, padx=10)

        self.file_label = Label(file_frame, text=LOCALES[self.current_ui_lang]['no_file'],
                                font=FONTS['small'], fg=COLORS['text'], bg=COLORS['background'])
        self.file_label.pack(side=LEFT)

        # Progress bar
        self.progress = ttk.Progressbar(self.master, orient=HORIZONTAL,
                                        length=400, mode='determinate')
        self.progress.pack(pady=20)

        # Translate button
        self.translate_btn = self.create_retro_button(
            self.master,
            LOCALES[self.current_ui_lang]['translate'],
            self.start_translation,
            width=25
        )
        self.translate_btn.pack(pady=20)

        # Status label
        self.status_label = Label(self.master, text=LOCALES[self.current_ui_lang]['status_ready'],
                                  font=FONTS['small'], fg=COLORS['text'], bg=COLORS['background'])
        self.status_label.pack()

    def create_retro_button(self, parent, text, command, width=15):
        return Button(
            parent,
            text=text,
            command=command,
            font=FONTS['normal'],
            bg=COLORS['widget_bg'],
            fg=COLORS['text'],
            activebackground=COLORS['active_bg'],
            activeforeground=COLORS['text'],
            relief=RAISED,
            bd=3,
            width=width,
            padx=10,
            pady=5
        )

    def get_language_options(self):
        return [f"{LANGUAGE_FLAGS[code]} {LOCALES[code]['language']}" for code in LOCALES]

    def get_translate_language_options(self):
        return {
            code: (LANGUAGE_FLAGS[code], LOCALES[code]['language'])
            for code in LOCALES
        }

    def change_ui_language(self, event):
        selected = self.lang_menu.get()
        for code in LOCALES:
            if f"{LANGUAGE_FLAGS[code]} {LOCALES[code]['language']}" == selected:
                self.current_ui_lang = code
                self.save_settings()
                self.update_ui_texts()
                break

    def update_ui_texts(self):
        # Update all text elements
        self.master.title(LOCALES[self.current_ui_lang]['title'])
        self.title_label.config(text=f"> {LOCALES[self.current_ui_lang]['title'].upper()} <")
        self.lang_menu.set(f"{LANGUAGE_FLAGS[self.current_ui_lang]} {LOCALES[self.current_ui_lang]['language']}")
        self.select_btn.config(text=LOCALES[self.current_ui_lang]['select_file'])
        self.file_label.config(text=LOCALES[self.current_ui_lang]['no_file'])
        self.translate_btn.config(text=LOCALES[self.current_ui_lang]['translate'])
        self.status_label.config(text=LOCALES[self.current_ui_lang]['status_ready'])

        # Update translation language comboboxes
        translate_langs = self.get_translate_language_options()
        self.src_menu['values'] = [LOCALES[self.current_ui_lang]['auto']] + \
                                  [f"{flag} {name}" for code, (flag, name) in translate_langs.items()]
        self.trg_menu['values'] = [f"{flag} {name}" for code, (flag, name) in translate_langs.items()]

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
        if file_path:
            self.file_label.config(text=file_path)

    def start_translation(self):
        if not self.file_label.cget('text') or self.file_label.cget('text') == LOCALES[self.current_ui_lang]['no_file']:
            self.status_label.config(text=LOCALES[self.current_ui_lang]['error_file'])
            return

        src_lang = 'auto'
        if self.src_menu.get() != LOCALES[self.current_ui_lang]['auto']:
            for code in LOCALES:
                if f"{LANGUAGE_FLAGS[code]} {LOCALES[code]['language']}" == self.src_menu.get():
                    src_lang = code
                    break

        for code in LOCALES:
            if f"{LANGUAGE_FLAGS[code]} {LOCALES[code]['language']}" == self.trg_menu.get():
                self.target_lang = code
                break

        threading.Thread(
            target=self.process_xml,
            args=(self.file_label.cget('text'), "translated.xml", src_lang, self.target_lang),
            daemon=True
        ).start()

    def translate_text(self, text, src, dest):
        try:
            result = self.translator.translate(text, src=src, dest=dest)
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def process_xml(self, input_path, output_path, src_lang, trg_lang):
        self.update_status(LOCALES[self.current_ui_lang]['status_processing'])
        self.toggle_buttons(False)

        try:
            tree = ET.parse(input_path)
            root = tree.getroot()
            total = len(root.findall('.//game'))

            self.progress['maximum'] = total
            self.progress['value'] = 0

            for i, game in enumerate(root.findall('.//game')):
                desc = game.find('desc')
                if desc is not None and desc.text:
                    translated = self.translate_text(desc.text, src_lang, trg_lang)
                    desc.text = translated

                self.progress['value'] = i + 1
                self.master.update_idletasks()

            tree.write(output_path, encoding='utf-8')
            self.update_status(LOCALES[self.current_ui_lang]['status_complete'])

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.toggle_buttons(True)
            self.progress['value'] = 0

    def update_status(self, text):
        self.status_label.config(text=text)

    def toggle_buttons(self, state):
        self.select_btn.config(state=NORMAL if state else DISABLED)
        self.translate_btn.config(state=NORMAL if state else DISABLED)

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump({
                'ui_lang': self.current_ui_lang,
                'target_lang': self.target_lang
            }, f)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.current_ui_lang = settings.get('ui_lang', 'en')
                self.target_lang = settings.get('target_lang', 'en')
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    root = Tk()
    app = RetroTranslator(root)
    root.mainloop()