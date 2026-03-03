#!/usr/bin/env python3
"""Test suite for Blackjack game.

This module contains comprehensive tests for the Blackjack game implementation,
including tests for:
- BlackjackHand: Card value calculation, Ace handling, and bust detection
- Player: Player and dealer initialization, card receiving, and hand display
- BlackjackGame: Game initialization, card dealing, and winner determination
- Edge cases: Complex hand scenarios and boundary conditions

The tests verify that Blackjack rules are correctly implemented, including:
- Face cards (J, Q, K) valued at 10
- Aces valued at 11 or 1 (whichever is better)
- Hands exceeding 21 are busted
- Blackjack (21 with two cards) detection
"""

import pytest
from blackjack import BLACKJACK, BlackjackGame, BlackjackHand, GameStatus, Player
from cards import Card


class TestBlackjackHand:
    """Tests for the BlackjackHand class.
    
    This test class verifies the functionality of the BlackjackHand class,
    including card value calculation, Ace value adjustment, bust detection,
    and proper handling of edge cases like multiple Aces.
    """

    def test_hand_initialization(self):
        """Test that a hand is initialized with one card.
        
        Verifies that a BlackjackHand is created with exactly one card and that
        the card is accessible through the cards property.
        """
        card = Card("5", "Hearts")
        hand = BlackjackHand(card)
        assert len(hand.cards) == 1
        assert hand.cards[0] == card

    def test_add_card(self):
        """Test adding cards to a hand.
        
        Verifies that the add_card method successfully adds cards to an existing hand.
        """
        hand = BlackjackHand(Card("5", "Hearts"))
        hand.add_card(Card("King", "Diamonds"))
        assert len(hand.cards) == 2

    def test_hand_value_simple(self):
        """Test hand value calculation for simple cards.
        
        Verifies that numeric cards are valued at their face value in Blackjack.
        """
        hand = BlackjackHand(Card("5", "Hearts"))
        hand.add_card(Card("7", "Diamonds"))
        assert hand.value == 12

    def test_hand_value_face_cards(self):
        """Test that face cards (J, Q, K) are worth 10.
        
        Verifies that Jack, Queen, and King cards are all valued at 10 points
        in Blackjack.
        """
        hand = BlackjackHand(Card("King", "Hearts"))
        hand.add_card(Card("Queen", "Diamonds"))
        assert hand.value == 20

        hand2 = BlackjackHand(Card("Jack", "Clubs"))
        hand2.add_card(Card("5", "Spades"))
        assert hand2.value == 15

    def test_hand_value_ace_as_eleven(self):
        """Test that Ace counts as 11 when it doesn't cause bust.
        
        Verifies that an Ace is valued at 11 when that value keeps the hand
        at or below 21.
        """
        hand = BlackjackHand(Card("Ace", "Hearts"))
        hand.add_card(Card("9", "Diamonds"))
        assert hand.value == 20

    def test_hand_value_ace_as_one(self):
        """Test that Ace counts as 1 when 11 would cause bust.
        
        Verifies that an Ace is automatically valued at 1 instead of 11 when
        using 11 would cause the hand to exceed 21.
        """
        hand = BlackjackHand(Card("Ace", "Hearts"))
        hand.add_card(Card("9", "Diamonds"))
        hand.add_card(Card("King", "Clubs"))
        # Ace + 9 + King = 1 + 9 + 10 = 20 (Ace reduced to 1)
        assert hand.value == 20

    def test_hand_value_multiple_aces(self):
        """Test hand value with multiple aces.
        
        Verifies that when a hand contains multiple Aces, only one is counted
        as 11 and the rest as 1, unless that would cause a bust.
        """
        hand = BlackjackHand(Card("Ace", "Hearts"))
        hand.add_card(Card("Ace", "Diamonds"))
        # Two aces = 11 + 1 = 12
        assert hand.value == 12

        hand.add_card(Card("9", "Clubs"))
        # Ace + Ace + 9 = 1 + 1 + 9 = 11 (both aces reduced)
        # Actually: 11 + 1 + 9 = 21 (one ace as 11, one as 1)
        assert hand.value == 21

    def test_hand_value_three_aces(self):
        """Test hand value with three aces.
        
        Verifies correct valuation when three Aces are in a hand (one as 11,
        two as 1, for a total of 13).
        """
        hand = BlackjackHand(Card("Ace", "Hearts"))
        hand.add_card(Card("Ace", "Diamonds"))
        hand.add_card(Card("Ace", "Clubs"))
        # Three aces: 11 + 1 + 1 = 13
        assert hand.value == 13

    def test_blackjack(self):
        """Test natural blackjack (Ace + 10-value card).
        
        Verifies that a two-card hand with an Ace and a 10-value card
        (10, J, Q, or K) correctly evaluates to 21.
        """
        hand = BlackjackHand(Card("Ace", "Hearts"))
        hand.add_card(Card("King", "Diamonds"))
        assert hand.value == 21

    def test_is_bust_false(self):
        """Test is_bust when hand is under 21.
        
        Verifies that the is_bust property returns False when the hand value
        is less than or equal to 21.
        """
        hand = BlackjackHand(Card("10", "Hearts"))
        hand.add_card(Card("9", "Diamonds"))
        assert hand.is_bust is False

    def test_is_bust_true(self):
        """Test is_bust when hand exceeds 21.
        
        Verifies that the is_bust property returns True when the hand value
        exceeds 21.
        """
        hand = BlackjackHand(Card("10", "Hearts"))
        hand.add_card(Card("King", "Diamonds"))
        hand.add_card(Card("5", "Clubs"))
        assert hand.value == 25
        assert hand.is_bust is True

    def test_is_bust_exact_21(self):
        """Test that exactly 21 is not a bust.
        
        Verifies that a hand with exactly 21 points is not considered a bust.
        """
        hand = BlackjackHand(Card("10", "Hearts"))
        hand.add_card(Card("Jack", "Diamonds"))
        hand.add_card(Card("Ace", "Clubs"))
        assert hand.value == 21
        assert hand.is_bust is False

    def test_get_cards_returns_copy(self):
        """Test that get_cards returns a copy, not the original list.
        
        Verifies that the cards property returns a copy of the internal card list,
        preventing external modification of the hand's internal state.
        """
        hand = BlackjackHand(Card("5", "Hearts"))
        cards = hand.cards
        cards.append(Card("King", "Diamonds"))
        # Original hand should still have only 1 card
        assert len(hand.cards) == 1


class TestPlayer:
    """Tests for the Player class.
    
    This test class verifies the functionality of the Player class,
    including player and dealer initialization, receiving cards,
    hand management, and displaying hands with proper dealer card hiding.
    """

    def test_player_initialization(self):
        """Test player initialization.
        
        Verifies that a Player object can be created with a name and dealer status.
        """
        player = Player("Alice", is_dealer=False)
        assert player.name == "Alice"
        assert player.is_dealer is False

    def test_dealer_initialization(self):
        """Test dealer initialization.
        
        Verifies that a Player can be initialized as a dealer.
        """
        dealer = Player("Dealer", is_dealer=True)
        assert dealer.name == "Dealer"
        assert dealer.is_dealer is True

    def test_receive_first_card(self):
        """Test receiving the first card creates a hand.
        
        Verifies that when a player receives their first card, a hand is
        automatically created.
        """
        player = Player("Bob", is_dealer=False)
        card = Card("5", "Hearts")
        player.receive_card(card)
        # Hand should be created after receiving first card
        assert hasattr(player, "_hand")
        assert player.hand is not None
        assert len(player.hand.cards) == 1

    def test_receive_multiple_cards(self):
        """Test receiving multiple cards.
        
        Verifies that a player can receive multiple cards sequentially and that
        all cards are added to their hand.
        """
        player = Player("Charlie", is_dealer=False)
        player.receive_card(Card("5", "Hearts"))
        player.receive_card(Card("King", "Diamonds"))
        player.receive_card(Card("Ace", "Clubs"))
        assert len(player.hand.cards) == 3

    def test_hand_property(self):
        """Test hand property access.
        
        Verifies that the player's hand can be accessed and that hand values
        are calculated correctly.
        """
        player = Player("Diana", is_dealer=False)
        player.receive_card(Card("10", "Hearts"))
        player.receive_card(Card("9", "Diamonds"))
        assert player.hand.value == 19

    def test_show_hand_returns_string(self):
        """Test that show_hand returns a string.
        
        Verifies that the show_hand method returns a formatted string
        representation of all cards in the player's hand.
        """
        player = Player("Eve", is_dealer=False)
        player.receive_card(Card("5", "Hearts"))
        player.receive_card(Card("King", "Diamonds"))
        result = player.show_hand()
        assert isinstance(result, str)
        assert "5 of Hearts" in result
        assert "King of Diamonds" in result

    def test_show_hand_dealer_initial_reveal(self):
        """Test dealer hand with second card hidden.
        
        Verifies that when a dealer's hand is shown with initial_reveal=True,
        the first card is visible but subsequent cards are hidden.
        """
        dealer = Player("Dealer", is_dealer=True)
        dealer.receive_card(Card("Ace", "Hearts"))
        dealer.receive_card(Card("King", "Diamonds"))
        result = dealer.show_hand(initial_reveal=True)
        assert "Ace of Hearts" in result
        assert "[HIDDEN CARD]" in result
        assert "King of Diamonds" not in result


class TestBlackjackGame:
    """Tests for the BlackjackGame class.
    
    This test class verifies the functionality of the BlackjackGame class,
    including game initialization, initial card dealing, blackjack detection,
    winner determination, and handling of various game outcomes.
    """

    def test_game_initialization(self):
        """Test game initialization.
        
        Verifies that a BlackjackGame is properly initialized with a player
        and dealer, and that the deck is created.
        """
        game = BlackjackGame("TestPlayer")
        assert game._player.name == "TestPlayer"
        assert game._dealer.name == "Dealer"
        assert game._player.is_dealer is False
        assert game._dealer.is_dealer is True

    def test_deal_initial_cards(self):
        """Test that initial cards are dealt to player and dealer.
        
        Verifies that both the player and dealer receive exactly two cards
        when the game starts.
        """
        game = BlackjackGame("TestPlayer")
        game.deal_initial_cards()

        # Check both player and dealer have 2 cards
        assert len(game._player.hand.cards) == 2
        assert len(game._dealer.hand.cards) == 2

    def test_check_initial_blackjack_both_have_blackjack(self):
        """Test determine_winner with initial_check when both have blackjack.
        
        Verifies that when both player and dealer have blackjack (21 with two
        cards), the result is a push (tie).
        """
        game = BlackjackGame("TestPlayer")
        # Give both blackjack
        game._player.receive_card(Card("Ace", "Hearts"))
        game._player.receive_card(Card("King", "Diamonds"))
        game._dealer.receive_card(Card("Ace", "Clubs"))
        game._dealer.receive_card(Card("Queen", "Spades"))

        status = game.determine_winner(initial_check=True)
        assert status == GameStatus.PUSH
        assert game._player.hand.value == 21
        assert game._dealer.hand.value == 21

    def test_check_initial_blackjack_player_only(self):
        """Test determine_winner with initial_check when only player has blackjack.
        
        Verifies that when only the player has blackjack, the player wins
        immediately.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("Ace", "Hearts"))
        game._player.receive_card(Card("King", "Diamonds"))
        game._dealer.receive_card(Card("5", "Clubs"))
        game._dealer.receive_card(Card("7", "Spades"))

        status = game.determine_winner(initial_check=True)
        assert status == GameStatus.PLAYER_WIN
        assert game._player.hand.value == 21

    def test_check_initial_blackjack_dealer_only(self):
        """Test determine_winner with initial_check when only dealer has blackjack.
        
        Verifies that when only the dealer has blackjack, the dealer wins
        immediately.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("9", "Diamonds"))
        game._dealer.receive_card(Card("Ace", "Clubs"))
        game._dealer.receive_card(Card("Jack", "Spades"))

        status = game.determine_winner(initial_check=True)
        assert status == GameStatus.DEALER_WIN
        assert game._dealer.hand.value == 21

    def test_check_initial_blackjack_none(self):
        """Test determine_winner with initial_check when neither has blackjack.
        
        Verifies that when neither player has blackjack, the game continues
        to player actions.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("9", "Diamonds"))
        game._dealer.receive_card(Card("5", "Clubs"))
        game._dealer.receive_card(Card("7", "Spades"))

        status = game.determine_winner(initial_check=True)
        assert status == GameStatus.CONTINUE

    def test_player_bust(self):
        """Test detecting player bust.
        
        Verifies that when a player's hand exceeds 21, it is correctly
        identified as a bust.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("King", "Hearts"))
        game._player.receive_card(Card("Queen", "Diamonds"))
        game._player.receive_card(Card("5", "Clubs"))

        assert game._player.hand.is_bust is True
        assert game._player.hand.value == 25

    def test_dealer_bust(self):
        """Test detecting dealer bust.
        
        Verifies that when a dealer's hand exceeds 21, it is correctly
        identified as a bust.
        """
        game = BlackjackGame("TestPlayer")
        game._dealer.receive_card(Card("10", "Hearts"))
        game._dealer.receive_card(Card("8", "Diamonds"))
        game._dealer.receive_card(Card("7", "Clubs"))

        assert game._dealer.hand.is_bust is True
        assert game._dealer.hand.value == 25

    def test_determine_winner_player_wins_higher_value(self):
        """Test determine_winner when player has higher value.
        
        Verifies that when both hands are valid (<= 21) and the player's
        hand value is higher, the player wins.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("9", "Diamonds"))
        game._dealer.receive_card(Card("10", "Clubs"))
        game._dealer.receive_card(Card("7", "Spades"))

        status = game.determine_winner(initial_check=False)
        assert status == GameStatus.PLAYER_WIN
        assert game._player.hand.value == 19
        assert game._dealer.hand.value == 17

    def test_determine_winner_dealer_wins_higher_value(self):
        """Test determine_winner when dealer has higher value.
        
        Verifies that when both hands are valid (<= 21) and the dealer's
        hand value is higher, the dealer wins.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("7", "Diamonds"))
        game._dealer.receive_card(Card("10", "Clubs"))
        game._dealer.receive_card(Card("9", "Spades"))

        status = game.determine_winner(initial_check=False)
        assert status == GameStatus.DEALER_WIN
        assert game._player.hand.value == 17
        assert game._dealer.hand.value == 19

    def test_determine_winner_push(self):
        """Test determine_winner when it's a tie.
        
        Verifies that when both player and dealer have the same hand value
        (<= 21), the result is a push (tie).
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("8", "Diamonds"))
        game._dealer.receive_card(Card("King", "Clubs"))
        game._dealer.receive_card(Card("8", "Spades"))

        status = game.determine_winner(initial_check=False)
        assert status == GameStatus.PUSH
        assert game._player.hand.value == 18
        assert game._dealer.hand.value == 18

    def test_determine_winner_player_bust(self):
        """Test determine_winner when player busts.
        
        Verifies that when the player busts (exceeds 21), the dealer wins
        regardless of the dealer's hand value.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("King", "Hearts"))
        game._player.receive_card(Card("Queen", "Diamonds"))
        game._player.receive_card(Card("5", "Clubs"))
        game._dealer.receive_card(Card("10", "Clubs"))
        game._dealer.receive_card(Card("7", "Spades"))

        status = game.determine_winner(initial_check=False)
        assert status == GameStatus.DEALER_WIN
        assert game._player.hand.is_bust is True

    def test_determine_winner_dealer_bust(self):
        """Test determine_winner when dealer busts.
        
        Verifies that when the dealer busts (exceeds 21) and the player has
        a valid hand, the player wins.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("9", "Diamonds"))
        game._dealer.receive_card(Card("King", "Clubs"))
        game._dealer.receive_card(Card("Queen", "Spades"))
        game._dealer.receive_card(Card("5", "Hearts"))

        status = game.determine_winner(initial_check=False)
        assert status == GameStatus.PLAYER_WIN
        assert game._dealer.hand.is_bust is True


class TestEdgeCases:
    """Test edge cases and boundary conditions.
    
    This test class covers unusual but valid game scenarios including
    hands with all face cards, multiple Aces, soft and hard 17s,
    and multi-card hands.
    """

    def test_hand_with_all_face_cards(self):
        """Test a hand with all face cards.
        
        Verifies that a hand with three face cards (K, Q, J) totals 30 and
        is correctly identified as a bust.
        """
        hand = BlackjackHand(Card("King", "Hearts"))
        hand.add_card(Card("Queen", "Diamonds"))
        hand.add_card(Card("Jack", "Clubs"))
        assert hand.value == 30
        assert hand.is_bust is True

    def test_hand_with_all_aces(self):
        """Test a hand with four aces.
        
        Verifies that a hand with four Aces is correctly valued (one Ace as 11,
        three Aces as 1, totaling 14).
        """
        hand = BlackjackHand(Card("Ace", "Hearts"))
        hand.add_card(Card("Ace", "Diamonds"))
        hand.add_card(Card("Ace", "Clubs"))
        hand.add_card(Card("Ace", "Spades"))
        # 11 + 1 + 1 + 1 = 14
        assert hand.value == 14
        assert hand.is_bust is False

    def test_soft_17(self):
        """Test soft 17 (Ace + 6).
        
        Verifies that a hand with an Ace and 6 correctly evaluates to 17
        (soft 17, where the Ace is counted as 11).
        """
        hand = BlackjackHand(Card("Ace", "Hearts"))
        hand.add_card(Card("6", "Diamonds"))
        assert hand.value == 17

    def test_hard_17(self):
        """Test hard 17 (10 + 7).
        
        Verifies that a hand with 10 and 7 correctly evaluates to 17
        (hard 17, with no Ace counted as 11).
        """
        hand = BlackjackHand(Card("10", "Hearts"))
        hand.add_card(Card("7", "Diamonds"))
        assert hand.value == 17

    def test_five_card_charlie(self):
        """Test a five-card hand under 21.
        
        Verifies that a hand with five cards totaling 20 is correctly valued
        and not considered a bust.
        """
        hand = BlackjackHand(Card("2", "Hearts"))
        hand.add_card(Card("3", "Diamonds"))
        hand.add_card(Card("4", "Clubs"))
        hand.add_card(Card("5", "Spades"))
        hand.add_card(Card("6", "Hearts"))
        assert hand.value == 20
        assert hand.is_bust is False
        assert len(hand.cards) == 5


class TestPlayerTurn:
    """Tests for the player_turn method.
    
    Verifies that player decisions (hit, stand, invalid input) are properly
    handled and that the method returns the correct continuation signal.
    """

    def test_player_turn_hit(self):
        """Test player chooses to hit.
        
        Verifies that when a player chooses to hit, a card is dealt and
        the method returns True to continue prompting (if not bust).
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("5", "Hearts"))
        game._player.receive_card(Card("7", "Diamonds"))
        
        initial_card_count = len(game._player.hand.cards)
        continue_playing = game.player_turn("hit")
        
        # Player should have received a card
        assert len(game._player.hand.cards) == initial_card_count + 1
        # Player should continue if not bust
        assert continue_playing == (not game._player.hand.is_bust)

    def test_player_turn_hit_shorthand(self):
        """Test player chooses to hit using 'h'.
        
        Verifies that 'h' is accepted as shorthand for 'hit'.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("5", "Hearts"))
        game._player.receive_card(Card("7", "Diamonds"))
        
        initial_card_count = len(game._player.hand.cards)
        continue_playing = game.player_turn("h")
        
        assert len(game._player.hand.cards) == initial_card_count + 1
        assert continue_playing == (not game._player.hand.is_bust)

    def test_player_turn_stand(self):
        """Test player chooses to stand.
        
        Verifies that when a player stands, no card is dealt and the
        method returns False to stop prompting.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("8", "Diamonds"))
        
        initial_card_count = len(game._player.hand.cards)
        continue_playing = game.player_turn("stand")
        
        # No card should be added
        assert len(game._player.hand.cards) == initial_card_count
        # Should return False to stop the game loop
        assert continue_playing is False

    def test_player_turn_stand_shorthand(self):
        """Test player chooses to stand using 's'.
        
        Verifies that 's' is accepted as shorthand for 'stand'.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("8", "Diamonds"))
        
        initial_card_count = len(game._player.hand.cards)
        continue_playing = game.player_turn("s")
        
        assert len(game._player.hand.cards) == initial_card_count
        assert continue_playing is False

    def test_player_turn_invalid_input(self):
        """Test player enters invalid input.
        
        Verifies that invalid input returns True to continue prompting
        but doesn't add a card.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("8", "Diamonds"))
        
        initial_card_count = len(game._player.hand.cards)
        continue_playing = game.player_turn("invalid")
        
        # No card should be added for invalid input
        assert len(game._player.hand.cards) == initial_card_count
        # Should return True to continue prompting
        assert continue_playing is True

    def test_player_turn_hit_causes_bust(self):
        """Test player hits and busts.
        
        Verifies that when a player hits and busts, the method returns False
        to stop prompting.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("King", "Hearts"))
        game._player.receive_card(Card("Queen", "Diamonds"))
        
        # Manually deal a card that will cause bust
        # K + Q + 5 = 25 (bust)
        game._deck._cards = [Card("5", "Clubs")]  # Force specific card
        continue_playing = game.player_turn("hit")
        
        # Player should have busted
        assert game._player.hand.is_bust is True
        # Should return False to stop prompting
        assert continue_playing is False


class TestDealerTurns:
    """Tests for the dealer_turns method.
    
    Verifies that the dealer AI correctly hits until 17 or higher,
    and properly handles bust scenarios.
    """

    def test_dealer_turns_stands_on_17(self):
        """Test dealer stands on 17.
        
        Verifies that when the dealer has 17, they don't hit.
        """
        game = BlackjackGame("TestPlayer")
        game._dealer.receive_card(Card("10", "Hearts"))
        game._dealer.receive_card(Card("7", "Diamonds"))
        
        actions = game.dealer_turns()
        
        # Dealer should stand with 17
        assert game._dealer.hand.value == 17
        assert len(game._dealer.hand.cards) == 2
        assert any("stands" in action for action in actions)

    def test_dealer_turns_hits_until_17(self):
        """Test dealer hits until reaching 17.
        
        Verifies that the dealer continues hitting when below 17.
        """
        game = BlackjackGame("TestPlayer")
        game._dealer.receive_card(Card("5", "Hearts"))
        game._dealer.receive_card(Card("7", "Diamonds"))
        
        actions = game.dealer_turns()
        
        # Dealer should have hit at least once
        assert len(game._dealer.hand.cards) > 2
        # Final value should be 17 or higher
        assert game._dealer.hand.value >= 17

    def test_dealer_turns_stops_on_bust(self):
        """Test dealer stops when bust.
        
        Verifies that the dealer stops hitting after busting.
        """
        game = BlackjackGame("TestPlayer")
        game._dealer.receive_card(Card("King", "Hearts"))
        game._dealer.receive_card(Card("5", "Diamonds"))
        
        # Set up deck so dealer will bust: K+5=15, then gets 7 (22, bust)
        # Note: pop() takes from end, so put the card we want to deal first at the end
        game._deck._cards = [Card("3", "Clubs"), Card("7", "Clubs")]  # Force specific cards
        
        actions = game.dealer_turns()
        
        # Dealer should have busted
        assert game._dealer.hand.is_bust is True
        # Check that bust message is in actions
        assert any("BUST" in action for action in actions)

    def test_dealer_turns_returns_list_of_actions(self):
        """Test dealer_turns returns list of action strings.
        
        Verifies that the return value is a list of strings describing
        the dealer's actions.
        """
        game = BlackjackGame("TestPlayer")
        game._dealer.receive_card(Card("10", "Hearts"))
        game._dealer.receive_card(Card("8", "Diamonds"))
        
        actions = game.dealer_turns()
        
        # Should return a list
        assert isinstance(actions, list)
        # All items should be strings
        assert all(isinstance(action, str) for action in actions)
        # Should have some content
        assert len(actions) > 0


class TestFinalResults:
    """Tests for the final_results method.
    
    Verifies that the final results message is properly formatted and
    contains correct information for all game outcomes.
    """

    def test_final_results_player_wins(self):
        """Test final results when player wins.
        
        Verifies that the message correctly indicates player victory.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("9", "Diamonds"))
        game._player.receive_card(Card("2", "Clubs"))  # Add third card to avoid blackjack detection
        game._dealer.receive_card(Card("10", "Clubs"))
        game._dealer.receive_card(Card("7", "Spades"))
        
        result = game.final_results(GameStatus.PLAYER_WIN)
        
        assert "TestPlayer" in result
        assert "WINS" in result or "win" in result
        assert "21" in result  # Player's hand value
        assert "17" in result  # Dealer's hand value

    def test_final_results_dealer_wins(self):
        """Test final results when dealer wins.
        
        Verifies that the message correctly indicates dealer victory.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("7", "Diamonds"))
        game._dealer.receive_card(Card("10", "Clubs"))
        game._dealer.receive_card(Card("9", "Spades"))
        
        result = game.final_results(GameStatus.DEALER_WIN)
        
        assert "DEALER WINS" in result or "Dealer wins" in result
        assert "17" in result  # Player's hand value
        assert "19" in result  # Dealer's hand value

    def test_final_results_push(self):
        """Test final results when it's a tie.
        
        Verifies that the message correctly indicates a push.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("8", "Diamonds"))
        game._dealer.receive_card(Card("King", "Clubs"))
        game._dealer.receive_card(Card("8", "Spades"))
        
        result = game.final_results(GameStatus.PUSH)
        
        assert "PUSH" in result or "tie" in result
        assert "18" in result  # Both have 18

    def test_final_results_player_blackjack(self):
        """Test final results when player has blackjack.
        
        Verifies that the message identifies initial blackjack.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("Ace", "Hearts"))
        game._player.receive_card(Card("King", "Diamonds"))
        game._dealer.receive_card(Card("10", "Clubs"))
        game._dealer.receive_card(Card("9", "Spades"))
        
        result = game.final_results(GameStatus.PLAYER_WIN)
        
        assert "BLACKJACK" in result
        assert "TestPlayer" in result
        assert "21" in result

    def test_final_results_dealer_blackjack(self):
        """Test final results when dealer has blackjack.
        
        Verifies that the message identifies dealer blackjack.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("9", "Diamonds"))
        game._dealer.receive_card(Card("Ace", "Clubs"))
        game._dealer.receive_card(Card("Queen", "Spades"))
        
        result = game.final_results(GameStatus.DEALER_WIN)
        
        assert "BLACKJACK" in result
        assert "Dealer" in result
        assert "21" in result

    def test_final_results_both_blackjack(self):
        """Test final results when both have blackjack.
        
        Verifies that the message indicates both players have blackjack.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("Ace", "Hearts"))
        game._player.receive_card(Card("King", "Diamonds"))
        game._dealer.receive_card(Card("Ace", "Clubs"))
        game._dealer.receive_card(Card("Queen", "Spades"))
        
        result = game.final_results(GameStatus.PUSH)
        
        assert "BLACKJACK" in result
        assert "PUSH" in result
        assert "TestPlayer" in result
        assert "Dealer" in result

    def test_final_results_player_bust(self):
        """Test final results when player busts.
        
        Verifies that the message indicates player busted.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("King", "Hearts"))
        game._player.receive_card(Card("Queen", "Diamonds"))
        game._player.receive_card(Card("5", "Clubs"))
        game._dealer.receive_card(Card("10", "Clubs"))
        game._dealer.receive_card(Card("7", "Spades"))
        
        result = game.final_results(GameStatus.DEALER_WIN)
        
        assert "busted" in result or "BUST" in result
        assert "TestPlayer" in result
        assert "25" in result  # Player's bust value

    def test_final_results_dealer_bust(self):
        """Test final results when dealer busts.
        
        Verifies that the message indicates dealer busted.
        """
        game = BlackjackGame("TestPlayer")
        game._player.receive_card(Card("10", "Hearts"))
        game._player.receive_card(Card("9", "Diamonds"))
        game._dealer.receive_card(Card("King", "Clubs"))
        game._dealer.receive_card(Card("Queen", "Spades"))
        game._dealer.receive_card(Card("5", "Hearts"))
        
        result = game.final_results(GameStatus.PLAYER_WIN)
        
        assert "busted" in result or "BUST" in result
        assert "Dealer" in result or "DEALER" in result


class TestAdditionalCoverage:
    """Additional tests to improve code coverage.
    
    Covers edge cases and less common code paths.
    """

    def test_show_hand_empty(self):
        """Test show_hand when player has no hand yet.
        
        Verifies that show_hand returns empty string when hand is None.
        """
        player = Player("TestPlayer", is_dealer=False)
        result = player.show_hand()
        assert result == ""

    def test_hand_property_raises_error_when_none(self):
        """Test accessing hand property before receiving cards.
        
        Verifies that accessing hand before it's created raises ValueError.
        """
        player = Player("TestPlayer", is_dealer=False)
        with pytest.raises(ValueError, match="hand has not been created"):
            _ = player.hand

    def test_game_deck_is_shuffled(self):
        """Test that game deck is shuffled on initialization.
        
        Verifies that the deck is shuffled when a game is created
        (by checking that two games deal different first cards).
        """
        game1 = BlackjackGame("Player1")
        game2 = BlackjackGame("Player2")
        
        # Deal first cards from each game
        card1 = game1._deck.deal_card()
        card2 = game2._deck.deal_card()
        
        # They may be the same, but if we deal multiple cards, 
        # at least some should differ (extremely unlikely all match)
        cards1 = [card1] + [game1._deck.deal_card() for _ in range(9)]
        cards2 = [card2] + [game2._deck.deal_card() for _ in range(9)]
        
        # At least one card should be different in position
        cards1_str = [str(c) for c in cards1]
        cards2_str = [str(c) for c in cards2]
        assert cards1_str != cards2_str

