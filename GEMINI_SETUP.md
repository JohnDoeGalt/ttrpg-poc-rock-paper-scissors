# Gemini API Setup Instructions

## Getting Your API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

## Setting Up the API Key

You have two options:

### Option 1: Environment Variable (Recommended)
Set the API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### Option 2: Direct Edit
Edit `gemini_evolution.py` and replace `"YOUR_API_KEY_HERE"` on line 15 with your actual API key:

```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_actual_api_key_here")
```

## Installing Dependencies

Make sure you have the required package installed:

```bash
pip install google-generativeai
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Usage

After running the simulation, you'll be asked:
```
Run Gemini API evolution analysis on final state? (Y/N):
```

Answer `Y` to process all surviving lineages through the Gemini API and generate belief evolution reports.

The results will be:
- Displayed in the console
- Saved to `belief_evolution_report.txt`

