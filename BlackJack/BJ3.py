import matplotlib.pyplot as plt
import random
import math
import time

#Yes double after split, 3 to 2 blackjack payoff, H17, 
class Game():
    def __init__(self, num_decks, num_players):
        self.play_errors = 0
        self.numWins =0
        self.numLosses = 0
        self.numPushes = 0
        self.num_play_deviations = 0
        self.count_results = {}
        self.bet_tracker = []

        self.running_count = 0
        self.true_count = 0
        self.bet_minimum = 10
        self.bet_maximum = 500
        self.bankroll = 5000
        self.current_bankroll = 5000

        self.num_reshufles = 0

        self.ruin_count = 0
        self.big_return_count = 0 #return >= bankroll

        self.num_decks = num_decks
        self.num_players = num_players

        self.cards_in_shoe = self.shoe_initializer(self.num_decks)
        self.cards_played = []

        self.bets = []
        self.profit = [0 for num in range(self.num_players)]

        self.cut_card = self.choose_cut_card()
        # in the form of [with_ace, without_ace, splitting] list of dictionaries
        # with_ace has sum of non-ace cards as key, without_ace has total sum as key, splitting has pair's number as key
        self.strategy_card = self.strategy_card_initializer()
        self.strategy_card_deviations = []

        self.player_cards = []
        self.dealer_cards = []
    
    def count_results_intiializer(self):
        dictionary = {}
        for i in range(-20,20):
            dictionary.update({i: [0,0,0]})
        return dictionary
    
    def choose_cut_card(self):
        if self.num_decks == 2:
            cut_card = random.randint(52, 52*2-20)
        else:
            num_cards = len(self.cards_in_shoe)
            upper_bound = num_cards - 52/2
            lower_bound = num_cards/4 +num_cards/2
            cut_card = random.randint(lower_bound, upper_bound)
        return cut_card

    def strategy_card_initializer(self):
        with_ace = {}
        without_ace = {}
        splitting = {}
        for i in range(1,22):
            with_ace.update({i: []})
            without_ace.update({i: []})
            splitting.update({i: []})
        for i in range(1,22):
            #without aces section
            no_ace_action = []
            if i in [17,18,19,20,21]:
                for j in range(12):
                    no_ace_action += [["S",100,"g","S"]]
            if i == 16:
                for j in range(7):
                    no_ace_action += [["S",100,"g","S"]]
                for j in range(7,9):
                    no_ace_action += [["H",100,"g","H"]]
                no_ace_action += [["H",4,"g","S"]]
                no_ace_action += [["H",1,"g","S"]]
                no_ace_action += [["H",100,"g","H"]]
            if i == 15:
                for j in range(7):
                    no_ace_action += [["S",100,"g","S"]]
                for j in range(7,10):
                    no_ace_action += [["H",100,"g","H"]]
                no_ace_action += [["H",4,"g","S"]]
                no_ace_action += [["H",100,"g","H"]]
            if i == 14:
                for j in range(7):
                    no_ace_action += [["S",100,"g","S"]]
                for j in range(7,12):
                    no_ace_action += [["H",100,"g","H"]]
            if i== 13:
                for j in range(2):
                    no_ace_action += [["S",100,"g","S"]]
                no_ace_action += [["S",-1,"l","H"]]
                for j in range(3,7):
                    no_ace_action += [["S",100,"g","S"]]
                for j in range(7,12):
                    no_ace_action += [["H",100,"g","H"]]
            if i== 12:
                for j in range(2):
                    no_ace_action += [["S",100,"g","S"]]
                no_ace_action += [["H",3,"g","S"]]
                no_ace_action += [["H",2,"g","S"]]
                no_ace_action += [["S",-1,"l","H"]]
                for j in range(5,7):
                    no_ace_action += [["S",100,"g","S"]]
                for j in range(7,12):
                    no_ace_action += [["H",100,"g","H"]]
            if i== 11:
                for j in range(11):
                    no_ace_action += [["D",100,"g","D"]]
                no_ace_action += [["H",1,"g","D"]]
            if i== 10:
                for j in range(10):
                    no_ace_action += [["D",100,"g","D"]]
                no_ace_action += [["H",4,"g","D"]]
                no_ace_action += [["H",4,"g","D"]]
            if i==9:
                for j in range(3):
                    no_ace_action += [["H",1,"g","D"]]
                for j in range(3,7):
                    no_ace_action += [["D",100,"g","D"]]
                no_ace_action += [["H",3,"g","D"]]
                for j in range(8,12):
                    no_ace_action += [["H",100,"g","D"]]
            if i==8:
                for j in range(6):
                    no_ace_action += [["H",100,"g","H"]]
                no_ace_action += [["H",2,"g","D"]]
                for j in range(7,12):
                    no_ace_action += [["H",100,"g","H"]]
            if i<=7:
                for j in range(12):
                    no_ace_action += [["H",100,"g","H"]]
            #with aces section
            if i<=11:
                ace_action = []
                if i==10:
                    for j in range(12):
                        ace_action += [["S",100,"g","S"]]
                if i==9:
                    for j in range(12):
                        if i==8 and j==6:
                            ace_action += [["D",100,"g","D"]]
                        else:
                            ace_action += [['S',100,"g","S"]]
                if i==8:
                    for j in range(12):
                        if j==4:
                            ace_action += [["S",3,"g","Ds"]]
                        elif j==5:
                            ace_action += [["S",1,"g","Ds"]]
                        elif j==6:
                            ace_action += [["S",1,"g","Ds"]]
                        else:
                            ace_action += [['S',100,"g", "S"]]
                if i==7:
                    for j in range(12):
                        if j<7:
                            ace_action += [["Ds",100,"g","Ds"]]
                        elif j in [7,9]:
                            ace_action += [['S',100,"g","S"]]
                        else:
                            ace_action +=[["H",100,"g","H"]]
                if i==6:
                    for j in range(3):
                        ace_action += [["H",1,"g","D"]]
                    for j in range(4):
                        ace_action += [["D",100,"g","D"]]
                    for j in range(5):
                        ace_action += [["H",100,"g","H"]]
                if i==5 or i==4:
                    for j in range(4):
                        ace_action += [["H",100,"g","H"]]
                    for j in range(3):
                        ace_action += [["D",100,"g","D"]]
                    for j in range(5):
                        ace_action += [["H",100,"g","H"]]
                if i<=3:
                    for j in range(5):
                        ace_action += [["H",100,"g","H"]]
                    for j in range(2):
                        ace_action += [["D",100,"g","D"]]
                    for j in range(5):
                        ace_action += [["H",100,"g","H"]]
            #splitting section
            if i<=11:
                split = []
                if i == 11 or i==8:
                    for j in range(12):
                        split +=[["Y",100,"g","Y"]]
                if i== 10:
                    for j in range(12):
                        if j==4:
                            split += [["N",6,"g","Y"]]
                        elif j==5:
                            split += [["N",5,"g","Y"]]
                        elif j==6:
                            split += [["N",4,"g","Y"]]
                        else:
                            split += [["N",100,"g","N"]]
                if i==5:
                    for j in range(12):
                        split +=[["N",100,"g","N"]]
                if i==9:
                    for j in range(12):
                        if j in [7,10,11]:
                            split +=[["N",100,"g","N"]]
                        else:
                            split += [["Y",100,"g","Y"]]
                if i==7:
                    for j in range(12):
                        if j <=7:
                            split +=[["Y",100,"g","Y"]] 
                        else:
                            split += [["N",100,"g","N"]]
                if i==6:
                    for j in range(12):
                        if j<=2:
                            split += [["N",100,"g","N"]] #Y if allowed to double after split
                        elif j <=6 and j>2:
                            split +=[["Y",100,"g","Y"]]
                        else:
                            split += [["N",100,"g","N"]]
                if i==4:
                    for j in range(12):
                        if j in[5,6]:
                            split +=[["N",100,"g","N"]] #Y if allowed to double after split
                        else:
                            split += [["N",100,"g","N"]]
                if i==3 or i==2:
                    for j in range(12):
                        if j<=3:
                            split += [["N",100,"g","N"]] #Y if allowed to double after split
                        elif j<=7 and j>3:
                            split += [["Y",100,"g","Y"]]
                        else:
                            split += [["N",100,"g","N"]]
            with_ace[i] += ace_action
            splitting[i] += split
            without_ace[i] = no_ace_action
        
        return [with_ace, without_ace, splitting]

    def initialize_bets(self):
        min = self.bet_minimum
        max = self.bet_maximum
        count = self.true_count
        bet = min
        if count >1:
            bet = min*(((count-1)**3)+1)
        if bet>max:
            bet= max
        if bet>self.current_bankroll:
            bet = self.current_bankroll
        for i in range(self.num_players):
            self.bets += [bet]
            self.bet_tracker+= [bet]

    def shoe_initializer(self, num_decks):
        cards = []
        for i in range(2,12):
            if i == 10:
                for j in range(16*num_decks):
                    cards += [i]
            else:
                for j in range(4*num_decks):
                    cards += [i]
        return cards
    def count(self, cards):
        lows = [2,3,4,5,6]
        highs = [10,11]
        for card in cards:
            if card in lows:
                self.running_count += 1
            if card in highs:
                self.running_count += -1
        decks_left = round(len(self.cards_in_shoe) / 52, 0)
        if decks_left == 0:
            self.true_count = self.running_count
        else:
            self.true_count = round(self.running_count / decks_left, 0)
    
    def reshuffle_cards(self):
        self.num_reshufles += 1
        self.running_count = 0
        self.true_count = 0
        self.cards_in_shoe = self.shoe_initializer(self.num_decks)
        self.cards_played = []
        self.cut_card = self.choose_cut_card()

    def quiz_user(self, action):
        print(f"True Count: {self.true_count}, Running Count: {self.running_count}")
        print(f"Player Cards: {self.player_cards}")
        print(f"Dealer Card: {self.dealer_cards}")
        quiz = input("Enter Move (H,S,D,SP,Surr): ")
        while quiz != action:
            self.play_errors +=1
            quiz = input("Wrong Move. Try Again: ")

    def play_hand(self):
        if self.cut_card < len(self.cards_played):
            self.reshuffle_cards()
        self.player_cards = []
        self.dealer_cards = []
        self.bets = []
        true_num_players = self.num_players
        self.initialize_bets()
        self.deal_cards()

        player_scores = []
        splits = []

        num_turns = 0
        while num_turns < self.num_players:
            player = num_turns
            action = self.surrender(player,splits)
            if action == "N":
                action = self.player_action(player)
            while action == "Y":
                self.quiz_user("SP")
                splits += [player]
                self.split(player)
                action = self.player_action(player)
            while action == "D":
                self.quiz_user("D")
                if num_turns not in splits and num_turns-1 not in splits: #no double after split
                    self.bets[player] = self.bets[player]*2
                    self.hit(player)
                    action = "S"
                else:
                    action = "H"
            while action == "Ds":
                self.quiz_user("D")
                if num_turns not in splits and num_turns-1 not in splits: #no double after split
                    self.bets[player] = self.bets[player]*2
                    self.hit(player)
                    action = "S"
                else:
                    action = "S"
            while action == "H":
                self.quiz_user("H")
                self.hit(player)
                action = self.player_action(player)
            if action == "Bust" or action == "S":
                self.quiz_user("S")
                player_scores += [sum(self.player_cards[player])]
                num_turns += 1
                continue
        for i in range(len(splits)-1):
            if splits[i]==splits[i+1]:
                splits[i+1] +=1

        dealer_score = self.dealer_action()
        print("Dealer Cards:",self.dealer_cards)
        self.num_players = true_num_players
        results = self.payout(dealer_score, player_scores, splits)
        if results[0]==1:
            print("Win")
        if results[1]==1:
            print("Loss")
        if results[2]==1:
            print("Push")
        print()
        
    def surrender(self, who,splits):
        count = self.true_count
        num_splits = len(splits)
        cards = self.player_cards[who]
        dealer_card = self.dealer_cards[0]
        #if sum(cards) == 17 and dealer_card == 11: #this if statement only for H17. remove for S17
        #    try:
        #        self.profit[who-num_splits] += - self.bets[who]/2
        #    except IndexError:
        #        self.profit[0]+= - self.bets[who]/2
        #    self.bets[who] = 0
        #    return "S"
        if sum(cards) == 16 and 11 not in cards:
            if (dealer_card in [10,11]) or (dealer_card==9 and count > -1) or (dealer_card==8 and count >= 4):
                self.quiz_user("Surr")
                if self.num_players==1:
                    self.profit[0] += - self.bets[who]/2
                else:
                    try:
                        self.profit[who-num_splits] += - self.bets[who]/2
                    except IndexError:
                        self.profit[0] += - self.bets[who]/2
                self.bets[who] = 0
                if dealer_card not in [10,11]:
                    self.num_play_deviations+=1
                return "S"
            else:
                return "N"                                                           #(dealer_card==11  and count >=-1): #for H17
        elif sum(cards) == 15 and 11 not in cards:                                                       #dealer_card==11  and count >=2     for S17
            if (dealer_card==9 and count>=2) or (dealer_card == 10 and count > 0) or (dealer_card==11  and count >=2): #for S17
                self.quiz_user("Surr")
                try:
                    self.profit[who-num_splits] += - self.bets[who]/2
                except IndexError:
                    self.profit[0] += - self.bets[who]/2
                self.bets[who] = 0
                self.num_play_deviations+=1
                return "S"
            else:
                return "N"
        else:
            return "N"
        
    def payout(self, dealer_score, player_scores, splits):
        #print("playerScores:", player_scores, "dealerScore:", dealer_score)
        num_wins = 0
        num_pushes = 0
        num_losses = 0
        #if self.bets[0] == 0:
        #    num_losses += 0.5
        #    num_wins += 0.5
        #    self.numWins += 0.5
        #    self.numLosses += 0.5
        #    return [num_wins,num_losses,num_pushes]
        num_splits = len(splits)
        if dealer_score > 21:
            dealer_score = 0
        for i in range(len(player_scores)-1,-1,-1):
            if player_scores[i] == 21 and len(self.player_cards[i]) == 2:
                if dealer_score == 21 and len(self.dealer_cards)==2:
                    num_pushes+=1
                    self.numPushes +=1
                    if i-1 in splits:
                        num_splits+= -1
                    continue
                else:
                    try:
                        self.profit[i-num_splits] += self.bets[i]*1.5
                    except IndexError:
                        self.profit[0] += self.bets[i]*1.5
                    num_wins +=1
                    self.numWins +=1
                if i-1 in splits:
                    num_splits-=1
            elif player_scores[i] <=21 and player_scores[i]>=dealer_score:
                if player_scores[i] == dealer_score:
                    num_pushes+=1
                    self.numPushes +=1
                    if i-1 in splits:
                        num_splits-=1
                    continue
                num_wins+=1
                self.numWins +=1
                try:
                    self.profit[i-num_splits] += self.bets[i]
                except IndexError:
                    self.profit[0] += self.bets[i]
                if i-1 in splits:
                    num_splits-=1
            else: # dealer_score > player_scores[i]:
                num_losses +=1
                self.numLosses +=1
                try:
                    self.profit[i-num_splits] += -self.bets[i]
                except IndexError:
                    self.profit[0] += -self.bets[i]
                if i-1 in splits:
                    num_splits-=1
        return [num_wins,num_losses,num_pushes]
                    
    def deal_cards(self):
        cards = []
        for i in range(2*self.num_players+1):
            cards += [random.choice(self.cards_in_shoe)]
            self.cards_in_shoe.remove(cards[i])
        self.count(cards)
        self.cards_played += cards
        for i in range(self.num_players):
            self.player_cards += [[cards[2*i],cards[2*i+1]]]
        self.dealer_cards += [cards[-1]]
    
    #creates a new player and shifts all players above up by one
    #automatically hits player who and player who+1
    def split(self, who):
        num = self.player_cards[who][0]
        self.player_cards.insert(who,[num])
        self.player_cards[who+1] = [num]
        self.num_players += 1
        
        bet = self.bets[who]
        self.bets.insert(who, bet)

        self.hit(who)
        self.hit(who+1)

    #if player, player = 0 ; if dealer, player = 1
    def hit(self, who):
        cards = [random.choice(self.cards_in_shoe)]
        self.cards_in_shoe.remove(cards[0])
        self.count(cards)
        self.cards_played += cards
        if who < self.num_players:
            self.player_cards[who] += cards
        if who == self.num_players:
            self.dealer_cards += cards

    #returns one of  "S", "H", "D", "Ds", "Y"(split), "N" (noSplit)
    #assuming always allowed to double when the card says. Can include caveots later on
    def player_action(self, who):
        cards = self.player_cards[who]
        score = sum(cards)
        dealer_card = self.dealer_cards[0]
        count = self.true_count
        if len(cards)==2 and cards[0] == cards[1]:
            action = self.strategy_card[2][cards[0]][dealer_card]
            act = action[0]
            if action[2] =="g" and count >= action[1]:
                act = action[-1]
                self.num_play_deviations+=1
            if action[2] =="l" and count <= action[1]:
                act = action[-1]
                self.num_play_deviations+=1
            if act == "Y":
                return act
        if score > 21:
            if 11 in cards:
                for i in range(len(cards)):
                    if cards[i] == 11:
                        cards[i] = 1
                        break
                return self.player_action(who)
            else:
                return "Bust"
        if 11 in cards:
            key = score-11
            action = self.strategy_card[0][key][dealer_card]
            act = action[0]
            if action[2] =="g" and count >= action[1]:
                act = action[-1]
                self.num_play_deviations+=1
            if action[2] =="l" and count <= action[1]:
                act = action[-1]
                self.num_play_deviations+=1
            if act == "D":
                if len(cards)==2:
                    return "D"
                else:
                    return "H"
            if act == "Ds":
                if len(cards)==2:
                    return "D"
                else:
                    return "S"
        action = self.strategy_card[1][score][dealer_card]
        act = action[0]
        if action[2] =="g" and count >= action[1]:
            act = action[-1]
            self.num_play_deviations+=1
        if action[2] =="l" and count <= action[1]:
            act = action[-1]
            self.num_play_deviations+=1
        if act == "D" or act == "Ds":
            if len(cards)==2:
                return "D"
            else:
                return "H"
        if act == "Ds":
            if len(cards)==2:
                return "D"
            else:
                return "S"
        return act
    
    def dealer_action(self):
        score = sum(self.dealer_cards)
        while score<17:
            self.hit(self.num_players)
            score = sum(self.dealer_cards)
        if score == 17 and 11 in self.dealer_cards:
            #self.hit(self.num_players)      #H17 -- dealer hits on a soft 17
            score = sum(self.dealer_cards)
            if score <= 21:
                return score
        if score > 21 and 11 in self.dealer_cards:
            for i in range(len(self.dealer_cards)):
                if self.dealer_cards[i] == 11:
                    self.dealer_cards[i] = 1
            return self.dealer_action()
        return score

    def reset_day(self):
        #self.numWins =0
        #self.numLosses = 0
        #self.numPushes = 0
        self.running_count = 0
        #self.num_play_deviations = 0
        self.true_count = 0
        self.bankroll = 5000
        self.current_bankroll = 5000
        self.cards_in_shoe = self.shoe_initializer(self.num_decks)
        self.cards_played = []
        self.bets = []
        self.profit = [0 for num in range(self.num_players)]
        self.cut_card = self.choose_cut_card()
        self.bet_tracker = []
        self.num_reshufles = 0

    def run_games(self, num_games):
        current_profit = 0
        winnings_per_hand = []
        Ruin_count = 0
        tenK_count = 0
        for game in range(num_games):
            old_profit = current_profit
            self.play_hand()
            current_profit = sum(self.profit)
            hand_profit = current_profit - old_profit
            winnings_per_hand += [hand_profit]
            self.current_bankroll += hand_profit
            if self.current_bankroll < 0 or current_profit > 25000 or self.num_reshufles >= int(round(num_games/50,0)):
                break
        average_bet = sum(self.bet_tracker)/len(self.bet_tracker)
        average_profit_per_hand = sum(winnings_per_hand)/len(winnings_per_hand)
        
        TotalProfit = sum(self.profit)
        arr = [Ruin_count,tenK_count]
        return arr

            

if "__main__" == __name__:
    cards = []
    game = Game(6,1)
    for i in range(100):
        cards += [random.choice(game.cards_in_shoe)]
        game.cards_in_shoe.remove(cards[i])
    game.count(cards)
    game.cards_played += cards
    for i in range(20):
        game.play_hand()
    print(f"Play Erros: {game.play_errors}")
    print(f"Profit: {sum(game.profit)}")
    print(f"Won: {game.numWins}, Lost: {game.numLosses}, Pushed: {game.numPushes}")