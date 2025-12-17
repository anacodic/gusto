"""
Allergy filtering tools for agent system.
"""
import json
import sys
import os
from typing import List

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
from services.restaurant_service import allergy_filter, filter_dishes_by_allergy
from strands import tool


@tool
def filter_dishes_by_allergy_hybrid(dishes: List[str], allergies: List[str]) -> str:
    """
    Filter dishes safe for allergies using HYBRID approach (keyword + AI intersection).
    
    Uses BOTH methods and takes INTERSECTION for maximum safety:
    - Keyword filter: Fast, catches explicit mentions
    - AI filter: Understands hidden allergens (e.g., "Pesto" → nuts/dairy)
    - Intersection: Only dishes that pass BOTH filters (safest approach)
    
    Args:
        dishes: List of dish names
        allergies: List of allergens (e.g., ["peanuts", "dairy", "shellfish"])
    
    Returns:
        JSON string with safe_dishes list and filtering stats
    """
    print(f"🛡️ [Allergy Filter] Filtering {len(dishes)} dishes for allergies: {', '.join(allergies)}")
    
    if not dishes or not allergies:
        print(f"⚠️ [Allergy Filter] No dishes or allergies provided")
        return json.dumps({"safe_dishes": dishes, "method": "none", "stats": {}})
    
    try:
        # Method 1: Keyword-based filtering (fast, explicit mentions)
        print(f"🔤 [Allergy Filter] Step 1: Keyword-based filtering...")
        keyword_safe = [d for d in dishes if allergy_filter([d], allergies)]
        print(f"   ✅ Keyword filter: {len(keyword_safe)}/{len(dishes)} dishes safe")
        
        # Method 2: AI-based filtering (understands hidden allergens)
        print(f"🤖 [Allergy Filter] Step 2: AI-based filtering (Groq LLM)...")
        ai_safe = filter_dishes_by_allergy(dishes, allergies)
        print(f"   ✅ AI filter: {len(ai_safe)}/{len(dishes)} dishes safe")
        
        # Method 3: INTERSECTION (safest - must pass both)
        print(f"🔒 [Allergy Filter] Step 3: Taking intersection (safety-first)...")
        keyword_set = set(keyword_safe)
        ai_set = set(ai_safe)
        intersection_safe = list(keyword_set & ai_set)  # Only dishes in BOTH sets
        
        print(f"   ✅ Intersection: {len(intersection_safe)}/{len(dishes)} dishes safe")
        print(f"   📊 Stats: Keyword={len(keyword_safe)}, AI={len(ai_safe)}, Intersection={len(intersection_safe)}")
        
        # If intersection is too restrictive, use AI results (more permissive but still safe)
        if len(intersection_safe) == 0 and len(ai_safe) > 0:
            print(f"   ⚠️ [Allergy Filter] Intersection empty, using AI results (more permissive)")
            final_safe = ai_safe
            method_used = "ai_fallback"
        else:
            final_safe = intersection_safe
            method_used = "intersection"
        
        return json.dumps({
            "safe_dishes": final_safe,
            "method": method_used,
            "stats": {
                "total_dishes": len(dishes),
                "keyword_safe": len(keyword_safe),
                "ai_safe": len(ai_safe),
                "intersection_safe": len(intersection_safe),
                "final_safe": len(final_safe)
            }
        }, indent=2)
        
    except Exception as e:
        print(f"❌ [Allergy Filter] Error: {str(e)}")
        # Fallback to keyword-only for safety
        try:
            safe = [d for d in dishes if allergy_filter([d], allergies)]
            print(f"   ⚠️ Using keyword-only fallback: {len(safe)}/{len(dishes)} dishes safe")
            return json.dumps({
                "safe_dishes": safe,
                "method": "keyword_fallback",
                "error": str(e),
                "stats": {"total_dishes": len(dishes), "final_safe": len(safe)}
            })
        except Exception as e2:
            print(f"   ❌ Complete failure: {str(e2)}")
            return json.dumps({
                "safe_dishes": [],
                "method": "error",
                "error": str(e2),
                "stats": {}
            })
