"""
Lineage visualization module for displaying lineage trees in a clear, intuitive format.
"""
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from lineage_registry import LineageRegistry, get_registry
from components import RPSType


def format_lineage_tree(registry: LineageRegistry, lineage_counts: Dict[Optional[int], int]) -> str:
    """
    Create a formatted tree visualization of lineages.
    
    Args:
        registry: The lineage registry
        lineage_counts: Dict mapping lineage_id to count of people with that lineage
    
    Returns:
        Formatted string showing the lineage tree
    """
    # Filter out None/0 lineages (base types)
    active_lineages = {lid: count for lid, count in lineage_counts.items() 
                      if lid is not None and lid != 0 and count > 0}
    
    if not active_lineages:
        return ""
    
    # Group lineages by their path string for better organization
    path_groups: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
    
    for lineage_id, count in active_lineages.items():
        path_str = registry.get_lineage_string(lineage_id)
        path_groups[path_str].append((lineage_id, count))
    
    # Build tree structure
    lines = []
    lines.append("+- Lineage Tree " + "-" * 50 + "+")
    
    # Sort paths by depth (shorter first) then by count
    sorted_paths = sorted(path_groups.items(), 
                         key=lambda x: (len(x[0].split(" -> ")), -sum(c for _, c in x[1])))
    
    for path_str, lineage_list in sorted_paths:
        total_count = sum(count for _, count in lineage_list)
        path_parts = path_str.split(" -> ")
        
        # Format based on depth
        if len(path_parts) == 2:
            # Simple split: rock -> paper
            lines.append(f"|  {path_parts[0].upper():8} ---> {path_parts[1].upper():8}  [{total_count:3} people]")
        else:
            # Multi-level: show as tree
            indent = "|  "
            for i, part in enumerate(path_parts):
                if i == 0:
                    lines.append(f"|  {part.upper():8}")
                elif i == len(path_parts) - 1:
                    # Last part - show count
                    connector = "+->" if i > 1 else "-->"
                    lines.append(f"{indent}{connector} {part.upper():8}  [{total_count:3} people]")
                else:
                    connector = "|->" if i < len(path_parts) - 1 else "+->"
                    lines.append(f"{indent}{connector} {part.upper():8}")
                    indent += "   "
    
    lines.append("+" + "-" * 64 + "+")
    
    return "\n".join(lines)


def format_lineage_summary(registry: LineageRegistry, lineage_counts: Dict[Optional[int], int]) -> str:
    """
    Create a compact summary of lineages grouped by path.
    
    Args:
        registry: The lineage registry
        lineage_counts: Dict mapping lineage_id to count of people with that lineage
    
    Returns:
        Formatted string showing lineage summary
    """
    # Filter out None/0 lineages
    active_lineages = {lid: count for lid, count in lineage_counts.items() 
                      if lid is not None and lid != 0 and count > 0}
    
    if not active_lineages:
        return ""
    
    # Group by path and sum counts
    path_totals: Dict[str, int] = defaultdict(int)
    
    for lineage_id, count in active_lineages.items():
        path_str = registry.get_lineage_string(lineage_id)
        path_totals[path_str] += count
    
    # Format as a nice list
    lines = []
    lines.append("Active Lineages:")
    
    # Sort by count (descending)
    sorted_paths = sorted(path_totals.items(), key=lambda x: -x[1])
    
    for path_str, total_count in sorted_paths:
        # Use simple ASCII arrows
        path_parts = path_str.split(" -> ")
        if len(path_parts) == 2:
            # Simple: rock -> paper
            lines.append(f"   {path_parts[0].upper():8} -> {path_parts[1].upper():8}  : {total_count:3} people")
        else:
            # Multi-level: show with indentation
            formatted_path = " -> ".join(p.upper() for p in path_parts)
            lines.append(f"   {formatted_path:30}  : {total_count:3} people")
    
    return "\n".join(lines)


def format_lineage_tree_compact(registry: LineageRegistry, lineage_counts: Dict[Optional[int], int]) -> str:
    """
    Create a compact tree visualization using box-drawing characters.
    """
    active_lineages = {lid: count for lid, count in lineage_counts.items() 
                      if lid is not None and lid != 0 and count > 0}
    
    if not active_lineages:
        return ""
    
    # Group by path
    path_groups: Dict[str, int] = defaultdict(int)
    for lineage_id, count in active_lineages.items():
        path_str = registry.get_lineage_string(lineage_id)
        path_groups[path_str] += count
    
    lines = []
    lines.append("=" * 65)
    lines.append("                    Lineage Evolution Tree                    ".center(65))
    lines.append("=" * 65)
    
    # Sort by depth then count
    sorted_paths = sorted(path_groups.items(), 
                         key=lambda x: (len(x[0].split(" -> ")), -x[1]))
    
    for path_str, total_count in sorted_paths:
        path_parts = path_str.split(" -> ")
        
        if len(path_parts) == 2:
            # Two-level: simple arrow
            lines.append(f"  {path_parts[0].upper():10} ------> {path_parts[1].upper():10}  ({total_count:3})")
        else:
            # Multi-level: tree structure
            for i, part in enumerate(path_parts):
                if i == 0:
                    prefix = "  "
                    suffix = " --"
                elif i == len(path_parts) - 1:
                    prefix = "     " + "    " * (i - 1) + "+-> "
                    suffix = f"  ({total_count:3})"
                else:
                    prefix = "     " + "    " * (i - 1) + "|-> "
                    suffix = ""
                
                lines.append(f"{prefix}{part.upper():10}{suffix}")
    
    lines.append("=" * 65)
    
    return "\n".join(lines)

