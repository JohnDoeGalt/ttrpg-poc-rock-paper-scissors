"""
XAI API addon for simulating philosophical belief evolution through lineage splits.
This processes the final simulation state and shows how beliefs dilute through transitions.
"""
import os
import warnings
import time
import re
from typing import List, Dict
from components import RPSType
from lineage_registry import get_registry

# Try to import requests for API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False


# API Key Configuration
# SECURITY NOTE: Never commit your API key to version control!
# Set your API key as an environment variable: export XAI_API_KEY='your_key_here'
# Or edit this file locally (it's in .gitignore)
# Default API key (can be overridden by environment variable)
XAI_API_KEY = os.getenv("XAI_API_KEY", None)

# Original philosophies
ORIGINAL_BELIEFS = {
    RPSType.ROCK: "Rockism is the faith of the enduring self: the archetype of the Mountain, the Stoic, the Guardian who survives by becoming unmovable. Rockists believe reality is shaped by weight, patience, and refusal—by the quiet \"no\" that outlasts storms and arguments alike. Their virtue is steadfastness: to hold a line, to keep a promise, to become simple enough that nothing can hook you. But Rockism also teaches its own shadow: rigidity hardens into pride, and pride becomes a statue—beautiful, certain, and unable to bend. That is why Rockists speak of Paperism with wary respect: not as brute opposition, but as the humbling reminder that the strongest wall can be claimed, named, and rendered powerless by a single decisive wrapping of meaning.",
    RPSType.PAPER: "Paperism is the religion of the shaping mind: the archetype of the Scribe, the Weaver, the Lawgiver who conquers by defining. Paperists hold that the world is not ruled by force but by form—by names, contracts, rituals, maps, and stories that turn raw stone into \"property,\" \"history,\" \"duty,\" \"sin,\" \"home.\" Their virtue is discernment: to classify chaos, to bind power in symbols, to make the invisible legible and therefore governable. Yet Paperism knows its own danger: meaning can become mere surface, and cleverness can turn to denial—layers upon layers that smother truth until nothing breathes. So Paperists fear Scissorism as their necessary counterweight: the clean cut that exposes what's real, the sharp critique that slices through pretense, the moment when the page's authority is revealed as fragile fiber.",
    RPSType.SCISSORS: "Scissorism is the faith of decisive transformation: the archetype of the Blade, the Rebel, the Surgeon who saves by separating. Scissorists teach that life demands choice—not endless interpretation, not stubborn endurance, but the courage to cut away what no longer serves: lies from fact, excess from essence, attachment from purpose. Their virtue is clarity: the swift act that ends confusion, the disciplined incision that makes a new path. But Scissorism carries its own shadow: the hunger to cut can become cruelty, and clarity can become contempt—reducing living things to scraps. That is why Scissorists honor Rockism as a needed boundary: the hard limit that stops the blade, the reminder that some truths must be endured rather than dissected, and that without something solid to meet, even the sharpest edge eventually dulls into"
}

BELIEF_NAMES = {
    RPSType.ROCK: "Rockism",
    RPSType.PAPER: "Paperism",
    RPSType.SCISSORS: "Scissorism"
}

# API base URL
XAI_API_BASE_URL = "https://api.x.ai/v1"


def initialize_xai(api_key: str = None) -> bool:
    """
    Initialize the XAI API connection.
    Returns True if successful, False otherwise.
    """
    if not REQUESTS_AVAILABLE:
        print("\n" + "="*70)
        print("ERROR: requests library not installed!")
        print("="*70)
        print("\nTo use the XAI evolution addon:")
        print("1. Install requests: pip install requests")
        print("2. Get your API key from: https://console.x.ai")
        print("3. Set it as an environment variable:")
        print("   export XAI_API_KEY='your_key_here'")
        print("\n   Or edit xai_evolution.py and set XAI_API_KEY")
        print("   with your actual API key.")
        print("\n" + "="*70 + "\n")
        return False
    
    if api_key is None:
        api_key = XAI_API_KEY
    
    if api_key == "YOUR_API_KEY_HERE" or not api_key:
        print("\n" + "="*70)
        print("ERROR: XAI API key not configured!")
        print("="*70)
        print("\nTo use the XAI evolution addon:")
        print("1. Get your API key from: https://console.x.ai")
        print("2. Either set it as an environment variable:")
        print("   export XAI_API_KEY='your_key_here'")
        print("\n   Or edit xai_evolution.py and replace 'YOUR_API_KEY_HERE'")
        print("   with your actual API key.")
        print("\n" + "="*70 + "\n")
        return False
    
    # Test the API key by making a simple request
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # Just verify the key is set, don't make an actual API call yet
        return True
    except Exception as e:
        print(f"\nError initializing XAI API: {e}\n")
        return False


def generate_belief_evolution(current_belief: str, new_philosophy: str, 
                              new_philosophy_name: str) -> str:
    """
    Call XAI API to generate how a belief evolves when mixed with a new philosophy.
    Uses HTTP requests directly to the XAI API.
    
    Args:
        current_belief: The current (possibly mixed) belief statement
        new_philosophy: The new philosophy being adopted
        new_philosophy_name: Name of the new philosophy (e.g., "Scissorism")
    
    Returns:
        A new belief string that merges the two philosophies
    """
    if not REQUESTS_AVAILABLE:
        return f"[Error: requests library not available. The belief mixes with {new_philosophy_name}, but the exact synthesis could not be determined.]"
    
    api_key = XAI_API_KEY
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return f"[Error: XAI API key not configured. The belief mixes with {new_philosophy_name}, but the exact synthesis could not be determined.]"
    
    # Detailed prompt for better quality outputs
    user_prompt = f"""Merge these two philosophical belief systems into a new, evolved belief statement. The output must be substantial and meaningful.

First philosophy: "{current_belief}"

Second philosophy: "{new_philosophy}"

Create a new belief statement that:
- Is 5-6 sentences long (substantial, not brief)
- Synthesizes both philosophies into a unified, coherent worldview
- Shows how the new philosophy transforms, reinterprets, and builds upon the old one
- Uses rich religious/philosophical language with depth and nuance
- Demonstrates how beliefs evolve, dilute, and reinterpret through cultural transmission
- Feels like a natural philosophical evolution, not just a mechanical combination
- Contains specific ideas and concepts, not vague platitudes
- Shows the tension and synthesis between the two belief systems
- Creates a new practice within the system that neither had before

Write ONLY the new belief statement. Do not include any introductory text, labels, explanations, or formatting. Just the belief statement itself as a continuous paragraph."""

    try:
        # Use grok-3 (only available model - others are deprecated)
        model_name = 'grok-3'
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.9,
            "top_p": 0.95
        }
        
        # Retry logic for 503 (service unavailable) and timeouts
        max_retries = 5
        retry_delay = 10  # Start with 10 seconds
        response_data = None
        last_error = None
        last_status_code = None
        last_response_text = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{XAI_API_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                last_status_code = response.status_code
                last_response_text = response.text[:500]  # First 500 chars
                
                # Check for errors
                if response.status_code == 200:
                    response_data = response.json()
                    break  # Success, exit retry loop
                elif response.status_code == 503:
                    # Service unavailable - retry with exponential backoff
                    if attempt < max_retries - 1:
                        try:
                            error_json = response.json()
                            error_msg = error_json.get('error', {}).get('message', 'Service temporarily unavailable')
                        except:
                            error_msg = 'Service temporarily unavailable'
                        print(f"  Service at capacity (503). Waiting {retry_delay} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, 120)  # Exponential backoff, max 120 seconds
                        continue
                    else:
                        # Last attempt failed
                        response.raise_for_status()
                elif response.status_code in [401, 403]:
                    # Auth error - don't retry
                    response.raise_for_status()
                else:
                    # Other error - raise immediately
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"  Request timed out. Waiting {retry_delay} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 120)
                    continue
                else:
                    raise
            except requests.exceptions.RequestException as e:
                last_error = e
                error_str = str(e)
                # For non-503 errors, don't retry (except timeouts handled above)
                if "503" not in error_str and "timeout" not in error_str.lower():
                    raise
                elif attempt < max_retries - 1:
                    print(f"  Request error: {error_str[:200]}. Waiting {retry_delay} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 120)
                    continue
                else:
                    raise
        
        if response_data is None:
            error_details = []
            if last_status_code:
                error_details.append(f"Status: {last_status_code}")
            if last_response_text:
                error_details.append(f"Response: {last_response_text[:200]}")
            if last_error:
                error_details.append(f"Exception: {last_error}")
            error_msg = f"Could not get response from {model_name} after {max_retries} attempts. " + " | ".join(error_details) if error_details else f"Last error: {last_error}"
            raise Exception(error_msg)
        
        # Extract text from response
        text = None
        
        # XAI API response structure: response.choices[0].message.content
        if 'choices' in response_data and response_data['choices']:
            choice = response_data['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                text = choice['message']['content']
        
        # Fallback: try direct access
        if not text and 'choices' in response_data and response_data['choices']:
            try:
                text = response_data['choices'][0]['message']['content']
            except (KeyError, IndexError):
                pass
        
        if text:
            # Clean up the text - remove markdown formatting, labels, etc.
            cleaned_text = text.strip()
            
            # Remove common prefixes/formatting
            prefixes_to_remove = [
                "**Unified Belief Statement:**",
                "**Belief Statement:**",
                "Unified Belief Statement:",
                "Belief Statement:",
                "Here is a unified belief statement",
                "Here is the unified belief statement",
                "Here is the belief statement",
                "New belief statement:",
                "Belief:",
            ]
            
            for prefix in prefixes_to_remove:
                if cleaned_text.startswith(prefix):
                    cleaned_text = cleaned_text[len(prefix):].strip()
                    # Remove leading colon if present
                    if cleaned_text.startswith(":"):
                        cleaned_text = cleaned_text[1:].strip()
            
            # Remove markdown bold/italic
            cleaned_text = cleaned_text.replace("**", "").replace("*", "").replace("__", "").replace("_", "")
            
            # If the result is too short or looks like an error, return a fallback
            if len(cleaned_text) < 20 or cleaned_text.lower().startswith("here is") or cleaned_text.lower().startswith("from the"):
                # Try to extract meaningful content
                sentences = cleaned_text.split('.')
                meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
                if meaningful_sentences:
                    cleaned_text = '. '.join(meaningful_sentences)
                    if not cleaned_text.endswith('.'):
                        cleaned_text += '.'
            
            return cleaned_text if cleaned_text else text.strip()
        
        # If we get here, response format is unexpected
        print(f"Warning: Could not extract text from response. Response type: {type(response_data)}")
        print(f"Response structure: {response_data}")
        return f"[Error: Unexpected response format. The belief mixes with {new_philosophy_name}, but the exact synthesis could not be determined.]"
        
    except requests.exceptions.HTTPError as e:
        error_str = str(e)
        error_msg = f"{type(e).__name__}: {error_str}"
        
        # Handle rate limiting (429)
        if e.response and e.response.status_code == 429:
            print(f"  Rate limit hit: {error_msg}")
            # Extract retry delay from error if available
            retry_delay = 60  # Default 60 seconds for rate limits
            if e.response.headers.get('Retry-After'):
                try:
                    retry_delay = int(e.response.headers['Retry-After']) + 2
                except:
                    pass
            return f"[Error: Rate limit exceeded. Waiting {retry_delay:.1f} seconds. The belief mixes with {new_philosophy_name}, but the exact synthesis could not be determined at this time.]"
        
        print(f"Error calling XAI API: {error_msg}")
        return f"[Error: Could not generate evolution. The belief mixes with {new_philosophy_name}, but the exact synthesis could not be determined. Error: {error_msg}]"
        
    except Exception as e:
        error_str = str(e)
        error_msg = f"{type(e).__name__}: {error_str}"
        print(f"Error calling XAI API: {error_msg}")
        return f"[Error: Could not generate evolution. The belief mixes with {new_philosophy_name}, but the exact synthesis could not be determined. Error: {error_msg}]"


def process_lineage_evolution(lineage_path: List[str], interactive: bool = False) -> List[str]:
    """
    Process a single lineage path through all its transitions.
    
    Args:
        lineage_path: List of type names, e.g., ["rock", "paper", "scissors"]
        interactive: If True, pause after each API call for debugging
    
    Returns:
        List of belief statements showing evolution at each step
    """
    if not lineage_path:
        return []
    
    evolution = []
    
    # Start with the original philosophy
    first_type = RPSType(lineage_path[0])
    current_belief = ORIGINAL_BELIEFS[first_type]
    evolution.append(f"Original ({BELIEF_NAMES[first_type]}): {current_belief}")
    
    if interactive:
        print(f"\n  [START] Original belief ({BELIEF_NAMES[first_type]}):")
        print(f"    \"{current_belief}\"")
        input("  Press Enter to continue to first merge...")
    
    # Process each transition
    for i in range(1, len(lineage_path)):
        new_type = RPSType(lineage_path[i])
        new_philosophy = ORIGINAL_BELIEFS[new_type]
        new_philosophy_name = BELIEF_NAMES[new_type]
        
        if interactive:
            print(f"\n  [MERGE {i}/{len(lineage_path)-1}] Merging current belief with {new_philosophy_name}:")
            print(f"    Current belief: \"{current_belief}\"")
            print(f"    New philosophy ({new_philosophy_name}): \"{new_philosophy}\"")
            print(f"    Calling XAI API (via HTTP)...")
        
        # Generate the mixed belief
        mixed_belief = generate_belief_evolution(
            current_belief, 
            new_philosophy, 
            new_philosophy_name
        )
        
        if interactive:
            print(f"    Result: \"{mixed_belief}\"")
            if i < len(lineage_path) - 1:
                input(f"  Press Enter to continue to next merge...")
            else:
                print(f"  [COMPLETE] Lineage evolution finished.")
        
        evolution.append(f"After adopting {new_philosophy_name}: {mixed_belief}")
        current_belief = mixed_belief  # Next iteration uses the mixed version
    
    return evolution


def run_xai_evolution(num_rooms: int = 10, interactive: bool = False):
    """
    Main function to process all surviving lineages from the final simulation state.
    
    Args:
        num_rooms: Number of rooms (for context)
        interactive: If True, pause after each API call for debugging
    """
    if not initialize_xai():
        return
    
    if interactive:
        print("\n" + "="*70)
        print("INTERACTIVE MODE ENABLED")
        print("="*70)
        print("You will see each API call and must press Enter to continue.")
        print("This helps with debugging and monitoring the API responses.")
        print("="*70 + "\n")
    
    registry = get_registry()
    import esper
    from components import Person, Lineage
    
    # Get all unique surviving lineages (those with people in the final state)
    surviving_lineages = {}
    lineage_populations = {}
    
    for entity, person in esper.get_component(Person):
        lineage_id = None
        if esper.has_component(entity, Lineage):
            lineage = esper.component_for_entity(entity, Lineage)
            lineage_id = lineage.lineage_id
        
        if lineage_id not in lineage_populations:
            lineage_populations[lineage_id] = 0
        lineage_populations[lineage_id] += 1
    
    # Get unique lineage paths (group by path string)
    unique_paths = {}
    for lineage_id, count in lineage_populations.items():
        if lineage_id is None or lineage_id == 0:
            continue  # Skip base types (no lineage)
        
        path = registry.get_lineage_path(lineage_id)
        if path:
            path_str = " -> ".join(p.upper() for p in path)
            if path_str not in unique_paths:
                unique_paths[path_str] = {
                    'path': path,
                    'count': 0,
                    'lineage_id': lineage_id
                }
            unique_paths[path_str]['count'] += count
    
    if not unique_paths:
        print("\n" + "="*70)
        print("No lineages found in final state.")
        print("All people have base types with no evolutionary history.")
        print("="*70 + "\n")
        return
    
    print("\n" + "="*70)
    print("PHILOSOPHICAL BELIEF EVOLUTION ANALYSIS")
    print("="*70)
    print(f"\nProcessing {len(unique_paths)} unique lineage paths...")
    print("This may take a moment as we generate belief evolutions via XAI API.")
    print("Note: Rate limits may apply. Processing will include delays as needed.\n")
    
    # Process each unique lineage path
    results = []
    sorted_paths_list = sorted(unique_paths.items(), key=lambda x: -x[1]['count'])
    for idx, (path_str, path_data) in enumerate(sorted_paths_list):
        path = path_data['path']
        count = path_data['count']
        
        print(f"\n{'='*70}")
        print(f"Lineage: {path_str} ({count} people)")
        print(f"{'='*70}")
        
        if interactive:
            input(f"Press Enter to start processing this lineage...")
        
        evolution = process_lineage_evolution(path, interactive=interactive)
        
        for i, belief_statement in enumerate(evolution):
            print(f"\n{i+1}. {belief_statement}")
        
        results.append({
            'path': path_str,
            'count': count,
            'evolution': evolution
        })
        
        print()  # Blank line between lineages
        
        # Add a delay between lineages to help with rate limiting
        if idx < len(sorted_paths_list) - 1:  # Not the last one
            print(f"  Waiting 5 seconds before next lineage (rate limit protection)...")
            time.sleep(5)  # 5 second delay between lineages
    
    # Save detailed evolution report
    output_file = "belief_evolution_report.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("PHILOSOPHICAL BELIEF EVOLUTION REPORT\n")
        f.write("="*70 + "\n\n")
        
        for result in results:
            f.write(f"{'='*70}\n")
            f.write(f"Lineage: {result['path']} ({result['count']} people)\n")
            f.write(f"{'='*70}\n\n")
            
            for i, belief_statement in enumerate(result['evolution']):
                f.write(f"{i+1}. {belief_statement}\n\n")
            
            f.write("\n")
    
    # Save simplified lineage-to-belief mapping
    lineage_belief_file = "lineage_beliefs.txt"
    with open(lineage_belief_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("LINEAGE TO BELIEF MAPPING\n")
        f.write("="*70 + "\n\n")
        f.write("This file maps each unique lineage to its final evolved belief.\n\n")
        f.write("="*70 + "\n\n")
        
        for result in results:
            # Get the final evolved belief (last item in evolution list)
            final_belief = result['evolution'][-1] if result['evolution'] else "No evolution"
            # Extract just the belief text (remove the "After adopting X:" prefix if present)
            if ": " in final_belief:
                belief_text = final_belief.split(": ", 1)[1]
            else:
                belief_text = final_belief
            
            f.write(f"Lineage: {result['path']}\n")
            f.write(f"Population: {result['count']} people\n")
            f.write(f"Final Belief: {belief_text}\n")
            f.write("-" * 70 + "\n\n")
    
    print(f"\n{'='*70}")
    print(f"Evolution analysis complete!")
    print(f"Detailed report saved to: {output_file}")
    print(f"Lineage-to-belief mapping saved to: {lineage_belief_file}")
    print(f"{'='*70}\n")

