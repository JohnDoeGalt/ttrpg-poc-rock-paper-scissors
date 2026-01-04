# Setup Instructions

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the simulation:
   ```bash
   python simulation.py
   ```

## Gemini API Setup (Optional)

The Gemini API integration is optional and only needed if you want to analyze belief evolution after the simulation.

### Option 1: Environment Variable (Recommended)

Set your API key as an environment variable:

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows CMD:**
```cmd
set GEMINI_API_KEY=your_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your_key_here"
```

### Option 2: Edit File Locally

1. Copy `gemini_evolution.py.example` to `gemini_evolution.py` (if it doesn't exist)
2. Edit `gemini_evolution.py` and replace `"YOUR_API_KEY_HERE"` with your actual API key
3. Note: This file is in `.gitignore` so it won't be committed to version control

### Get Your API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Rate Limits

The free tier has rate limits (5 requests/minute per model). The code automatically handles this with:
- Automatic retry logic with delays
- 15-second delays between lineages
- Progress messages when waiting

For better performance, consider upgrading to a paid tier.

