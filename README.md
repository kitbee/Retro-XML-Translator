# Retro XML Translator

## Overview
The **Retro XML Translator** is a desktop application designed to translate text within XML files. It is particularly useful for translating game descriptions, metadata, or any other text content stored in XML format. The application supports multiple languages for both the user interface and the translation process.

## Features
- **Multi-language Support**: The user interface can be displayed in English, Russian, German, Italian, or French.
- **Auto-Detect Source Language**: The application can automatically detect the source language of the text.
- **Customizable Target Language**: Users can select the target language for translation.
- **Progress Tracking**: A progress bar shows the status of the translation process.
- **Save Settings**: The application remembers the last used interface and target languages.

## Supported Languages
### User Interface Languages
- English (`en`)
- Russian (`ru`)
- German (`de`)
- Italian (`it`)
- French (`fr`)

### Translation Languages
The application supports all languages supported by the Google Translate API.

## Installation
To run the Retro XML Translator, you need to install the following Python libraries:

```bash
pip install googletrans==4.0.0-rc1
pip install tkinter
pip install tqdm
```
## How to Run
Clone the repository:

```bash
git clone https://github.com/yourusername/retro-xml-translator.git
cd retro-xml-translator
Install the required libraries (see Installation above).
```
Run the application:

```bash
python retro_translator.py
```
How to Use
Select an XML File: Click the "Select XML File" button to choose the XML file you want to translate.

Choose Source and Target Languages: Use the dropdown menus to select the source and target languages. If the source language is unknown, select "Auto Detect."

Translate: Click the "Translate" button to start the translation process. The progress bar will show the status of the translation.

Save Translated File: The translated XML file will be saved as translated.xml in the same directory as the input file
