mkdir -p .devcontainer

cat <<EOL > .devcontainer/devcontainer.json
{
  "name": "BGDDOS",
  "image": "mcr.microsoft.com/devcontainers/python:1-3.12-bookworm",
  "features": {
    "ghcr.io/devcontainers/features/sshd:1": {
      "version": "latest"
    }
  },
  "postStartCommand": "cd /workspaces/BGDDOS && python3 -m venv .venv && . .venv/bin/activate && python -m pip install --upgrade pip && pip install pyTelegramBotAPI requests aiohttp certifi",
  "customizations": {
    "vscode": {
      "settings": {
        "python.defaultInterpreterPath": "/workspaces/BGDDOS/.venv/bin/python"
      },
      "extensions": [
        "ms-python.python"
      ]
    }
  }
}
EOL

git add .devcontainer/devcontainer.json
git commit -m "Fix devcontainer environment setup"
git push origin main
