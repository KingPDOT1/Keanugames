import tkinter as tk
from tkinter import messagebox
import random
import os
import time
import re

# NOTE: The 'google_search' tool is used for dynamic word generation.
# If running this code in a standard Python environment outside of the AI, 
# you will need to replace the calls to google_search with a static word list 
# or integrate a third-party search API.

# --- AI Word Pools for strategic uniqueness (Kept for AI behavior) ---
INNOCENT_WORDS_POOL = [
    "Digital", "Social", "Video", "Global", "Fashion", "Tech", "Food", "Sport", 
    "Stream", "Trendy", "Viral", "Modern", "Iconic", "Online", "Casual", "Luxury",
    "Creative", "Experience", "Service", "Platform", "Entertainment", "Fast", "Popular"
]

IMPOSTER_WORDS_POOL = [
    "Product", "Concept", "Thing", "Place", "Service", "Company", "Media", "Item", 
    "Expensive", "Famous", "Blue", "Yellow", "Red", "Green", "Big", "Small", "Abstract", 
    "Object", "Noun", "Business", "Name", "Idea", "Culture"
]

# --- Tool Integration Functions (Dynamic Word Generation) ---

def get_random_trending_topic():
    """Uses Google Search to get a random, current, and popular topic/brand."""
    print("Fetching random secret word from current popular topics...")
    try:
        # Search for a list of current trends/brands/topics
        search_result = google_search.search(queries=["current popular brands or trending topics 2024"])
        
        # Clean the search result to extract a list of potential words
        if search_result and hasattr(search_result, 'result'):
            text = search_result.result
            # Simple cleaning: split by common separators and filter for clean words/phrases
            keywords = re.findall(r'\b[A-Z][a-zA-Z\s\-]+(?=\s*[,\-\n]|$)', text)
            
            # Further filtering: Remove common filler words and single words that are too generic
            keywords = [w.strip() for w in keywords if w.strip() and len(w.split()) < 3 and len(w) > 3]
            keywords = list(set(keywords)) # Remove duplicates
            
            if keywords:
                # Select a random word/phrase
                return random.choice(keywords)

        print("Warning: Could not extract a clean list of trending topics. Falling back to default.")
        return random.choice(["Tesla", "Netflix", "ChatGPT", "Fortnite", "Starbucks"]) # Fallback to a well-known topic
    except Exception as e:
        print(f"Error fetching topic: {e}. Falling back to default.")
        return random.choice(["Disney", "Amazon", "YouTube", "Apple", "Spotify"]) # Fallback to a well-known topic

def get_word_description(word):
    """Uses Google Search to get a brief, one-line description of the secret word."""
    try:
        search_result = google_search.search(queries=[f"one sentence description of {word}"])
        
        if search_result and hasattr(search_result, 'result'):
            text = search_result.result
            # Try to extract the first full sentence
            match = re.search(r'[^.]*\.', text)
            if match:
                description = match.group(0).strip()
                # Clean up source mentions if present (e.g., "Wikipedia says...")
                if len(description) > 10 and len(description) < 200:
                    return description
            
            # Fallback: just return the first chunk of text
            return text[:200].replace('\n', ' ').strip() + "..."
            
        return "No specific description found."
    except Exception as e:
        print(f"Error fetching description: {e}")
        return "A popular entity or concept recently mentioned online."


# --- Helper Function for Innocent "Help" (Updated to use live search) ---
def get_secret_word_help(secret_word):
    """
    Provides 3 random, clean, unique words from a live search description 
    of the secret word.
    """
    # Perform a dedicated search for description/context
    description = get_word_description(secret_word)
    
    # 1. Clean the description and split into words
    cleaned_description = re.sub(r'[^\w\s]', '', description.lower())
    all_words = [word.capitalize() for word in cleaned_description.split() if word.strip() and word.lower() != secret_word.lower().lower() and len(word) > 2]
    
    # 2. Ensure words are unique
    unique_words = list(set(all_words))
    
    # 3. Select up to 3 words
    if len(unique_words) > 3:
        help_words = random.sample(unique_words, 3)
    else:
        # Fallback filler words if the description is too short/generic
        filler_words = random.sample([w for w in ["Internet", "Popular", "Famous", "Recent", "Concept", "Brand"] if w not in unique_words], max(0, 3 - len(unique_words)))
        help_words = unique_words + filler_words
        
    return help_words


# --- Shared AI/MIX Logic (Console Modes) ---

def generate_ai_response(player_data, secret_word, used_words):
    """Generates a unique ONE-WORD response for the AI players, avoiding used words."""
    role = player_data['role']
    secret_word_lower = secret_word.lower()
    
    # 1. Select the relevant pool based on role
    if role == "INNOCENT":
        primary_pool = INNOCENT_WORDS_POOL
        secret_word_initial = secret_word[0].lower()
        strategic_words = [w for w in primary_pool if w[0].lower() != secret_word_initial]
    else:
        primary_pool = IMPOSTER_WORDS_POOL
        strategic_words = primary_pool 
        
    # 2. Try words from the strategic pool first
    unique_strategic_words = [w for w in strategic_words if w.lower() not in used_words and w.lower() != secret_word_lower]
    
    if unique_strategic_words:
        return random.choice(unique_strategic_words)

    # 3. If strategic words are exhausted, fall back to generic words
    fallback_pool = ["Great", "Cool", "Fun", "Shiny", "New", "Old", "Everyday", "Unique"]
    unique_fallback_words = [w for w in fallback_pool if w.lower() not in used_words and w.lower() != secret_word_lower]

    if unique_fallback_words:
        return random.choice(unique_fallback_words)
        
    # 4. Critical failure 
    print(f"Warning: {player_data['name']} used an emergency fallback word.")
    return f"Word{random.randint(100, 999)}" 


def generate_ai_vote(players, imposter_index, current_player_index):
    """Generates a vote from an AI player. (This is where strategic voting happens for AIs)"""
    available_targets = [i for i in range(len(players)) if i != current_player_index]

    if players[current_player_index]['role'] == "INNOCENT":
        # AI Innocent votes randomly,
