
import time
import random
from random import shuffle
import math
from queue import Queue
import csv
import matplotlib.pyplot as plt



class blackjack():
    def __init__(self, num_decks, H17, DAS, Surrender, Insurance, min_bet, max_bet, starting_bankroll):
        # Typically 6 or 8
        self.num_decks = num_decks

        # True or False values
        self.H17 = H17
        self.DAS = DAS
        self.Surrender = Surrender
        self.insurance = Insurance

        # anywhere from 10/25 to 100/1000
        self.min_bet = min_bet
        self.max_bet = max_bet

        #shoe builder
        self.shoe = self.initialize_shoe(num_decks)

        #player and dealer cards
        self.player_cards = []      #will be a list of lists (more spots / split paris)
        self.dealer_cards = []      #will be a list of cards
        self.hidden_dealer_card = 0
        self.num_player_hands = 1      #starts every game wiht 1 hand, might play more spots when count is high or split pairs

        #counting stuff
        self.running_count = 0
        self.true_count = 0
        self.num_cards_dealt = 0

        #optimal play
        self.strategy_card = self.build_strategy_card()

        #bankroll, bets, and money stuff
        self.starting_bankroll = starting_bankroll
        self.current_bankroll = starting_bankroll       #updates as play progresses
        self.optimal_bet = 0        #determined by count
        self.spots_to_play = 1      #will remain as 1 until I decide to incorporate multiple spots
        self.bets = []
        self.total_wagered = 0
        self.wager_sum = 0
        self.EV_Tracker = 0

        #Things to remember and keep track of during play
        self.current_spot = 0   #index in the self.player_cards array that we are currently playing
        self.num_splits = 0     #number of times I've split my starting spot
        self.max_splits = 4

        #tracking performance
        self.profit = 0
        self.num_hands_played = 0
        self.num_shoes_played = 0
        self.path = []
        self.countEV = {i: [0,0,0,0,1] for i in range(-30,31)} #profit, wagered, ev at that count, num dealer_busts, num_hands
        self.print_in_hand = False

        self.dealer_upcards = []

    def initialize_shoe(self, num_decks):
        cards = [2,3,4,5,6,7,8,9,10,10,10,10,11]
        shoe = []
        for card in cards:
            shoe += [card]*(num_decks*4)
        random.shuffle(shoe)
        return shoe
    
    def build_strategy_card(self):
        strategy_card = {"HardTotal": {}, "SoftTotal": {}, "Pair": {}, "Surrender": {}}
        card = []
        if self.H17:
            with open('H-17.csv', 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    updated_row = row[0:3]
                    for i in range(3,13):
                        try:
                            arr = row[i].split(".")
                            arr[1] = int(arr[1])
                            #arr[3] = arr[0]         #INCLUDE THIS FOR OPTIMAL PLAY WITHOUT COUNTING CARDS
                        except IndexError:
                            arr = []
                        updated_row += [arr]
                    card += [updated_row]
        else:
            with open('S-17.csv', 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    updated_row = row[0:3]
                    for i in range(3,13):
                        arr = row[i].split(".")
                        try:
                            arr[1] = int(arr[1])
                            #arr[3] = arr[0]         #INCLUDE THIS FOR OPTIMAL PLAY WITHOUT COUNTING CARDS
                        except IndexError:
                            arr = []
                        updated_row += [arr]
                    card += [updated_row]
        for i in range(len(card)):
            if i <= 9: #hardTotals
                strategy_card["HardTotal"].update({int(card[i][0]): card[i][1:]})                
            elif i<= 17: #softTotals
                strategy_card["SoftTotal"].update({card[i][0]: card[i][1:]})
            elif i<= 27: #pair
                strategy_card["Pair"].update({int(card[i][0]): card[i][1:]})
            else:
                strategy_card["Surrender"].update({card[i][0]: card[i][1:]})
        return strategy_card
    
    def play_blackjack(self, num_hands_or_shoes):
        #while self.num_hands_played <= num_hands_or_shoes:
        while self.num_shoes_played < num_hands_or_shoes:
            self.play_a_shoe()
            self.new_shoe()
    
    def play_a_shoe(self):
        #choose the cut card spot, play until that many cards are dealt

        cut_card = (self.num_decks-1)*52 -39 + int(random.random()*26)

        while self.num_cards_dealt<cut_card:
            self.num_hands_played += 1
            start_true_count = self.true_count
            winnings = self.play_a_hand()

            if start_true_count in self.countEV.keys():
                self.countEV[start_true_count][0] += winnings
                self.countEV[start_true_count][1] += 1
                self.countEV[start_true_count][2] = round(self.countEV[start_true_count][0]/self.countEV[start_true_count][1],4)
            else:
                self.countEV.update({start_true_count: [winnings,1,winnings]})


        self.num_shoes_played += 1

    def deal_n_cards(self, n):
        cards = []
        for i in range(n):
            cards += [self.shoe.pop()]
        self.num_cards_dealt += n
        self.count(cards)
        return cards

    def count(self,cards):
        for card in cards:
            if card >= 10:
                self.running_count -= 1
            if card <= 6:
                self.running_count += 1
        self.true_count = int(round(self.running_count/(self.num_decks-self.num_cards_dealt/52),0))

    def place_bets(self):
        self.bet_per_spot = 1
        #will change to vary in terms of count later
        self.bets = [self.bet_per_spot for i in range(self.num_player_hands)]
        self.total_wagered = sum(self.bets)

    def deal_initial_cards(self):
        spots = self.num_player_hands
        self.player_cards = [[] for i in range(spots)]
        self.dealer_cards = []
        cards = self.deal_n_cards(1+2*spots)
        #deals the player cards and dealer up-card
        for i in range(spots):
            self.player_cards[i] += [cards.pop()]
        self.dealer_cards += [cards.pop()]
        for i in range(spots):
            self.player_cards[i] += [cards.pop()]
        #deals the dealer's hidden card
        self.hidden_dealer_card = self.shoe.pop()
        #Must remember to count this card after it is turned over!
        self.num_cards_dealt += 1

    def deviate(self, table, key, dealercard):      #returns False if no info
        try:
            move_info = self.strategy_card[table][key][dealercard]
        except KeyError:
            return False
        if move_info == []:
            return False
        elif move_info[1]==0:
            if (move_info[2] == "+" and self.running_count > 0) or (move_info[2] == "-" and self.running_count < 0):
                return move_info[3]
            else:
                return move_info[0]
        else:
            if (move_info[2] == "+" and self.true_count >= move_info[1]) or (move_info[2] == "-" and self.true_count <= move_info[1]):
                return move_info[3]
            else:
                return move_info[0]
    
    def can_double(self, cards):
        if len(cards) != 2:
            return False
        else:
            if self.num_splits == 0:
                return True
            elif self.DAS:
                return True
        return False

    def determine_move(self):
        dc = self.dealer_cards[0]
        if self.player_cards[self.current_spot] in [[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,10],[11,11]]:
            #should we split?
            pair_move = self.deviate("Pair", self.player_cards[self.current_spot][0], dc)
            if (pair_move == "Y" or (pair_move == "Y/N" and self.DAS == True)) and self.num_splits < self.max_splits:
                #return "Split"
                self.split()
        if len(self.player_cards[self.current_spot])==2:
            #should we surrender?
            surr_move = self.deviate("Surrender", str(sum(self.player_cards[self.current_spot])), dc)
            if surr_move == "Surr" and self.num_splits == 0 and self.Surrender == True:
                return "Surr"
        #hit stand or double?
        if 11 in self.player_cards[self.current_spot]:
            table = "SoftTotal"
            num = sum(self.player_cards[self.current_spot])-11
            key = "A."+str(num)
            move = self.deviate(table, key,dc)
            if self.player_cards[self.current_spot] == [11]:
                return "Ace"
        else:
            table = "HardTotal"
            if sum(self.player_cards[self.current_spot])<8:
                return "H"
            move = self.deviate(table, sum(self.player_cards[self.current_spot]),dc)
        if (move == "D" or move == "Ds") and self.can_double(self.player_cards[self.current_spot]):
            return "D"
        elif move == "H" or move == "D":
            return "H"
        else:
            return "S"
        
    def deal_one_card(self):
        card = self.shoe.pop()
        self.num_cards_dealt += 1
        self.count([card])
        return card

    def hit(self):
        card = self.deal_one_card()
        self.player_cards[self.current_spot] += [card]

    def split(self):
        self.num_splits += 1
        i = self.current_spot
        array = self.player_cards[:i] + [[self.player_cards[i][0]], [self.player_cards[i][0]]] + self.player_cards[i+1:]
        self.player_cards = array
        bet_array = self.bets[:i] + [self.bet_per_spot] + [self.bet_per_spot] + self.bets[i+1:] 
        self.bets = bet_array
        self.total_wagered += self.bet_per_spot

    def surrender(self):
        self.player_cards[self.current_spot] = [12,12]
        self.bets[self.current_spot] = self.bets[self.current_spot]/2

    def hit_dealer(self):
        card = self.deal_one_card()
        self.dealer_cards += [card]
        if 11 in self.dealer_cards and sum(self.dealer_cards)>21:
            self.dealer_cards.remove(11)
            self.dealer_cards += [1]

    def new_shoe(self):
        self.shoe = self.initialize_shoe(self.num_decks)
        self.running_count = 0
        self.true_count = 0
        self.num_cards_dealt = 0

    def play_a_hand(self):
        start_true_count = self.true_count
        self.place_bets()
        self.deal_initial_cards()
        winnings = 0
        if self.print_in_hand:
            print()
            print(f"dealer card:  {self.dealer_cards}")
            print(f"player cards: {self.player_cards}")
            print(f"bets:         {self.bets}")

        #if dealer has blackjack:
        if self.dealer_cards[0] == 11:
            insurance_bet = 0
            if self.true_count >= 3 and self.insurance:
                insurance_bet = sum(self.bets)/2
                self.total_wagered += insurance_bet      #taken insurance
            if self.hidden_dealer_card == 10:           #dealer has BJ
                winnings += 2*insurance_bet
                for hand in self.player_cards:
                    if hand not in [[10,11],[11,10]]:   #dealer has BJ, you don't
                        winnings -= self.bets[0]
                    else:                           #dealer has BJ, and you do too
                        winnings += 0
                self.EV_Tracker += winnings/self.total_wagered
                self.wager_sum += self.total_wagered
                self.profit += winnings

                if self.print_in_hand:
                    print("dealer blackjack:")
                    print(f"total bets:     {self.bets}")
                    print(f"total winnings: {winnings}")
                    print(f"total wagered:  {self.total_wagered}")
                    print(f"wager sum:      {self.wager_sum}")
                    print(f"total profit:   {self.profit}")

                self.countEV[start_true_count][0] += winnings
                self.countEV[start_true_count][1] += self.total_wagered
                self.countEV[start_true_count][2] = round(self.countEV[start_true_count][0]/self.countEV[start_true_count][1],4)
                return winnings    
            else:                               #dealer does not have blackjack
                winnings -= insurance_bet
        if self.dealer_cards[0] == 10:
            if self.hidden_dealer_card == 11:           #dealer has BJ
                for hand in self.player_cards:
                    if hand not in [[10,11],[11,10]]:   #dealer has BJ, you don't
                        winnings -= self.bets[0]
                    else:                           #dealer has BJ, and you do too
                        winnings += 0
                self.EV_Tracker += winnings/self.total_wagered
                self.wager_sum += self.total_wagered
                self.profit += winnings
                if self.print_in_hand:
                    print("dealer blackjack:")
                    print(f"total bets:     {self.bets}")
                    print(f"total winnings: {winnings}")
                    print(f"total wagered:  {self.total_wagered}")
                    print(f"wager sum:      {self.wager_sum}")
                    print(f"total profit:   {self.profit}")
                
                self.countEV[start_true_count][0] += winnings
                self.countEV[start_true_count][1] += self.total_wagered
                self.countEV[start_true_count][2] = round(self.countEV[start_true_count][0]/self.countEV[start_true_count][1],4)
                return winnings    
            
        #if player(s) has blackjack
        for i in range(len(self.player_cards)):
            if self.player_cards[i] in [[10,11],[11,10]]:
                winnings += self.bets[i]*1.5
                self.player_cards[i] = [0,0]
            
        #begin player action
        self.current_spot = 0
        while self.current_spot < len(self.player_cards):
            if self.print_in_hand:
                print(f"spot: {self.current_spot}")
                print(f"Player Cards: {self.player_cards}")
            while True:
                if self.player_cards[self.current_spot] == [0,0]:
                    break
                if sum(self.player_cards[self.current_spot]) >21:
                    if 11 in self.player_cards[self.current_spot]:
                        if self.player_cards[self.current_spot] == [11,11]:
                            self.split()
                            continue
                        self.player_cards[self.current_spot].remove(11)
                        self.player_cards[self.current_spot] += [1]
                    else:
                        break
                move = self.determine_move()   #returns a legal move
                if self.print_in_hand:
                    print(f"move: {move}")
                if move == "H":
                    self.hit()
                    continue
                elif move == "S":
                    break
                elif move == "D":
                    self.total_wagered += self.bets[self.current_spot]
                    self.bets[self.current_spot] = self.bets[self.current_spot]*2
                    self.hit()
                    break
                elif move == "Split":
                    self.split()
                    continue
                elif move == "Surr":
                    self.surrender()
                    break
                elif move == "Ace":
                    self.hit()
                    break
                break

            self.current_spot += 1
            if  self.current_spot - self.num_splits ==1:
                self.num_splits = 0
        
        if self.print_in_hand:
            print()
            print(f"Player Cards: {self.player_cards}")

        #begin dealer action
        if self.hidden_dealer_card in [10,11]:
            self.running_count -= 1
        if self.hidden_dealer_card in [2,3,4,5,6]:
            self.running_count += 1
        self.true_count = int(round(self.running_count/(self.num_decks-self.num_cards_dealt/52),0))
        self.dealer_cards += [self.hidden_dealer_card]
        while sum(self.dealer_cards)<= 17:
            ds = sum(self.dealer_cards)
            if ds< 17:
                self.hit_dealer()
                continue
            elif ds == 17 and 11 in self.dealer_cards and self.H17 == True:
                self.hit_dealer()
            elif ds <= 21:
                break
            if ds>21 and 11 in self.dealer_cards:
                self.dealer_cards.remove(11)
                self.dealer_cards += [1]
                continue
        
        if self.print_in_hand:
            print(f"Dealer Cards: {self.dealer_cards}, {sum(self.dealer_cards)}")
        
        #tally up the wins and losses
        dealer_sum = sum(self.dealer_cards)
        for i in range(len(self.player_cards)):
            spot = self.player_cards[i]
            if spot == [0,0]:
                continue
            if sum(spot) >21:
                winnings -= self.bets[i] #lose your bet
                continue
            else:
                if dealer_sum >21:
                    winnings += self.bets[i] #win your bet
                else:
                    if sum(spot) > dealer_sum:
                        winnings += self.bets[i] #win your bet
                    elif sum(spot) < dealer_sum:
                        winnings -= self.bets[i] #lose your bet
                    # otherwise push or blackjack so already paid out
        self.wager_sum += self.total_wagered
        self.profit += winnings
        if self.print_in_hand:
            print(f"total bets:     {self.bets}")
            print(f"total winnings: {winnings}")
            print(f"total wagered:  {self.total_wagered}")
            print(f"wager sum:      {self.wager_sum}")
            print(f"total profit:   {self.profit}")
        
        self.countEV[start_true_count][0] += winnings
        #self.countEV[start_true_count][1] += self.total_wagered
        self.countEV[start_true_count][1] += 1
        self.countEV[start_true_count][2] = round(self.countEV[start_true_count][0]/self.countEV[start_true_count][1],4)
        if dealer_sum > 21:
            self.countEV[start_true_count][3]+= 1
        self.countEV[start_true_count][4] += 1
        return winnings

    def test_dealer_bust(self, n):
        Tcount = 0
        Rcount = 0
        dictionary = {i: [0,1,0] for i in range(-30,31)}

        for i in range(n):
            start_Tcount = Tcount
            if len(self.shoe)<52*5:
                self.shoe = self.initialize_shoe(6)

                Tcount = 0
                Rcount = 0

            dealer_cards = [self.shoe.pop()]
            
            while sum(dealer_cards)< 17:
                dealer_cards += [self.shoe.pop()]
                if sum(dealer_cards)>21 and 11 in dealer_cards:
                    dealer_cards.remove(11)
                    dealer_cards += [1]
            bust = 0
            if sum(dealer_cards)>21:
                bust = 1
            dictionary[Tcount][0]+=bust
            dictionary[Tcount][1]+=1
            dictionary[Tcount][2] = round(dictionary[Tcount][0]/dictionary[Tcount][1],4)
            for card in dealer_cards:
                if card >=10:
                    Rcount -= 1
                if card <=6:
                    Rcount += 1
            Tcount = int(round(Rcount / (len(self.shoe)/52),0))
        
        return dictionary
        



if "__main__" == __name__:
    start = time.time()
    num_decks, H17, DAS = 6, True, False
    Surrender, Insurance = False, False
    min_bet, max_bet, starting_bankroll = 10, 1000, 10000
    self = blackjack(num_decks,H17,DAS,Surrender,Insurance, min_bet, max_bet, starting_bankroll)
  
    '''
    dictionary = self.test_dealer_bust(10000000)
    for i in range(-8,9):
        print(i, dictionary[i][2], dictionary[i][1])
    '''
    cut_card = int((self.num_decks * 52) * 0.75 + random.randint(0, 20))
    #for i in range(1000000):
    for i in range(1000000):
        if self.num_cards_dealt > cut_card:
            self.new_shoe()
            cut_card = int((self.num_decks * 52) * 0.75 + random.randint(0, 20))
        start_true_count = self.true_count
        winnings = self.play_a_hand()
    
    print()
    print(f"Total EV: {self.profit / self.wager_sum}")

    for i in range(-8,9):
        key = i
        prof = self.countEV[key][0]
        change = round(self.countEV[key][2] - self.countEV[key-1][2],4)
        ev = self.countEV[key][2]
        busts = round(self.countEV[key][3]/self.countEV[key][4],4)
        if i >=0:
            print(f" {key}, {ev}, {busts},   {self.countEV[key][4]}")
        else:
            print(f"{key}, {ev}, {busts},    {self.countEV[key][4]}")

    print()
    print(sum(self.dealer_upcards) / len(self.dealer_upcards))

    print("time:", time.time()-start)
    print()
    #plt.show()



