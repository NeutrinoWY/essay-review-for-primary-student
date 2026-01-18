# UV Environment Setup Guide

This guide explains how to set up and update your uv environment for Python 3.13.

## Initial Setup

### 1. Install Python 3.13 via uv

```bash
uv python install 3.13
```

This downloads and installs Python 3.13 if not already available.

### 2. Pin Python 3.13 for this project

```bash
uv python pin 3.13
```

This creates a `.python-version` file that tells uv to use Python 3.13 for this project.

### 3. Create/Recreate the virtual environment

```bash
# Remove existing .venv if you want a fresh start
rm -rf .venv

# Create new virtual environment with Python 3.13
uv venv --python 3.13
```

### 4. Install dependencies

**Option A: Using pyproject.toml (Recommended)**
```bash
uv sync
```

**Option B: Using requirements.txt**
```bash
uv pip install -r requirements.txt
```

## Updating the Environment

### Update all packages to latest compatible versions

```bash
# Update packages based on pyproject.toml
uv sync --upgrade

# Or if using requirements.txt
uv pip install --upgrade -r requirements.txt
```

### Update specific package

```bash
# Using uv add (updates pyproject.toml automatically)
uv add --upgrade-package gradio

# Or using pip
uv pip install --upgrade gradio
```

### Recreate environment from scratch

If you want to completely rebuild the environment:

```bash
# Remove existing environment
rm -rf .venv

# Recreate with Python 3.13
uv venv --python 3.13

# Reinstall all packages
uv sync
```

## Running the Application

```bash
# Using uv run (automatically uses the project's virtual environment)
uv run app.py

# Or activate the environment manually
source .venv/bin/activate  # On macOS/Linux
python app.py
```

## Useful Commands

```bash
# Check Python version
uv run python --version

# List installed packages
uv pip list

# Check for outdated packages
uv pip list --outdated

# Update uv itself
uv self update
```

## Troubleshooting

If you encounter issues:

1. **Clear uv cache:**
   ```bash
   uv cache clean
   ```

2. **Reinstall Python 3.13:**
   ```bash
   uv python uninstall 3.13
   uv python install 3.13
   ```

3. **Verify Python version:**
   ```bash
   uv python list
   ```
