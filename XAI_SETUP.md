# XAI API Setup Instructions

## Getting Your API Key

1. Go to: https://console.x.ai
2. Sign in with your account
3. Navigate to settings to generate your API key
4. Copy your API key

## Setting Up the API Key

You have two options:

### Option 1: Environment Variable (Recommended)

Set the API key as an environment variable:

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

1. Edit `xai_evolution.py` directly and set `XAI_API_KEY` with your actual API key (replace the default value on line 28)
2. Note: This file is in `.gitignore` so it won't be committed to version control

## Installing Dependencies

Make sure you have the required package installed:

```bash
pip install requests
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Usage

After running the simulation, you'll be asked:
```
Run XAI API evolution analysis on final state? (Y/N):
```

Answer `Y` to process all surviving lineages through the XAI API and generate belief evolution reports.

The results will be:
- Displayed in the console
- Saved to `belief_evolution_report.txt`
- Saved to `lineage_beliefs.txt`

## Rate Limits

Rate limits may apply depending on your API tier. The code automatically handles this with:
- Automatic retry logic with delays
- 5-second delays between lineages
- Progress messages when waiting

For better performance, consider upgrading to a paid tier.

