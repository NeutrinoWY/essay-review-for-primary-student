# Primary Student Essay Reviewer

A Gradio and AI-based tool for reviewing primary school students' essays. It can recognize essay content from hand-writings in images and provide detailed review feedback.

## Features

- 📸 **Image Upload**: Support for uploading images containing essays
- 🔍 **Text Recognition**: Automatically recognizes text in images using Gemini/OpenAI Vision model
- ✍️ **Smart Review**: Provides structured review feedback, including:
  - Word error identification
  - Grammar error checking
  - Expression optimization suggestions (suitable for primary school level)
  - Overall evaluation

## Installation Steps

### Using uv (Recommended)

1. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install Python 3.13 via uv:
```bash
uv python install 3.13
```

3. Pin Python 3.13 for this project:
```bash
uv python pin 3.13
```

4. Clone or download the project to your local machine

5. Create virtual environment and install dependencies:
```bash
# Create virtual environment with Python 3.13
uv venv --python 3.13

# Install dependencies (recommended - uses pyproject.toml)
uv sync

# Or install from requirements.txt
uv pip install -r requirements.txt
```

6. Set up API Key:

Create a `.env` file:
```
GOOGLE_API_KEY=your-api-key
OPENAI_API_KEY=your-openai-api-key
```


## Usage

1. Run the application:
```bash
# With uv
uv run app.py

# or
uv run python app.py

```

2. Open the displayed address in your browser (usually `http://localhost:7860`)

3. Upload an image containing the essay

4. Click the "Recognize and Analyze" button to get the recognized text and essay review

## Tech Stack

- **Gradio**: For building the simple user interface
- **OpenAI**: For calling OpenAI or Gemini API

## API Notes

This application uses the `OpenAI` library to call the Gemini or OpenAI API, with code structured following OpenAI client patterns (`chat.completions.create()` calls). 

## Updating the UV Environment

To update packages in your uv environment:

```bash
# Update all packages to latest compatible versions
uv sync --upgrade

# Or update from requirements.txt
uv pip install --upgrade -r requirements.txt
```

For more detailed uv setup and update instructions, see [UV_SETUP.md](UV_SETUP.md).

## Notes

- Make sure you have obtained a GOOGLE API Key or OPENAI API KEY
- Supported image formats: JPG, PNG, and other common formats
- Recommended: Use clear images with easily recognizable text
- This project requires Python 3.13 or higher

## License

MIT License
