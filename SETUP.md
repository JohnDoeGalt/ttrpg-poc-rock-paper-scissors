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

## XAI API Setup (Optional)

The XAI API integration is optional and only needed if you want to analyze belief evolution after the simulation.

### Option 1: Environment Variable (Recommended)

Set your API key as an environment variable:

**Windows PowerShell:**
```powershell
$env:XAI_API_KEY="your_api_key_here"
```

**Windows CMD:**
```cmd
set XAI_API_KEY=your_key_here
```

**Linux/Mac:**
```bash
export XAI_API_KEY="your_key_here"
```

### Option 2: Edit File Locally

1. Edit `xai_evolution.py` directly and set `XAI_API_KEY` with your actual API key (change `None` to your API key string on line 35)
   ```python
   XAI_API_KEY = os.getenv("XAI_API_KEY", "your_actual_api_key_here")
   ```
2. Note: This file is in `.gitignore` so it won't be committed to version control

### Get Your API Key

1. Go to: https://console.x.ai
2. Sign in with your account
3. Navigate to settings to generate your API key
4. Copy your API key

### Rate Limits

Rate limits may apply depending on your API tier. The code automatically handles this with:
- Automatic retry logic with delays
- 5-second delays between lineages
- Progress messages when waiting

For better performance, consider upgrading to a paid tier.

