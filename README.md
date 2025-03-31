# Echo-sound#!/bin/bash

# Replace with your GitHub username and repository name
GITHUB_USERNAME="Kelushael"
REPO_NAME="kelushael-studio-mixer"

# Replace with your API keys
OPENAI_API_KEY="your_openai_api_key_here"
ELEVENLABS_API_KEY="your_elevenlabs_api_key_here"

# Function to initialize the Git repository
initialize_git() {
    echo "[INFO] Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git
    git push -u origin main
}

# Function to create .gitignore file
create_gitignore() {
    echo "[INFO] Creating .gitignore file..."
    cat <<EOF > .gitignore
__pycache__/
*.pyc
input_audio/
output_mix/
temp_processing/
.env
EOF
    git add .gitignore
    git commit -m "Add .gitignore"
    git push
}

# Function to create README.md file
create_readme() {
    echo "[INFO] Creating README.md file..."
    cat <<EOF > README.md
# Kelushael Studio Mixer

This project is a GUI application for audio file processing using Python's \`tkinter\` library. It allows users to load audio files, separate them into stems using the \`demucs\` model, query GPT-4 for mixing instructions, and apply basic mixing to create a final audio mix. It also integrates with Logic Pro for automatic import and ElevenLabs for narration.

## Features
- Load and process audio files
- Separate audio into stems using \`demucs\`
- Query GPT-4 for mixing instructions
- Apply basic mixing to audio stems
- Export final mix
- Auto-import mix into Logic Pro
- Narrate mixing instructions using ElevenLabs

## Installation
1. Clone the repository:
   \`\`\`sh
   git clone https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git
   cd ${REPO_NAME}
   \`\`\`

2. Install the required dependencies:
   \`\`\`sh
   pip install -r requirements.txt
   \`\`\`

3. Set your API keys in the \`.env\` file:
   \`\`\`plaintext
   OPENAI_API_KEY=${OPENAI_API_KEY}
   ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
   \`\`\`

## Usage
Run the application:
\`\`\`sh
python kelushael_mixer_autopilot.py
\`\`\`

## License
This project is licensed under the MIT License.
EOF
    git add README.md
    git commit -m "Add README.md"
    git push
}

# Check if the repository already exists
echo "[INFO] Checking if repository exists..."
if ! git ls-remote https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git &>/dev/null; then
    echo "[INFO] Creating new repository on GitHub..."
    curl -u "${GITHUB_USERNAME}" https://api.github.com/user/repos -d "{\"name\":\"${REPO_NAME}\"}"
fi

# Run the functions
initialize_git
create_gitignore
create_readme

echo "[INFO] Setup complete!"