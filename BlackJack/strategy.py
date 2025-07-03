
import random
import math
import queue
import csv
import time
import matplotlib.pyplot as plt


class Game():
    def __init__(self, num_decks, S17):

        self.strategy = {"HardSum": {}, "SoftSum": {}, "Pair": {}, "Surr": {}}
        if S17==True:
            self.strategy_reader()

        self.num_decks = num_decks
        self.cards = self.build_cards(num_decks)
        self.deck = queue.Queue()
        self.shuffle_deck()
        self.stale_count_in_a_row = 0

        self.runningCount = 0
        self.trueCount = 0
        self.num_dealt_cards = 0
        self.cut_card = num_decks*52 - 30
        
        self.mistake_count = 0

        self.num_hands = 0
        self.player_cards = []
        self.scores = []
        self.dealer_cards = []

        self.starting_bankroll = 8000
        self.bankroll = self.starting_bankroll
        self.bets = []       #amount placed on each hand
        self.profit = 0
        self.total_wagered = 0

        self.num_rounds_played = 0
        self.split_hands = []

        self.minimum_bet = 10
        self.maximum_bet = 120
        self.blackjack_payout = 3/2

        self.lucky_ladies_side_bet = {}
        self.insurance_bets = 0

        self.make_mistakes = False          #False for perfect play, True for imperfect play
        self.mistake_frequency = 26         #running count error after every n cards dealt
        self.mistakes = []
        
        self.S_17 = False
        self.Surrender = False

        '''
        - BlackJack pays 3/2
        - Can only split aces once
          No hit aces after splitting
        - Yes double after splitting 
        - Yes early surrender
          No late surrender
        - S-17


        '''

    def reset_day(self):
        self.bankroll = self.starting_bankroll
        self.profit = 0
        self.total_wagered = 0
        self.num_rounds_played = 0
        self.shuffle_deck()
        self.mistake_count =0

    def strategy_reader(self):
        array = []
        with open('S-17.csv', 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                updated_row = row[0:3]
                for i in range(3,13):
                    arr = row[i].split(".")
                    try:
                        arr[1] = int(arr[1])
                        arr[3] = arr[0]         #INCLUDE THIS FOR OPTIMAL PLAY WITHOUT COUNTING CARDS
                    except IndexError:
                        arr = []
                    updated_row += [arr]
                array += [updated_row]
        array[18][0] = 11
        for i in range(0,10):
            self.strategy["HardSum"].update({int(array[i][0]): array[i][1:]})
        for i in range(10,18):
            self.strategy["SoftSum"].update({array[i][0]: array[i][1:]})
        for i in range(18,28):
            self.strategy["Pair"].update({int(array[i][0]): array[i][1:]})
        for i in range(28,30):
            self.strategy["Surr"].update({int(array[i][0]): array[i][1:]})
        
    def build_cards(self,num_decks):
        array = [2,3,4,5,6,7,8,9,10,10,10,10,11]
        cards = []
        for i in range(4*num_decks):
            for num in array:
                cards += [num]
        return cards
    
    def shuffle_deck(self):
        self.runningCount = 0
        self.mistake_count = 0
        self.trueCount = 0
        self.num_dealt_cards = 0
        random.shuffle(self.cards)
        self.deck = queue.Queue()
        for card in self.cards:
            self.deck.put(card)

    def deal_cards(self,n):
        cards = []
        for i in range(n):
            cards += [self.deck.get()]
        self.num_dealt_cards += n
        self.count(cards)
        return cards
    
    def count(self, cards):
        lows = [2,3,4,5,6]
        highs = [10,11]
        for card in cards:
            if card in lows:
                self.runningCount += 1
            if card in highs:
                self.runningCount += -1
        if round(self.num_decks - self.num_dealt_cards/52,0) == 0:
            self.trueCount == self.runningCount*2
        else:
            self.trueCount = int(self.runningCount/round(self.num_decks - self.num_dealt_cards/52,0))

    def deal_player_cards(self, num_hands):
        self.player_cards = []
        self.scores = []
        for num in range(num_hands):
            hand = self.deal_cards(2)
            self.player_cards += [hand]
    def deal_dealer_cards(self):
        self.dealer_cards = self.deal_cards(2)
    def deal_all_cards(self,num_hands):
        self.player_cards = []
        self.scores = []
        for num in range(num_hands):
            hand = self.deal_cards(1)
            self.player_cards += [hand]
        self.dealer_cards = self.deal_cards(1)
        for num in range(num_hands):
            self.player_cards[num] += self.deal_cards(1)
        self.dealer_cards += self.deal_cards(1)
    
    def choose_player_move(self, hand,spot):
        cards = hand
        score = sum(cards)
        if cards == [11,11]:
            if spot not in self.split_hands:
                return "Y"
            else:
                self.player_cards[spot] = [11,1]
                return "S"
        if cards == [11]:
            return "Hs"
        if score > 21:
            if 11 in cards:
                cards.remove(11)
                cards += [1]
                score = sum(cards)
            else:
                return "B"
        if score >= 17 and 11 not in cards:
            return "S"
        dealer_card = self.dealer_cards[0]
        #IF WE HAVE A PAIR
        if len(cards)==2 and cards[1] == cards[0]:
            key = cards[1]
            move = self.strategy["Pair"][key][dealer_card]
            if (move[2] == "+" and self.trueCount >= move[1]) or (move[2] == "-" and self.trueCount <= move[1]):
                return move[3]
            else:
                return move[0]
        #IF WE HAVE A SOFT SUM
        elif 11 in cards:
            if sum(cards) == 21:
                return "S"
            kicker = score - 11
            key = "A."+str(kicker)
            move = self.strategy["SoftSum"][key][dealer_card]
            if (move[2] == "+" and self.trueCount >= move[1]) or (move[2] == "-" and self.trueCount <= move[1]):
                return move[3]
            else:
                return move[0]
        #IF WE HAVE A HARD SUM
        #first check if we should surrender:
        elif self.Surrender == True and len(cards) == 2 and score in [15,16] and dealer_card in [11,10,9,8]:
            key = score
            move = self.strategy["Surr"][key][dealer_card]
            if move != []:
                if (move[2] == "+" and self.trueCount >= move[1]) or (move[2] == "-" and self.trueCount <= move[1]):
                    return move[3]
                else:
                    return move[0]
            else:
                move = self.strategy["HardSum"][key][dealer_card]
                if (move[2] == "+" and self.trueCount >= move[1]) or (move[2] == "-" and self.trueCount <= move[1]):
                    return move[3]
                else:
                    return move[0]
        #Make move off of hard sum
        else:
            key = score
            if key<8:
                return "H"
            move = self.strategy["HardSum"][key][dealer_card]
            if (move[2] == "+" and self.trueCount >= move[1]) or (move[2] == "-" and self.trueCount <= move[1]):
                return move[3]
            else:
                return move[0]

    
    def hit_player(self, hand):
        self.player_cards[hand] += self.deal_cards(1)
    
    def split_player(self, hand):
        new_hand = [self.player_cards[hand][1]]
        self.player_cards[hand] = new_hand
        self.player_cards += [new_hand]
        self.bets += [self.bets[hand]]
    def insurance(self):
        if self.dealer_cards[0] == 11 and self.trueCount >= 3:
            self.insurance_bets = sum(self.bets)/2
        else:
            self.insurance_bets = 0

    def run_hands(self, num_hands, bet):
        if self.make_mistakes == True:
            if self.num_dealt_cards/self.mistake_frequency > self.mistake_count + 1:
                self.mistake_count += 1
                mistake = random.choice([1,1,1,-1,-1,-1,0,0,2,-2])
                self.runningCount += mistake
                self.mistakes += [mistake]
        key = self.trueCount
        if self.num_dealt_cards > self.cut_card:
            self.shuffle_deck()
        self.bets = [bet for i in range(num_hands)]
        self.num_hands = num_hands
        self.deal_all_cards(num_hands)
        self.insurance()
        if sum(self.dealer_cards) == 21:
            starting_prof = self.profit
            for i in range(len(self.player_cards)):
                self.scores += [sum(self.player_cards[i])]
            self.payout()
            self.insurance_bets = 0
            profit = self.profit - starting_prof
            return profit
        spot = 0
        while spot < len(self.player_cards):
            hand = self.player_cards[spot]
            move = self.choose_player_move(hand, spot)
            if move == "Ds":
                if len(hand) == 2:
                    move = "D"
                else:
                    move = "S"
            if move == "D" and len(hand) > 2:
                move = "H"
            if move == "S":
                self.scores += [sum(self.player_cards[spot])]
                spot += 1
                continue
            elif move in ["B","Surr"]:
                spot += 1
                self.scores += [move]
                continue
            elif move == "H":
                self.hit_player(spot)
                continue
            elif move == "D":
                self.hit_player(spot)
                self.bets[spot] = self.bets[spot]*2
                score = sum(self.player_cards[spot])
                if score >21:
                    score += -10
                self.scores += [score]
                spot +=  1
                continue
            elif move == "Hs":
                self.hit_player(spot)
                score = sum(self.player_cards[spot])
                self.scores += [score]
                spot +=  1
                continue
            elif move == "Y" or move == "Y/N":
                self.split_hands += [spot]
                self.split_player(spot)
                self.split_hands += [len(self.player_cards)-1]
                continue
            elif move == "N":
                self.player_cards[spot] = [sum(hand)]
                continue
            else:
                self.scores += ["Surr"]
                spot += 1
        self.play_dealer()
        starting_prof = self.profit
        self.payout()
        self.insurance_bets = 0
        profit = self.profit - starting_prof
        return profit

    def play_dealer(self):
        dealer_score = sum(self.dealer_cards)
        while dealer_score < 17:
            self.dealer_cards += self.deal_cards(1)
            dealer_score = sum(self.dealer_cards)
            if dealer_score >21 and 11 in self.dealer_cards:
                self.dealer_cards.remove(11)
                self.dealer_cards += [1]
                dealer_score += -10
            if self.S_17 == False and dealer_score == 17 and 11 in self.dealer_cards:
                self.dealer_cards += self.deal_cards(1)
                dealer_score = sum(self.dealer_cards)
                if dealer_score >21:
                    self.dealer_cards.remove(11)
                    self.dealer_cards += [1]
                    dealer_score += -10

    def payout(self):
        prev_profit = self.profit
        if self.dealer_cards == [10,11] or self.dealer_cards == [11,10]:
            self.profit += self.insurance_bets
        dealer_score = sum(self.dealer_cards)
        self.total_wagered += sum(self.bets)
        if dealer_score > 21:
            for i in range(len(self.scores)):
                outcome = self.scores[i]
                if outcome == 21  and len(self.player_cards[i])==2:
                    self.profit += self.bets[i]*self.blackjack_payout
                elif type(outcome) == int:
                    self.profit += self.bets[i]
                elif outcome == "B":
                    self.profit += -self.bets[i]
                else:
                    self.profit += -self.bets[i]*(0.5)
        else:
            for i in range(len(self.scores)):
                outcome = self.scores[i]
                if outcome == 21  and len(self.player_cards[i])==2:
                    if dealer_score == 21 and len(self.dealer_cards) ==2:
                        self.profit += 0
                    else:
                        self.profit += self.bets[i]*self.blackjack_payout
                elif type(outcome) == int:
                    if outcome > dealer_score:
                        self.profit += self.bets[i]
                    elif outcome < dealer_score:
                        self.profit += -self.bets[i]
                    else:
                        if dealer_score == 21 and len(self.dealer_cards) ==2:
                            self.profit += -self.bets[i]
                elif outcome == "B":
                    self.profit += -self.bets[i]
                else:
                    self.profit += -self.bets[i]*(0.5)
        new_profit = self.profit - prev_profit
        self.bankroll += new_profit
            

    def optimal_bet(self):

        min_bet = self.minimum_bet
        onebet = 2*min_bet
        max_bet = self.maximum_bet

        scope = max_bet/min_bet
        scale = scope/8
        slope = (max_bet-onebet)/5

        if self.trueCount < 0:
            return min(min_bet, self.bankroll)      #10
        elif self.trueCount == 0:
            return min(min_bet, self.bankroll)        #10     
        elif self.trueCount == 1:
            return min(onebet, self.bankroll)      #20
        elif self.trueCount == 2:
            #return min(min_bet*scale, self.bankroll)  48
            return min(onebet+slope, self.bankroll)  #40
        elif self.trueCount == 3:
            #return min(min_bet*(scale*2), self.bankroll) 86
            return min(onebet+slope*2, self.bankroll)  #60
        elif self.trueCount == 4:
            #return min(min_bet*(scale*4), self.bankroll) 124
            return min(onebet+slope*3, self.bankroll)  #80
        elif self.trueCount == 5:
            #return min(min_bet*(scale*8), self.bankroll)     #500  162
            return min(onebet+slope*4, self.bankroll)  #100
        elif self.trueCount >= 6:
            #return min(min_bet*(scale*8), self.bankroll)     #500  200
            return min(onebet+slope*5, self.bankroll)  #120

    def optimal_hands(self):
        if self.trueCount <= -3:
            return 0
        elif self.trueCount < -1:
            return 1
        elif self.trueCount < 1:
            self.num_rounds_played +=1
            return 1
        elif self.trueCount >= 1:
            self.num_rounds_played +=1
            return 2
    def play_a_hand(self, num_hands, bet):
        self.bets = [bet for i in range(num_hands)]
        self.num_hands = num_hands
        self.deal_player_cards(num_hands)
        self.deal_dealer_cards()
        spot = 0
        while spot < len(self.player_cards):
            hand = self.player_cards[spot]
            print(f"dealer card: {self.dealer_cards[0]}")
            print(f"hand = {hand}")
            correct_move = self.choose_player_move(hand, spot)
            if correct_move == "B":
                print("Bust")
                move = "B"
            else:
                move = input("Enter Move (S,H,D,Ds,Y,N,Y/N,Hs(if A),Surr): ")
                while move != correct_move:
                    move = input("Incorrect move, try again: ")
            if move == "Ds":
                if len(hand) == 2:
                    move = "D"
                else:
                    move = "S"
            if move == "D" and len(hand) > 2:
                move = "H"
            if move == "S":
                self.scores += [sum(self.player_cards[spot])]
                spot += 1
                continue
            elif move in ["B","Surr"]:
                spot += 1
                self.scores += [move]
                continue
            elif move == "H":
                self.hit_player(spot)
                continue
            elif move == "D":
                self.hit_player(spot)
                self.bets[spot] = self.bets[spot]*2
                score = sum(self.player_cards[spot])
                print(score)
                if score >21:
                    score += -10
                self.scores += [score]
                spot +=  1
                continue
            elif move == "Hs":
                self.hit_player(spot)
                score = sum(self.player_cards[spot])
                self.scores += [score]
                spot +=  1
                continue
            elif move == "Y" or move == "Y/N":
                self.split_hands += [spot]
                self.split_player(spot)
                self.split_hands += [len(self.player_cards)-1]
                continue
            elif move == "N":
                self.player_cards[spot] = [sum(hand)]
                continue
            else:
                self.scores += ["Surr"]
                spot += 1
        self.play_dealer()
        starting_prof = self.profit
        self.payout()
        profit = self.profit - starting_prof
        return profit

    def play_for_hours(self, hands): #estimate 80 hands per hour
        count = 0
        while count <hands:
            count += 1
            num_hands = self.optimal_hands()
            bet = self.optimal_bet()
            self.run_hands(num_hands, bet)
            if Game.bankroll < 1:
                break
        return Game.profit
    
    def normal(self,x,mu,sigma):
        return (1/(sigma*math.sqrt(2*math.pi)))*(math.e**((-0.5)*(((x-mu)/sigma)**2)))
    def negative_probability(self, mu, sigma,):
        upperbound = -mu/sigma
        x = -6*(mu+sigma)
        integral = 0
        while x<0:
            integral += self.normal(x,mu,sigma)*0.01
            x+= 0.01
        return integral


    def play_one_hand(self, num_hands, bet):
        self.bets = [bet for i in range(num_hands)]
        self.num_hands = num_hands
        self.deal_all_cards(num_hands)
        spot = 0
        while spot < len(self.player_cards):
            print(f"Dealer: {self.dealer_cards[0]}")
            print()
            print(f"{self.player_cards}")
            print(f"hand: {spot+1}")




if "__main__" == __name__:
    start = time.time()
    Game = Game(6,True)
    indicator = 2

    if indicator == 0:
        X = []
        Y = []
        hands_per_hour = 100
        hours = 80
        iterations = hands_per_hour*hours
        ruined_count = 0
        n=1000
        for i in range(n):
            Y += [Game.play_for_hours(iterations)]
            if Y[-1] <= -Game.starting_bankroll:
                ruined_count+=1
            X += [i]
            Game.reset_day()
        #plt.plot(X,Y)
        average_profit = round(sum(Y)/len(Y),4)
        RoR = round(100*ruined_count/n,5)
        EsquaredV = 0
        for num in Y:
            EsquaredV += num**2
        EsquaredV = EsquaredV/len(Y)
        variance = EsquaredV - average_profit**2
        NZero = variance / average_profit**2
        print()
        print(f"hours: {hours}, bankroll: {Game.starting_bankroll}, min: {Game.minimum_bet}, max: {Game.maximum_bet}")
        print(f"expected value: {average_profit}, RoR: {RoR}%")
        print(f"variance: {round(variance,2)}, sd: {round(variance**(1/2),2)}, N-Zero: {round(NZero,2)}")
        print(f"probability of negative profit: {round(100*Game.negative_probability(average_profit,variance**(1/2)),4)}%")
        print(f"Mistakes: {Game.make_mistakes, Game.mistake_frequency}")
        print()
        #plt.show()



    if indicator == 1:
        goodhands = 100
        averages = []
        Rounds = []
        bust_count = 0
        averageeye = []
        for j in range(10000):
            X = []
            Profit = []
            i=0
            while Game.num_rounds_played<goodhands:
                X+= [i]
                i+=1
                Game.run_hands(Game.optimal_hands(),Game.optimal_bet())
                Profit += [Game.profit]
                if Game.bankroll < 1:
                    bust_count +=1
                    break
                
            averageeye += [X[-1]]
            averages += [round(sum(Profit)/(len(Profit)+1),0)]
            Game.profit = 0
            Game.total_wagered = 0
            Game.num_rounds_played = 0
            Game.reset_day()
        #print(averages)
        print()
        sits = round(sum(averageeye)/len(averageeye),2)
        print(f"{goodhands} rounds played on ", round(sum(averageeye)/len(averageeye),0), "sits at table")
        print(f"average average profit: {sum(averages)/len(averages)}")
        ev = (sum(averages)/len(averages))/ (sits)
        variance = (sum(num**2 for num in averages)/len(averages))/sits - (sum(averages)/len(averages))/ sits
        print(f"variance/ev^2 = N-zero: {round(variance/(ev**2),2)} hands, or {round((variance/(ev**2))/80,2)} hours at 80 hands per hour")
        print(f"${round(sum(averages)/len(averages) / (sum(averageeye)/len(averageeye)/60),2)} expected per hour with {Game.starting_bankroll} bankroll, {Game.minimum_bet} min, {Game.maximum_bet} max")
        print("Bust count: ", bust_count, "out of 10,000 --> ", 100*bust_count/10000, "% RoR")
        print()

    if indicator == 2:
        num_rounds = 10000000       #100 million - like 13450 seconds
        EVDict = {"total": [0,0,0,0,0,0]}
        for i in range(num_rounds):
            Game.profit = 0
            key = Game.trueCount
            Game.run_hands(1, 1)
            if key in EVDict.keys():
                EVDict[key][0] += Game.profit
                EVDict[key][1] += sum(Game.bets)+Game.insurance_bets
                EVDict[key][2] = round(EVDict[key][0]/EVDict[key][1],4)
            else:
                EVDict.update({key: [Game.profit, 1, Game.profit]})
            EVDict["total"][0]+= Game.profit
            EVDict["total"][1]+= sum(Game.bets)+Game.insurance_bets
            EVDict["total"][2] = round(EVDict["total"][0]/EVDict["total"][1],6)
            if Game.profit < 1:
                EVDict["total"][3] += 1
            EVDict["total"][4] += 1
            EVDict["total"][5] = round(EVDict["total"][3]/EVDict["total"][4],6)
        for key in range(-10,11):
            print(f"{key}: {EVDict[key]}", "   ",round(100*EVDict[key][2],4))
        print()
        print(EVDict["total"])
        print()
        #plt.plot([i for i in range(-10,11)], [round(100*EVDict[key][2],4) for key in range(-10,11)])
        #plt.show()

    print(round(time.time()-start,4), "seconds")




