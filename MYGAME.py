import tkinter as tk
from tkinter import messagebox
import random
import os
import time
import re

# --- Global Word Bank (Now replaced by dynamic search) ---
# BRANDS is removed.

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

# --- Tool Integration Functions (New) ---

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
        filler_words = random.sample([w for w in ["Internet", "Popular", "Famous", "Recent", "Concept", "Brand"] if w not in unique_words], 3 - len(unique_words))
        help_words = unique_words + filler_words
        
    return help_words


# --- Shared AI/MIX Logic (No changes to functions that rely on AI logic) ---

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
        # AI Innocent votes randomly, could vote for the Imposter
        return random.choice(available_targets)
    else: 
        # AI Imposter tries to vote for an Innocent player to throw suspicion off themself
        innocent_targets = [i for i in available_targets if i != imposter_index]
        return random.choice(innocent_targets) if innocent_targets else random.choice(available_targets)


def end_game(outcome_type, secret_word, imposter_name, human_player_data=None):
    """
    Handles game conclusion and displays final messages, tailored by outcome and human role.
    """
    is_human_imposter = human_player_data and human_player_data['role'] == "IMPOSTER"
    is_human_innocent = human_player_data and human_player_data['role'] == "INNOCENT"
    
    message = ""
    
    if outcome_type == "IMPOSTER_GUESS_WIN":
        message = "IMPOSTER WINS by successfully guessing the word!"
        if is_human_imposter:
            message = "CONGRATULATIONS, YOU WIN! You correctly guessed the word!"
        elif is_human_innocent:
            message = "DEFEAT! The Imposter slipped away and guessed the word."
            
    elif outcome_type == "IMPOSTER_SURVIVED_WIN":
        message = "IMPOSTER WINS! The Innocents failed to catch them in time."
        if is_human_imposter:
            message = "CONGRATULATIONS, YOU WIN! You survived the vote and tricked the Innocents."
        elif is_human_innocent:
            message = "DEFEAT! You eliminated an innocent player, and the Imposter wins."

    elif outcome_type == "INNOCENT_CAUGHT_WIN":
        message = "INNOCENTS WIN! The Imposter was successfully identified and voted out."
        if is_human_imposter:
            message = "YOU LOSE! You were caught and voted out by the Innocents."
        elif is_human_innocent:
            message = "CONGRATULATIONS, YOU WIN! You successfully identified the Imposter."

    elif outcome_type == "TIED_VOTE_INNOCENT_WIN":
        message = "INNOCENTS WIN! The vote was tied, and the Imposter failed to secure a victory."
        if is_human_imposter:
            message = "YOU LOSE! The vote was a tie, and you failed to escape the round."
        elif is_human_innocent:
            message = "CONGRATULATIONS, YOU WIN! The vote was tied, saving the Innocents."

    print("\n" * 3)
    print("=" * 60)
    print("--- GAME OVER ---")
    print(f"\t\t*** {message} ***")
    print(f"The secret word was: **{secret_word}**")
    print(f"The Imposter was: **{imposter_name}**")
    print("=" * 60)
    return


# --- MODE 1 & 2: CONSOLE GAME (AI Only & MIXED) ---

def start_ai_game():
    """Starts the console game against only AIs."""
    
    print("\n" * 2)
    print("=" * 60)
    print("WELCOME TO IMPOSTER: HUMAN VS. AI (SOLO)")
    print("=" * 60)
    
    # --- Setup (Uses new dynamic word generator) ---
    num_ai_players = random.randint(3, 5) 
    num_total_players = num_ai_players + 1
    
    secret_word = get_random_trending_topic()
    secret_description = get_word_description(secret_word)
    imposter_index = random.randint(0, num_total_players - 1)
    
    human_name = input("Enter your player name: ")
    
    all_players_raw = [{'name': f"AI Player {i + 1}", 'type': 'AI'} for i in range(num_ai_players)]
    human_data = {'name': human_name, 'type': 'Human'}
    
    insertion_index = random.randint(0, num_total_players - 1)
    all_players_raw.insert(insertion_index, human_data)
    
    human_index = -1
    for i, player in enumerate(all_players_raw):
        player['role'] = "IMPOSTER" if i == imposter_index else "INNOCENT"
        if player['type'] == 'Human':
            human_index = i
            
    # --- Initial Role Reveal ---
    print("-" * 60)
    print(f"Game Setup Complete: {len(all_players_raw)} players total.")
    time.sleep(1)
    
    human_player_data = all_players_raw[human_index]
    
    print(f"Your role, {human_player_data['name']}, is: **{human_player_data['role']}**")
    if human_player_data['role'] == "INNOCENT":
        print(f"The SECRET WORD is: **{secret_word}**")
        print(f"Description: *{secret_description}*") 
        print(f"Image query for reference: ")
        print("Tip: Type 'help' during your turn for quick hints about the secret word!") 
    else:
        print("You are the IMPOSTER. Type 'guess' instead of a word to try and guess the secret word!")
    print("-" * 60)
    time.sleep(3)
    
    run_console_game_rounds(all_players_raw, secret_word, imposter_index, human_player_data)


def start_mix_game():
    """Starts the console game against human players and AIs."""
    
    print("\n" * 2)
    print("=" * 60)
    print("WELCOME TO IMPOSTER: MIXED MODE")
    print("=" * 60)
    
    # Get Human Player and AI counts
    while True:
        try:
            num_human_players = int(input("Enter number of HUMAN players (2 or more): "))
            if num_human_players < 2:
                print("Must be 2 or more human players.")
                continue
            break
        except ValueError:
            print("Invalid input.")

    while True:
        try:
            num_ai_players = int(input("Enter number of AI players (0 or more): "))
            if num_ai_players < 0:
                print("Must be 0 or more AI players.")
                continue
            break
        except ValueError:
            print("Invalid input.")

    num_total_players = num_human_players + num_ai_players
    if num_total_players < 3:
         print("Total players must be 3 or more for a meaningful game. Please try again.")
         return

    # --- Setup (Uses new dynamic word generator) ---
    secret_word = get_random_trending_topic() 
    secret_description = get_word_description(secret_word)
    imposter_index = random.randint(0, num_total_players - 1)
    
    # Build player list
    human_names = []
    for i in range(num_human_players):
        human_names.append(input(f"Enter name for Human Player {i + 1}: "))
    
    all_players_list = []
    for name in human_names:
        all_players_list.append({'name': name, 'type': 'Human'})
    for i in range(num_ai_players):
        all_players_list.append({'name': f"AI Player {i + 1}", 'type': 'AI'})
    
    for i, player in enumerate(all_players_list):
        player['role'] = "IMPOSTER" if i == imposter_index else "INNOCENT"
        
    random.shuffle(all_players_list)
    
    imposter_index = next(i for i, p in enumerate(all_players_list) if p['role'] == "IMPOSTER")
    
    # Find the current human player for end_game messaging (only relevant in solo/mix modes)
    current_human_player = next((p for p in all_players_list if p['type'] == 'Human'), None)

    # --- Initial Role Reveal (Fixed) ---
    print("-" * 60)
    print(f"Game Setup Complete: {len(all_players_list)} players total ({num_human_players} Human, {num_ai_players} AI).")
    time.sleep(1)
    
    print("\nRole Reveal Phase (Pass the device for private role check):")
    for i, player in enumerate(all_players_list):
        if player['type'] == 'Human':
            input(f"Player {player['name']}, press ENTER when you are ready to see your role...")
            print("\n" * 50) 
            print("=" * 30)
            
            print(f"Your role, {player['name']}, is: **{player['role']}**")
            if player['role'] == "INNOCENT":
                print(f"The SECRET WORD is: **{secret_word}**")
                print(f"Description: *{secret_description}*") 
                print(f"Image query for reference: ") 
                print("Tip: Type 'help' during your turn for quick hints about the secret word!")
            else:
                print("You are the IMPOSTER! Type 'guess' instead of a word to try and guess the secret word!")
                
            print("=" * 30)
            input("Press ENTER to clear screen and pass to the next human player.")
            print("\n" * 50) 

    print("All human players have seen their roles. Starting game...")
    print("-" * 60)
    time.sleep(2)
    
    run_console_game_rounds(all_players_list, secret_word, imposter_index, current_human_player)


def run_console_game_rounds(players, secret_word, imposter_index, human_player_data=None):
    """
    The core loop for AI and MIX modes.
    """
    all_players_raw = players
    
    elimination_round = 0
    # The game only goes through one round of descriptions and one vote.
    while len(all_players_raw) > 2 and elimination_round < 1: 
        elimination_round += 1
        
        all_responses = [] 
        used_words = set() 

        # 1. --- Response Collection (3 Sub-Rounds) ---
        for sub_round in range(1, 4):
            
            print(f"\n--- ELIMINATION ROUND {elimination_round}, RESPONSE SUB-ROUND {sub_round}/3 ---")
            
            current_sub_round_responses = []
            
            for i, player in enumerate(all_players_raw):
                time.sleep(0.5)
                
                if player['type'] == 'Human':
                    print("-" * 30)
                    print(f"Human Player {player['name']}'s turn (Word {sub_round}):")
                    valid_input = False
                    response = ""
                    while not valid_input:
                        raw_input = input("Your ONE-WORD description (or type 'guess' or 'help'): ").strip()
                        
                        # --- Imposter Guess Check ---
                        if raw_input.lower() == "guess":
                            if player['role'] == "IMPOSTER":
                                guess = input("Imposter, enter your guess for the secret word: ").strip()
                                # HIGHLIGHT GUESS
                                print(f"**[GUESS] {player['name']} guesses: {guess}**") 
                                
                                if guess.lower() == secret_word.lower():
                                    return end_game("IMPOSTER_GUESS_WIN", secret_word, player['name'], human_player_data)
                                else:
                                    print(f"Incorrect guess: {guess}. You must now provide a word description.")
                                    # Fall through to the regular response logic
                            else:
                                print("Only the Imposter can use the 'guess' command!")
                                continue
                        
                        # --- Innocent Help Check ---
                        elif raw_input.lower() == "help":
                            if player['role'] == "INNOCENT":
                                help_words = get_secret_word_help(secret_word)
                                if help_words:
                                    print(f"\n*** HINTS: {', '.join(help_words)} ***\n")
                                else:
                                    print("\n*** HINTS: No unique words available from the description. ***\n")
                                print("Now, provide your own unique one-word description.")
                                continue # Go back to the start of the while loop to get the actual response
                            else:
                                print("Only Innocent players can use the 'help' command!")
                                continue


                        response = raw_input 
                        
                        if len(response.split()) != 1:
                            print("Error: You must enter exactly ONE word.")
                        elif response.lower() == secret_word.lower():
                             print("Error: You cannot say the secret word!")
                        elif response.lower() in used_words: 
                             print(f"Error: The word '{response}' has already been used this round.")
                        else:
                            valid_input = True
                            
                    accepted_response = response
                        
                else: # AI Player
                    # AI does not have the 'guess' or 'help' feature
                    print(f"AI Player {player['name']}'s turn (Thinking...)")
                    accepted_response = generate_ai_response(player, secret_word, used_words)
                    
                    time.sleep(random.uniform(1, 2))
                    print(f"{player['name']}: {accepted_response}")

                
                used_words.add(accepted_response.lower()) 
                
                current_sub_round_responses.append({
                    'name': player['name'], 
                    'response': accepted_response, 
                    'sub_round': sub_round
                })
            
            all_responses.extend(current_sub_round_responses)


        # 2. --- Display All Responses and Vote Collection ---
        print("\n" * 1)
        print("=" * 60)
        print(f"--- VOTING PHASE: ELIMINATION ROUND {elimination_round} ---")
        print("=" * 60)
        
        # Display all responses from all 3 sub-rounds
        print("Player Summaries:")
        for i, player in enumerate(all_players_raw):
            print(f"  [{i+1}] {player['name']}: ", end="")
            player_responses = [r['response'] for r in all_responses if r['name'] == player['name']]
            print(f"Words: {', '.join(player_responses)}")
        print("-" * 60)
        
        # 3. Vote Collection
        votes = {} 
        
        for i, player in enumerate(all_players_raw):
            vote_index = -1
            if player['type'] == 'Human':
                # Human vote collection
                valid_vote = False
                while not valid_vote:
                    try:
                        vote = input(f"Player {player['name']}, who do you accuse? Enter player number (1 to {len(all_players_raw)}): ")
                        vote_index = int(vote) - 1 
                        
                        if 0 <= vote_index < len(all_players_raw) and vote_index != i: 
                            votes[vote_index] = votes.get(vote_index, 0) + 1
                            valid_vote = True
                        else:
                            print(f"Invalid number, or you cannot vote for yourself ({i+1}).")
                    except ValueError:
                        print("Invalid input.")
            
            else: # AI Vote
                vote_index = generate_ai_vote(all_players_raw, imposter_index, i)
                votes[vote_index] = votes.get(vote_index, 0) + 1
        
        # --- Display Vote Breakdown ---
        print("\n--- VOTE RESULTS ---")
        vote_breakdown = []
        for i, player in enumerate(all_players_raw):
            count = votes.get(i, 0)
            vote_breakdown.append(f"[{i+1}] {player['name']}: {count} votes")
        
        print(f"**Total Votes:** {', '.join(vote_breakdown)}")
        print("-" * 60)
                
        # Determine the outcome of the vote
        if not votes:
            print("No votes cast! Game continues.") 
        
        winning_vote_index = max(votes, key=votes.get)
        max_votes = votes[winning_vote_index]
        
        tied_players = [idx for idx, count in votes.items() if count == max_votes]
        
        if len(tied_players) > 1:
            print(f"\nVote is a TIE with {max_votes} votes! No one is eliminated.")
            # If there's a tie, the Imposter failed to rally enough support to get an Innocent out.
            return end_game("TIED_VOTE_INNOCENT_WIN", secret_word, all_players_raw[imposter_index]['name'], human_player_data)

        accused_player = all_players_raw[winning_vote_index]
        
        print(f"\nPlayer {winning_vote_index + 1} (**{accused_player['name']}**) was VOTED OUT with {max_votes} votes!")
        
        # Check if the Imposter was caught
        if accused_player['role'] == "IMPOSTER":
            # Innocents Win!
            imposter_name = accused_player['name']
            return end_game("INNOCENT_CAUGHT_WIN", secret_word, imposter_name, human_player_data)
        
        # Imposter not caught (an innocent person was eliminated)
        print(f"**{accused_player['name']}** was INNOCENT! They are eliminated.")
        
        # Imposter Wins! (They successfully tricked the innocents)
        return end_game("IMPOSTER_SURVIVED_WIN", secret_word, all_players_raw[imposter_index]['name'], human_player_data)
        
    # If the loop finishes without an outcome (shouldn't happen with the current 1-round rule)
    imposter_name = all_players_raw[imposter_index]['name']
    return end_game("Game Ended Prematurely.", secret_word, imposter_name)


# --- MODE 3: MULTI-PLAYER (Graphical User Interface) ---

class ImposterGameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Imposter Word Game (Player Mode)")
        
        # --- GUI FIX: Enable resizing/fullscreen and set min size ---
        self.master.resizable(True, True)
        self.master.minsize(500, 400) # Ensure a minimum readable size
        
        # self.brands is no longer used, we call the functions directly
        
        self.player_data = []  
        self.num_players = 0
        self.current_player_index = 0
        self.imposter_index = -1
        self.secret_word = ""
        self.secret_description = "" # Store description for use in GUI

        # Remove any previous bindings before setting up the first screen
        self.master.unbind('<Return>')
        
        self.setup_player_count_screen()

    # Helper function to process ENTER key bind for player count
    def bind_player_count_enter(self, event):
        self.process_player_count()
        
    # Helper function to process ENTER key bind for name input
    def bind_name_enter(self, event):
        self.save_name(self.name_entry.get())
        
    # Helper function to process ENTER key bind for role screen click
    def bind_move_to_next_player(self, event):
        self.move_to_next_player()
        
    # Helper function to process ENTER key bind for starting game discussion
    def bind_start_discussion(self, event):
        self.show_role_screen()


    def setup_player_count_screen(self):
        self.clear_frame()
        
        # Bind the Enter key to process the player count
        self.master.bind('<Return>', self.bind_player_count_enter)
        
        # Use a main frame to contain content and allow expansion
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text="Player Mode Setup", font=('Arial', 20, 'bold')).pack(pady=10)
        tk.Label(main_frame, text="Enter the total number of players (2 or more):", font=('Arial', 14)).pack(pady=20)
        
        self.player_count_entry = tk.Entry(main_frame, font=('Arial', 12), width=10)
        self.player_count_entry.pack(pady=10)
        
        # --- GUI FIX: Auto-focus the input box ---
        self.player_count_entry.focus_set()
        
        tk.Button(main_frame, text="Next", command=self.process_player_count, font=('Arial', 12)).pack(pady=20)

    def process_player_count(self):
        # Unbind the generic ENTER key command after input is processed
        self.master.unbind('<Return>')
        
        try:
            self.num_players = int(self.player_count_entry.get())
            if self.num_players < 2:
                messagebox.showerror("Invalid Input", "Please enter 2 or more players.")
                # Rebind the enter key since the state didn't change successfully
                self.master.bind('<Return>', self.bind_player_count_enter)
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            # Rebind the enter key
            self.master.bind('<Return>', self.bind_player_count_enter)
            return

        # --- Dynamic Word Generation for GUI Mode ---
        self.secret_word = get_random_trending_topic()
        self.secret_description = get_word_description(self.secret_word)
        self.imposter_index = random.randint(0, self.num_players - 1)
        self.player_data = [] 
        self.current_setup_player = 0
        self.setup_next_player_info()

    def setup_next_player_info(self):
        self.clear_frame()
        if self.current_setup_player >= self.num_players:
            self.start_player_turns()
            return

        player_num = self.current_setup_player + 1
        
        # Bind the Enter key to save the name
        self.master.bind('<Return>', self.bind_name_enter)
        
        # Use a main frame to contain content and allow expansion
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill='both')

        tk.Label(main_frame, text=f"Setup Player {player_num} / {self.num_players}", font=('Arial', 18, 'bold')).pack(pady=15)
        tk.Label(main_frame, text="Enter your name:", font=('Arial', 14)).pack(pady=10)
        
        self.name_entry = tk.Entry(main_frame, font=('Arial', 12), width=20)
        self.name_entry.pack(pady=10)
        
        # --- GUI FIX: Auto-focus the input box ---
        self.name_entry.focus_set()

        tk.Button(main_frame, text="Save Name & Continue", 
                  command=lambda: self.save_name(self.name_entry.get()), 
                  font=('Arial', 12)).pack(pady=20)

    def save_name(self, name):
        # Unbind the generic ENTER key command after input is processed
        self.master.unbind('<Return>')
        
        if not name.strip():
            messagebox.showerror("Error", "Please enter a name.")
            # Rebind the enter key
            self.master.bind('<Return>', self.bind_name_enter)
            return
        
        role = "IMPOSTER" if self.current_setup_player == self.imposter_index else "INNOCENT"

        self.player_data.append({
            'name': name,
            'role': role,
            'type': 'Human'
        })

        self.current_setup_player += 1
        self.setup_next_player_info()

    def start_player_turns(self):
        self.current_player_index = 0
        self.show_next_player_click_screen()

    def show_next_player_click_screen(self):
        self.clear_frame()

        if self.current_player_index == self.num_players:
            self.show_end_game_screen()
            return

        player_data = self.player_data[self.current_player_index]

        # Bind the Enter key to immediately proceed to the role screen
        self.master.bind('<Return>', self.bind_start_discussion)
        
        # Use a main frame to contain content and allow expansion
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill='both')

        tk.Label(main_frame, text=f"It is time for {player_data['name']}.", font=('Arial', 16)).pack(pady=10)
        tk.Label(main_frame, text="Click or press ENTER to see your secret identity.", font=('Arial', 18)).pack(pady=40)

        # Set focus to the root window so that the ENTER key press works correctly
        self.master.focus_set()
        
        tk.Button(main_frame, text="Click to Reveal",
                  command=self.show_role_screen, font=('Arial', 16), padx=20, pady=10).pack(pady=20)

    def show_role_screen(self):
        # Unbind the ENTER key press for this specific action
        self.master.unbind('<Return>')
        
        self.clear_frame()
        player_data = self.player_data[self.current_player_index]
        role = player_data['role']
        
        # Bind the Enter key to move to the next player
        self.master.bind('<Return>', self.bind_move_to_next_player)
        
        # Use a main frame to contain content and allow expansion
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill='both')
        
        tk.Label(main_frame, text=f"Your Role, {player_data['name']}:", font=('Arial', 16)).pack(pady=10)

        if role == "IMPOSTER":
            role_text = "IMPOSTER"
            details_text = "Your goal is to blend in! Pay attention to the Innocents' clues."
            color = "red"
        else:
            role_text = "INNOCENT"
            # Use the dynamically generated description
            details_text = f"The secret word is: **{self.secret_word}**\nDescription: *{self.secret_description}*" 
            color = "green"

        tk.Label(main_frame, text=role_text, font=('Arial', 36, 'bold'), fg=color).pack(pady=5)
        # Use wraplength on the description label
        tk.Label(main_frame, text=details_text, font=('Arial', 18), wraplength=500, justify='center').pack(pady=10)

        tk.Label(main_frame, text=f"Image query for reference: ", font=('Arial', 10)).pack(pady=5)
        tk.Label(main_frame, text="Click or press ENTER to hide and pass the device.", font=('Arial', 14)).pack(pady=15)

        tk.Button(main_frame, text="I've seen my role. Click to hide and pass the device.",
                  command=self.move_to_next_player, font=('Arial', 12)).pack(pady=5)
        
        # Set focus to the root window so that the ENTER key press works correctly
        self.master.focus_set()


    def move_to_next_player(self):
        # Unbind the ENTER key before changing screens
        self.master.unbind('<Return>')
        self.current_player_index += 1
        self.show_next_player_click_screen()

    def show_end_game_screen(self):
        self.clear_frame()
        
        # Bind the Enter key to reveal results
        self.master.bind('<Return>', lambda event: self.reveal_results())

        # Use a main frame to contain content and allow expansion
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill='both')

        tk.Label(main_frame, text="All roles revealed. Time to discuss!", font=('Arial', 18)).pack(pady=30)
        tk.Label(main_frame, text="Click or press ENTER to reveal the final results.", font=('Arial', 16)).pack(pady=10)
        tk.Button(main_frame, text="END (Reveal Results)",
                  command=self.reveal_results, font=('Arial', 24, 'bold'), padx=30, pady=15, bg='lightcoral').pack(pady=30)
        
        self.master.focus_set()


    def reveal_results(self):
        self.master.unbind('<Return>')
        self.clear_frame()
        
        # Use a main frame to contain content and allow expansion
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill='both')

        tk.Label(main_frame, text="--- FINAL REVEAL ---", font=('Arial', 24, 'bold'), fg='purple').pack(pady=10)

        tk.Label(main_frame, text="The secret word was:", font=('Arial', 16)).pack(pady=10)
        tk.Label(main_frame, text=f"**{self.secret_word}**", font=('Arial', 36, 'bold'), fg='blue').pack(pady=5)
        # Use the dynamically generated description
        tk.Label(main_frame, text=f"Description: *{self.secret_description}*", font=('Arial', 14), wraplength=500, justify='center').pack(pady=5)

        imposter_data = self.player_data[self.imposter_index]
        
        tk.Label(main_frame, text="The Imposter was:", font=('Arial', 16)).pack(pady=20)
        tk.Label(main_frame, text=f"**{imposter_data['name']}**", font=('Arial', 36, 'bold'), fg='red').pack(pady=5)

        tk.Button(main_frame, text="Play Again", command=self.setup_player_count_screen, font=('Arial', 14)).pack(pady=30)

    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()


# --- MAIN ENTRY POINT ---

def main():
    """Prompts user for input mode and starts the corresponding game."""
    print("Welcome to the Imposter Word Game!")
    mode = input('Enter "AI", "PLAYER", or "MIX" to choose the game mode: ').strip().upper()

    if mode == "AI":
        start_ai_game()
    elif mode == "MIX":
        start_mix_game()
    elif mode == "PLAYER":
        try:
            root = tk.Tk()
            ImposterGameGUI(root)
            root.mainloop()
        except Exception as e:
            print(f"\n--- FATAL ERROR IN PLAYER MODE (GUI) ---\n")
            print("Ensure tkinter is installed and accessible.")
            print(f"Error details: {e}")
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()
