import matplotlib.pyplot as plt
import random
import math
import time

class Game():
    def __init__(self, num_decks):
        self.num_decks = num_decks
        self.shoe = self.shoe_initializer()
        self.strategy_card_base = self.strategy_card_initializer()
        self.strategy_card = self.strategy_card_base

        self.running_count = 0
        self.true_count = 0
        self.player_cards = []
        self.dealer_cards = []

        self.take_break = 0

        self.num_wins = 0
        self.num_losses = 0
        self.num_pushes = 0

        self.split_hands = []
        self.split_index = 0

        self.cut_card = self.cut_card_initializer()

        self.bet = 0
        self.table_minimum = 10
        self.table_maximum = 500
        self.starting_bankroll = 5000
        self.current_bankroll = 5000
        self.profit = 0

    def shoe_initializer(self):
        decks = self.num_decks
        shoe = []
        for i in range(2,12):
            if i==10:
                for j in range(16*decks):
                    shoe += [10]
            else:
                for j in range(4*decks):
                    shoe += [i]
        random.shuffle(shoe)
        return shoe

    def strategy_card_initializer(self):
        HardSums = ['0,H,H,H,H,H,H,H,H,H,H','1,H,H,H,H,H,H,H,H,H,H','2,H,H,H,H,H,H,H,H,H,H','3,H,H,H,H,H,H,H,H,H,H','4,H,H,H,H,H,H,H,H,H,H','5,H,H,H,H,H,H,H,H,H,H','6,H,H,H,H,H,H,H,H,H,H','7,H,H,H,H,H,H,H,H,H,H','8,H,H,H,H,H,H,H,H,H,H','9,H,D,D,D,D,H,H,H,H,H','10,D,D,D,D,D,D,D,D,H,H','11,D,D,D,D,D,D,D,D,D,H','12,H,H,S,S,S,H,H,H,H,H','13,S,S,S,S,S,H,H,H,H,H','14,S,S,S,S,S,H,H,H,H,H','15,S,S,S,S,S,H,H,H,H,H','16,S,S,S,S,S,H,H,H,H,H','17,S,S,S,S,S,S,S,S,S,S','18,S,S,S,S,S,S,S,S,S,S','19,S,S,S,S,S,S,S,S,S,S','20,S,S,S,S,S,S,S,S,S,S','21,S,S,S,S,S,S,S,S,S,S']
        SoftSums = ['0,H,H,H,H,H,H,H,H,H,H','2,H,H,H,D,D,H,H,H,H,H','3,H,H,H,D,D,H,H,H,H,H','4,H,H,D,D,D,H,H,H,H,H','5,H,H,D,D,D,H,H,H,H,H','6,H,D,D,D,D,H,H,H,H,H','7,S,D,D,D,D,S,S,H,H,H','8,S,S,S,S,S,S,S,S,S,S','9,S,S,S,S,S,S,S,S,S,S','10,S,S,S,S,S,S,S,S,S,S']
        Pairs = ['2,SP,SP,SP,SP,SP,SP,H,H,H,H','3,SP,SP,SP,SP,SP,SP,H,H,H,H','4,H,H,H,SP,SP,H,H,H,H,H','5,D,D,D,D,D,D,D,D,H,H','6,SP,SP,SP,SP,SP,H,H,H,H,H','7,SP,SP,SP,SP,SP,SP,H,H,H,H','8,SP,SP,SP,SP,SP,SP,SP,SP,SP,SP','9,SP,SP,SP,SP,SP,S,SP,SP,S,S','10,S,S,S,S,S,S,S,S,S,S','11,SP,SP,SP,SP,SP,SP,SP,SP,SP,SP']
        decisions = {"HardSums": {}, "SoftSums": {}, "Pairs": {}}
        for list in HardSums:
            arr = list.split(",")
            arr[0] = int(arr[0])
            decisions['HardSums'].update({arr[0]: [0,0]+arr[1:]})
        for list in SoftSums:
            arr = list.split(",")
            arr[0] = int(arr[0])
            decisions['SoftSums'].update({arr[0]: [0,0]+arr[1:]})
        for list in Pairs:
            arr = list.split(",")
            arr[0] = int(arr[0])
            decisions['Pairs'].update({arr[0]: [0,0]+arr[1:]})
        return decisions

    def strtegy_deviations(self):
        self.strategy_card = self.strategy_card_base
        count = self.true_count
        if self.running_count > 0:
            self.strategy_card["HardSums"][16][10] = "S"
        if self.running_count < 0:
            self.strategy_card["HardSums"][12][4] = "H"
        if count >=1:
            self.strategy_card["SoftSums"][8][5] = "D"
            self.strategy_card["SoftSums"][8][6] = "D"
            self.strategy_card["SoftSums"][6][2] = "D"
            self.strategy_card["HardSums"][11][11] = "D"
            self.strategy_card["HardSums"][9][2] = "D"
        if count <= -1:
            self.strategy_card["HardSums"][13][2] = "H"
        if count >=2:
            self.strategy_card["HardSums"][12][3] = "S"
            self.strategy_card["HardSums"][8][6] = "D"
        if count >=3:
            self.strategy_card["SoftSums"][8][4] = "D"
            self.strategy_card["HardSums"][12][2] = "S"
            self.strategy_card["HardSums"][9][7] = "D"
        if count >= 4:
            self.strategy_card["HardSums"][10][10] = "D"
            self.strategy_card["HardSums"][10][11] = "D"
            self.strategy_card["HardSums"][15][10] = "S"
            self.strategy_card["HardSums"][16][10] = "S"
            self.strategy_card["Pairs"][10][6] = "SP"
        if count >= 5:
            self.strategy_card["Pairs"][10][5] = "SP"
        if count >= 6:
            self.strategy_card["Pairs"][10][4] = "SP"

    def count_cards(self, cards):
        for card in cards:
            if card <=6:
                self.running_count += 1
            if card >= 10:
                self.running_count += -1
        decks_left = int(round(len(self.shoe)/52,0))
        if decks_left > 0:
            self.true_count = int(round(self.running_count/decks_left,0))
        else:
            self.true_count = self.running_count
        
    def deal_cards(self):
        cards = []
        for i in range(3):
            cards += [random.choice(self.shoe)]
            self.shoe.remove(cards[i])
        self.count_cards(cards)
        self.player_cards = [cards[0],cards[2]]
        self.dealer_cards = [cards[1]]
        self.split_hands = [self.player_cards]
        self.split_index = 0
    
    def cut_card_initializer(self):
        cut_card = random.randint(self.num_decks*52*(2/3), self.num_decks*52*(5/6))
        return cut_card

    def reshuffle(self):
        self.shoe = self.shoe_initializer()
        self.running_count = 0
        self.true_count = 0
        self.cut_card = self.cut_card_initializer()

    def initialize_bets(self):
        bet = self.table_minimum
        count = self.true_count
        #if count < 4:
        #    bet = self.table_maximum*2/(6-count)
        #if count >= 4:
        #    bet = self.table_maximum
        #if bet < self.table_minimum:
        #    bet = self.table_minimum
        if count>0:
            bet = self.table_minimum*(3**count)
        if bet > self.table_maximum:
            bet = self.table_maximum
        self.bet = bet

    def play_hand(self):
        if len(self.shoe) <= 52*self.num_decks - self.cut_card:
            self.reshuffle()
        self.player_cards, self.dealer_cards = [],[]
        self.initialize_bets()
        self.deal_cards()

        cards = self.player_cards
        action = self.decide_player_action(cards)
        keep_going = self.player_move(action)
        cards = self.player_cards
        if sum(cards)>21 and 11 in cards:
            self.player_cards.remove(11)
            self.player_cards += [1]
            cards = self.player_cards
        while keep_going == True and sum(cards)<=21:
            action = self.decide_player_action(cards)
            keep_going = self.player_move(action)
            cards = self.player_cards
            if sum(cards)>21 and 11 in cards:
                self.player_cards.remove(11)
                self.player_cards += [1]
                cards = self.player_cards
        if action == "SP" or action == "Surr":
            return None
        score = sum(cards)
        if score == 21 and len(cards) ==2:
            self.payout(score, True)
        else:
            self.payout(score, False)

    def payout(self, score, blackjack):
        dealer_score = sum(self.dealer_cards)
        while dealer_score <17:
            card = random.choice(self.shoe)
            self.shoe.remove(card)
            self.dealer_cards += [card]
            dealer_score = sum(self.dealer_cards)
            if dealer_score >21 and 11 in self.dealer_cards:
                self.dealer_cards.remove(11)
                self.dealer_cards += [1]
                dealer_score = sum(self.dealer_cards)
        if blackjack == True:
            if dealer_score ==21 and len(self.dealer_cards) ==2:
                self.profit += 0
                self.num_pushes +=1
            else:
                self.profit += self.bet*1.5
                self.num_wins +=1
        else:
            if score > 21:
                self.profit += -self.bet
                self.num_losses +=1
            else:
                if dealer_score >21:
                    self.profit += self.bet
                    self.num_wins +=1
                elif score > dealer_score:
                    self.profit += self.bet
                    self.num_wins +=1
                elif score < dealer_score:
                    self.profit += -self.bet
                    self.num_losses +=1
                else:
                    if dealer_score == 21 and len(self.dealer_cards)==2:
                        self.profit += -self.bet
                        self.num_losses += 1
                    else:
                        self.profit += 0
                        self.num_pushes +=1


    #don't call player_action if sum(cards) > 21
    #returns "S", "H", "D", "SP", "Surr" *** still need to implement "Surr"
    def decide_player_action(self, cards):
        self.strtegy_deviations()
        dealer_card = self.dealer_cards[0]
        #if len(cards) == 2 and self.split_index==0:
        if len(cards) == 2:
            action = self.surrender()
            if action == False:
                return "Surr"
        if len(cards)==2 and cards[0]==cards[1]:
            action= self.strategy_card["Pairs"][cards[0]][dealer_card]
            return action
        elif 11 in cards:
            score = sum(cards) -11
            action = self.strategy_card["SoftSums"][score][dealer_card]
            return action
        else:
            score = sum(cards)
            action = self.strategy_card["HardSums"][score][dealer_card]
            return action
    
    #returns true if need to keep going
    def player_move(self,action):
        if action == "Surr":
            return False
        if action == "S":
            return False
        if action == "H":
            self.hit_player()
            return True
        if action == "D":
            self.double()
            return False
        if action == "SP":
            self.split()
            return False
        if action == "Surr":
            self.surrender()
            return False
    
    def hit_player(self):
        card = random.choice(self.shoe)
        self.shoe.remove(card)
        self.player_cards += [card]

    def double(self):
        card = random.choice(self.shoe)
        self.shoe.remove(card)
        self.player_cards += [card]
        self.bet = self.bet * 2

    def split(self):
        self.split_hands.pop(self.split_index)

        self.player_cards.remove(self.player_cards[0])
        self.split_hands += [[self.player_cards[0]], [self.player_cards[0]]]

        while self.split_index < len(self.split_hands):
            self.player_cards = self.split_hands[self.split_index]
            cards = self.player_cards
            action = self.decide_player_action(cards)
            keep_going = self.player_move(action)
            cards = self.player_cards
            if (sum(cards)>21 and 11 in cards) and not (len(cards)==2 and cards[0]==cards[1]):
                self.player_cards.remove(11)
                self.player_cards += [1]
                cards = self.player_cards
            while keep_going == True and sum(cards)<=21:
                action = self.decide_player_action(cards)
                keep_going = self.player_move(action)
                cards = self.player_cards
                if sum(cards)>21 and 11 in cards:
                    self.player_cards.remove(11)
                    self.player_cards += [1]
                    cards = self.player_cards
            score = sum(cards)
            if score == 21 and len(cards) ==2:
                self.payout(score, True)
            else:
                self.payout(score, False)
            self.split_index += 1

    def surrender(self):
        cards = self.player_cards
        dealer_card = self.dealer_cards[0]
        count = self.true_count
        if sum(cards) == 16 and 11 not in cards:
            if (dealer_card in [10,11]) or (dealer_card==9 and count > -1) or (dealer_card==8 and count >= 4):
                self.profit += -self.bet/2
                self.num_losses += 0.5
                self.num_wins += 0.5
                self.bet = 0
                return False
        elif sum(cards) == 15 and 11 not in cards:                                                       #dealer_card==11  and count >=2     for S17
            if (dealer_card==9 and count>=2) or (dealer_card == 10 and count > 0) or (dealer_card==11  and count >=2): #for S17
                self.profit += -self.bet/2
                self.bet = 0
                self.num_losses += 0.5
                self.num_wins += 0.5
                return False
        else:
            return True

    def reset_day(self):
        self.shoe = self.shoe_initializer()
        self.running_count = 0
        self.true_count = 0
        self.cut_card = self.cut_card_initializer()
        self.profit = 0
        self.current_bankroll = self.starting_bankroll

    def test_play_rounds(self, n):
        X=[]
        profit = []
        bets =[]
        for i in range(n):
            game.play_hand()
            X+=[i]
            profit += [game.profit]
            bets += [game.bet]
        print(f"TotalBets: {sum(bets)}, AverageBet: {round(sum(bets)/len(bets),3)}")
        print(f"TotalProfit: {profit[-1]}, AverageProfit: {sum(profit[i]-profit[i-1] for i in range(1,len(profit)))/(len(profit)-1)}")
        plt.plot(X,profit)
        plt.show()

    def test_120_round_profit_RoR(self):
        n=1000
        Days = []
        ruin_count = 0
        EndResults = []
        for day in range(n):
            Days += [day]
            for i in range(120):
                old_profit = self.profit
                self.play_hand()
                self.current_bankroll += (self.profit - old_profit)
                if self.current_bankroll < 0:
                    ruin_count += 1
                    break  
                if self.current_bankroll - self.starting_bankroll > self.starting_bankroll:
                    break  
            EndResults += [self.profit]
            self.reset_day()
        print(f"Risk of Ruin: {100*ruin_count/n}%")
        print(f"AverageEndProfit: {sum(EndResults)/len(EndResults)}")        
        plt.scatter(Days,EndResults,s=10)
        plt.show()

    def test_show_winRate_by_count(self):
        dictionary = {}
        n=100000
        for i in range(n):
            count = game.true_count
            wins = game.num_wins
            losses = game.num_losses
            game.play_hand()
            if count in dictionary.keys():
                dictionary[count][0] += 1
                if game.num_wins > wins:
                    dictionary[count][1] += 1
                if game.num_losses > losses:
                    dictionary[count][2] += 1
                dictionary[count][3] = round(100*dictionary[count][1]/dictionary[count][0],2)
                dictionary[count][4] = round(100*dictionary[count][2]/dictionary[count][0],2)
                dictionary[count][5] = round((dictionary[count][4] - dictionary[count][3]),2)
            else:
                if game.num_wins > wins:                            # 0      1     2      3      4     5
                    dictionary.update({count: [1, 1, 0, 0, 0, 0]}) #total, wins, losses, win%, loss%, casinoEdge
                elif game.num_losses > losses:
                    dictionary.update({count: [1, 0, 1, 0, 0, 0]})
                else:
                    dictionary.update({count: [1, 0, 0, 0, 0, 0]})
            
        keys = dictionary.keys()
        for key in sorted(keys):
            print(key, dictionary[key])
        num_wins = game.num_wins
        num_losses = game.num_losses
        num_pushes = game.num_pushes
        print()
        print(f"Win: {round(100*num_wins/n,2)}%, Loss: {round(100*num_losses/n,2)}%, Push: {round(100*num_pushes/n, 2)}%")
        print(f"Casino Edge: {round(100*(num_losses/n - num_wins/n),2)}")

if "__main__" == __name__:
    game = Game(6)
    n = 120
    game.test_120_round_profit_RoR()


        
    


'''
    game = Game(6)
    n=1000000
    for i in range(n):
        game.play_hand()
        
    num_wins = game.num_wins
    num_losses = game.num_losses
    num_pushes = game.num_pushes
    #print(f"Wins: {num_wins}, Losses: {num_losses}, Pushes: {num_pushes}")
    print(f"Win: {round(100*num_wins/n,2)}%, Loss: {round(100*num_losses/n,2)}%, Push: {round(100*num_pushes/n, 2)}%")
    print(f"Casino Edge: {round(100*(num_losses/n - num_wins/n),2)}")
    print()
'''
'''
    game = Game(6)
    X=[]
    profit = []
    bets =[]
    for i in range(120):
        game.play_hand()
        X+=[i]
        profit += [game.profit]
        bets += [game.bet]
    print(f"TotalBets: {sum(bets)}, AverageBet: {round(sum(bets)/len(bets),3)}")
    print(f"TotalProfit: {profit[-1]}, AverageProfit: {sum(profit[i]-profit[i-1] for i in range(1,len(profit)))/(len(profit)-1)}")
    plt.plot(X,profit)
    plt.show()
'''