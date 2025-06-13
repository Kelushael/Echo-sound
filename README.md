# Echo-sound

This repository initially contained a setup script directly embedded in the README. The script has now been moved to `setup_repo.sh`.

`Echo-sound` aims to be a GUI application for audio file processing using Python's `tkinter` library. It will let users load audio files, separate them into stems using the `demucs` model, generate mixing instructions with GPT-4, and apply basic mixing to create a final audio mix. Integration with Logic Pro and narration via ElevenLabs are also planned.

## Getting started
1. Clone the repository:
   ```sh
   git clone https://github.com/Kelushael/kelushael-studio-mixer.git
   cd kelushael-studio-mixer
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. (Optional) Run the setup script to initialise a new repository:
   ```sh
   bash setup_repo.sh
   ```

The script will create a `.gitignore`, generate a project README and optionally create the GitHub repository if it does not exist.

## License
MIT
