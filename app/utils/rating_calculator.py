from typing import Tuple

# Default K-factor for Elo rating system
DEFAULT_K_FACTOR = 32

def calculate_elo_rating_change(winner_rating: float, loser_rating: float, k_factor: int = DEFAULT_K_FACTOR) -> Tuple[float, float]:
    """
    Calculate the Elo rating change for both players after a match.
    
    Args:
        winner_rating: Current rating of the winner
        loser_rating: Current rating of the loser
        k_factor: K-factor for the Elo calculation (default: 32)
        
    Returns:
        Tuple containing the new ratings for winner and loser
    """
    # Calculate expected scores
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    
    # Calculate new ratings
    new_winner_rating = winner_rating + k_factor * (1 - expected_winner)
    new_loser_rating = loser_rating + k_factor * (0 - expected_loser)
    
    return new_winner_rating, new_loser_rating


def get_initial_rating() -> float:
    """
    Get the initial rating for a new player.
    """
    return 1500.0
