"""
Gemini API addon for simulating philosophical belief evolution through lineage splits.
This processes the final simulation state and shows how beliefs dilute through transitions.
"""
import os
import warnings
import time
import re
from typing import List, Dict
from components import RPSType
from lineage_registry import get_registry

# Suppress deprecation warnings for google.generativeai and Python version warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='google.generativeai')
warnings.filterwarnings('ignore', category=FutureWarning, module='google.api_core')
warnings.filterwarnings('ignore', message='.*importlib.metadata.*')

# Try to import the new google.genai package, fall back to deprecated google.generativeai
try:
    import google.genai as genai
    USE_NEW_API = True
except ImportError:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import google.generativeai as genai
        USE_NEW_API = False
    except ImportError:
        genai = None
        USE_NEW_API = None


# API Key Configuration
# Put your Gemini API key here, or set it as an environment variable GEMINI_API_KEY
# SECURITY NOTE: Never commit your API key to version control!
# Use environment variable: export GEMINI_API_KEY='your_key_here'
# Or edit this file locally (it's in .gitignore)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Original philosophies
ORIGINAL_BELIEFS = {
    RPSType.ROCK: "Stand fast, take the hit, and let time prove what cannot be moved.",
    RPSType.PAPER: "Write the world into order—what is defined can be claimed, directed, and contained.",
    RPSType.SCISSORS: "Sever the needless and the untrue—one clean cut turns confusion into a path."
}

BELIEF_NAMES = {
    RPSType.ROCK: "Rockism",
    RPSType.PAPER: "Paperism",
    RPSType.SCISSORS: "Scissorism"
}


def initialize_gemini(api_key: str = None) -> bool:
    """
    Initialize the Gemini API client.
    Returns True if successful, False otherwise.
    """
    if api_key is None:
        api_key = GEMINI_API_KEY
    
    if api_key == "YOUR_API_KEY_HERE" or not api_key:
        print("\n" + "="*70)
        print("ERROR: Gemini API key not configured!")
        print("="*70)
        print("\nTo use the Gemini evolution addon:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Either set it as an environment variable:")
        print("   export GEMINI_API_KEY='your_key_here'")
        print("\n   Or edit gemini_evolution.py and replace 'YOUR_API_KEY_HERE'")
        print("   with your actual API key.")
        print("\n" + "="*70 + "\n")
        return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"\nError initializing Gemini API: {e}\n")
        return False


def generate_belief_evolution(current_belief: str, new_philosophy: str, 
                              new_philosophy_name: str) -> str:
    """
    Call Gemini API to generate how a belief evolves when mixed with a new philosophy.
    Uses a minimal, iterative approach - just merges two belief strings.
    
    Args:
        current_belief: The current (possibly mixed) belief statement
        new_philosophy: The new philosophy being adopted
        new_philosophy_name: Name of the new philosophy (e.g., "Scissorism")
    
    Returns:
        A new belief string that merges the two philosophies
    """
    # Detailed prompt for better quality outputs
    user_prompt = f"""Merge these two philosophical belief systems into a new, evolved belief statement. The output must be substantial and meaningful.

First philosophy: "{current_belief}"

Second philosophy: "{new_philosophy}"

Create a new belief statement that:
- Is 3-6 sentences long (substantial, not brief)
- Synthesizes both philosophies into a unified, coherent worldview
- Shows how the new philosophy transforms, reinterprets, and builds upon the old one
- Uses rich religious/philosophical language with depth and nuance
- Demonstrates how beliefs evolve, dilute, and reinterpret through cultural transmission
- Feels like a natural philosophical evolution, not just a mechanical combination
- Contains specific ideas and concepts, not vague platitudes
- Shows the tension and synthesis between the two belief systems

Write ONLY the new belief statement. Do not include any introductory text, labels, explanations, or formatting. Just the belief statement itself as a continuous paragraph."""

    try:
        # Try different model names - prioritize more capable models
        model = None
        # Use the models/ prefix format that the API expects
        # Prioritize PRO models for better quality outputs
        model_names = [
            'models/gemini-2.5-pro',        # Most capable - best quality
            'models/gemini-2.0-flash-exp',  # Experimental but capable
            'models/gemini-1.5-pro-latest', # Fallback pro model
            'models/gemini-2.5-flash',      # Fast but less capable
            'models/gemini-1.5-flash-latest', # Last resort
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # Test if it works by checking if we can access it
                break
            except Exception as e:
                continue
        
        if model is None:
            # Try to list available models for debugging
            try:
                available_models = [m.name for m in genai.list_models()]
                print(f"Available models: {available_models[:5]}...")  # Show first 5
            except:
                pass
            raise Exception("Could not create any Gemini model. Please check your API key and model availability.")
        
        # Use just the user prompt - no system prompt needed for this iterative approach
        full_prompt = user_prompt
        
        # Generate content - suppress warnings during API call
        # Add retry logic for rate limiting (free tier: 5 requests/minute)
        max_retries = 3
        retry_delay = 20  # seconds (free tier is 5 requests/minute = 12 seconds between requests)
        response = None
        
        for attempt in range(max_retries):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        response = model.generate_content(
                            full_prompt,
                            generation_config=genai.types.GenerationConfig(
                                max_output_tokens=500,  # Much higher for substantial, detailed responses
                                temperature=0.9,  # Higher for more creative and nuanced synthesis
                                top_p=0.95,  # Nucleus sampling for better quality
                                top_k=40  # Top-k sampling for diversity
                            )
                        )
                    except AttributeError:
                        # Fallback if GenerationConfig doesn't work
                        response = model.generate_content(full_prompt)
                break  # Success, exit retry loop
            except Exception as e:
                error_str = str(e)
                # Check if it's a rate limit error
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    if attempt < max_retries - 1:
                        # Extract retry delay from error if available
                        if "retry in" in error_str.lower():
                            try:
                                # Try to extract seconds from error message
                                match = re.search(r'retry in ([\d.]+)s', error_str.lower())
                                if match:
                                    retry_delay = float(match.group(1)) + 2  # Add 2 second buffer
                            except:
                                pass
                        
                        print(f"  Rate limit hit. Waiting {retry_delay:.1f} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        # Last attempt failed
                        raise
                else:
                    # Not a rate limit error, raise immediately
                    raise
        
        if response is None:
            raise Exception("Failed to generate response after retries")
        
        # Extract text from response - try multiple methods
        text = None
        
        # Method 1: Direct text attribute
        if hasattr(response, 'text') and response.text:
            text = response.text
        
        # Method 2: candidates[0].content.parts[0].text
        elif hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                if len(candidate.content.parts) > 0:
                    if hasattr(candidate.content.parts[0], 'text'):
                        text = candidate.content.parts[0].text
        
        # Method 3: candidates[0].text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'text'):
                text = candidate.text
        
        # Method 4: Try to get text from parts directly
        if not text and hasattr(response, 'candidates') and response.candidates:
            try:
                text = response.candidates[0].content.parts[0].text
            except (AttributeError, IndexError):
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
        print(f"Warning: Could not extract text from response. Response type: {type(response)}")
        print(f"Response structure: {response}")
        return f"[Error: Unexpected response format. The belief mixes with {new_philosophy_name}, but the exact synthesis could not be determined.]"
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"Error calling Gemini API: {error_msg}")
        # Only print full traceback in debug mode (comment out for production)
        # import traceback
        # print(f"Full traceback:\n{traceback.format_exc()}")
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
            print(f"    Calling Gemini API...")
        
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


def run_gemini_evolution(num_rooms: int = 10, interactive: bool = False):
    """
    Main function to process all surviving lineages from the final simulation state.
    
    Args:
        num_rooms: Number of rooms (for context)
        interactive: If True, pause after each API call for debugging
    """
    if not initialize_gemini():
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
    print("This may take a moment as we generate belief evolutions via Gemini API.")
    print("Note: Free tier has rate limits (5 requests/minute). Processing will include delays.\n")
    
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
        # Free tier allows 5 requests/minute, so we need ~12 seconds between requests
        # But we're doing multiple requests per lineage, so add a buffer
        if idx < len(sorted_paths_list) - 1:  # Not the last one
            print(f"  Waiting 15 seconds before next lineage (rate limit: 5 requests/minute)...")
            time.sleep(15)  # 15 second delay between lineages to stay under rate limit
    
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

