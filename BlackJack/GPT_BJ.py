import random
from collections import deque

class Game():
    def __init__(self, num_players, num_decks):
        self.num_players = num_players
        self.num_decks = num_decks
        self.shoe = deque(self.initialize_shoe())
        self.hands = [[] for _ in range(num_players + 1)]  # players and dealer hands
        self.card_count = 0  # High-Low card count
        self.init_strategies()
        #self.play()
        self.games_won = 0
        self.games_lost = 0
        self.games_pushed = 0
        self.cut_card = random.randint(num_decks*52-78, num_decks*52-26)

    

    def initialize_shoe(self):
        """Initialize the shoe with num_decks decks of cards."""
        shoe = []
        for _ in range(self.num_decks):
            for rank in range(1, 14):  # 1-13 represent Ace-King
                for _ in range(4):  # 4 suits
                    shoe.append(rank)
        random.shuffle(shoe)
        return shoe

    def deal_card(self, hand):
        """Deal a card from the shoe to a hand and update the card count."""
        card = self.shoe.pop()
        hand.append(card)
        self.update_card_count(card)

    def update_card_count(self, card):
        """Update the High-Low card count based on the card dealt."""
        if card >= 10 or card == 1:  # 10, J, Q, K, A
            self.card_count -= 1
        elif 2 <= card <= 6:
            self.card_count += 1
        # 7, 8, 9 are neutral

    def calculate_hand_value(self, hand):
        """Calculate the total value of a hand."""
        value = 0
        num_aces = 0
        for card in hand:
            if card == 1:  # Ace
                num_aces += 1
                value += 11
            elif card >= 10:  # 10, J, Q, K
                value += 10
            else:
                value += card
        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1
        return value

    def init_strategies(self):
        """Initialize strategy tables based on the provided data."""
        hard_sums = [
            '1,H,H,H,H,H,H,H,H,H,H', '2,H,H,H,H,H,H,H,H,H,H', '3,H,H,H,H,H,H,H,H,H,H',
            '4,H,H,H,H,H,H,H,H,H,H', '5,H,H,H,H,H,H,H,H,H,H', '6,H,H,H,H,H,H,H,H,H,H',
            '7,H,H,H,H,H,H,H,H,H,H', '8,H,H,H,H,H,H,H,H,H,H', '9,H,D,D,D,D,H,H,H,H,H',
            '10,D,D,D,D,D,D,D,D,H,H', '11,D,D,D,D,D,D,D,D,D,H', '12,H,H,S,S,S,H,H,H,H,H',
            '13,S,S,S,S,S,H,H,H,H,H', '14,S,S,S,S,S,H,H,H,H,H', '15,S,S,S,S,S,H,H,H,H,H',
            '16,S,S,S,S,S,H,H,H,H,H', '17,S,S,S,S,S,S,S,S,S,S', '18,S,S,S,S,S,S,S,S,S,S',
            '19,S,S,S,S,S,S,S,S,S,S', '20,S,S,S,S,S,S,S,S,S,S'
        ]
        soft_sums = [
            '2,H,H,H,D,D,H,H,H,H,H', '3,H,H,H,D,D,H,H,H,H,H', '4,H,H,D,D,D,H,H,H,H,H',
            '5,H,H,D,D,D,H,H,H,H,H', '6,H,D,D,D,D,H,H,H,H,H', '7,S,D,D,D,D,S,S,H,H,H',
            '8,S,S,S,S,S,S,S,S,S,S', '9,S,S,S,S,S,S,S,S,S,S', '10,S,S,S,S,S,S,S,S,S,S'
        ]
        pairs = [
            '2,SP,SP,SP,SP,SP,SP,H,H,H,H', '3,SP,SP,SP,SP,SP,SP,H,H,H,H',
            '4,H,H,H,SP,SP,H,H,H,H,H', '5,D,D,D,D,D,D,D,D,H,H',
            '6,SP,SP,SP,SP,SP,H,H,H,H,H', '7,SP,SP,SP,SP,SP,SP,H,H,H,H',
            '8,SP,SP,SP,SP,SP,SP,SP,SP,SP,SP', '9,SP,SP,SP,SP,SP,S,SP,SP,S,S',
            '10,S,S,S,S,S,S,S,S,S,S', '11,SP,SP,SP,SP,SP,SP,SP,SP,SP,SP'
        ]

        # Convert strings to lists of actions
        self.HardSums = {i + 1: actions.split(',')[1:] for i, actions in enumerate(hard_sums)}
        self.SoftSums = {i + 2: actions.split(',')[1:] for i, actions in enumerate(soft_sums)}
        self.Pairs = {i + 2: actions.split(',')[1:] for i, actions in enumerate(pairs)}

    def play_optimal_strategy(self, player_hand, dealer_upcard):
        """Decide the player's action based on the strategy tables."""
        player_value = self.calculate_hand_value(player_hand)
        dealer_index = dealer_upcard - 1

        # Validate dealer_index
        if dealer_index < 0 or dealer_index >= 10:
            dealer_index = min(max(dealer_index, 0), 9)  # Clamp to valid range

        # Determine if the hand is a pair
        if len(player_hand) == 2 and player_hand[0] == player_hand[1]:
            pair_value = player_hand[0] if player_hand[0] < 10 else 10
            action = self.Pairs.get(pair_value, ['H'] * 10)[dealer_index]
        # Determine if the hand is a soft sum (contains an Ace counted as 11)
        elif 1 in player_hand and player_value <= 21:
            soft_value = player_value - 11
            action = self.SoftSums.get(soft_value, ['H'] * 10)[dealer_index]
        # Otherwise, it's a hard sum
        else:
            action = self.HardSums.get(player_value, ['H'] * 10)[dealer_index]

        if action == 'H':
            return "hit"
        elif action == 'S':
            return "stand"
        elif action == 'D':
            return "double" if len(player_hand) == 2 else "hit"
        elif action == 'SP':
            return "split" if len(player_hand) == 2 else "hit"
        else:
            return "hit"


    def dealer_plays(self):
        """Simulate the dealer's turn."""
        dealer_hand = self.hands[-1]
        while self.calculate_hand_value(dealer_hand) < 17:
            self.deal_card(dealer_hand)

    def play(self):
        win = 0 #1 if win, 0 else
        lose = 0 #1 if lose, 0 else
        push = 0 #1 if tie, 0 else
        """Simulate the Blackjack game."""
        # Initial deal
        for _ in range(2):
            for hand in self.hands:
                self.deal_card(hand)

        dealer_upcard = self.hands[-1][0]

        # Players play
        for i in range(self.num_players):
            player_hand = self.hands[i]
            action = self.play_optimal_strategy(player_hand, dealer_upcard)
            while action == "hit":
                self.deal_card(player_hand)
                if self.calculate_hand_value(player_hand) > 21:
                    break
                action = self.play_optimal_strategy(player_hand, dealer_upcard)
            if action == "double":
                self.deal_card(player_hand)
        
        # Dealer plays
        self.dealer_plays()

        # Results
        dealer_value = self.calculate_hand_value(self.hands[-1])
        results = []
        for i in range(self.num_players):
            player_value = self.calculate_hand_value(self.hands[i])
            if player_value > 21:
                results.append("loss")
                lose =1
            elif dealer_value > 21 or player_value > dealer_value:
                results.append("win")
                win = 1
            elif player_value < dealer_value:
                results.append("loss")
                lose = 1
            else:
                results.append("push")
                push = 1

        print(f"Dealer hand: {self.hands[-1]} (value: {dealer_value})")
        for i, result in enumerate(results):
            print(f"Player {i+1} hand: {self.hands[i]} (value: {self.calculate_hand_value(self.hands[i])}) - {result}")
        print(f"Card count: {self.card_count}")
        self.hands = [[] for _ in range(self.num_players + 1)]  # players and dealer hands
        if  self.num_decks*52-len(self.shoe) > self.cut_card:
            self.shoe = deque(self.initialize_shoe())
            self.cut_card = random.randint(self.num_decks*52-78, self.num_decks*52-26)
        return win,push,lose


# Example of playing a game
#game = Game(1, 6)
if "__main__" == __name__:
    game = Game(1,6)
    results = [0,0,0]
    n=100000
    for i in range(n):
        a,b,c = game.play()
        results[0] += a
        results[1] += b
        results[2] += c
    print()
    print(f"won: {results[0]/n}, lost: {results[2]/n}, pushed: {results[1]/n}")
    print(f"CasinoEdge: {(results[2]/n - results[0]/n)*100}%")