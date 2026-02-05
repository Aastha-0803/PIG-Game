import random

class PigGame:
    def __init__(self, players, target=100):
        self.players=players
        self.target=target
        self.scores=[0]*len(players)
        self.current_player_index=0
        self.game_over=False
        self.winner=None
        # self.last_dice=None

    def roll_dice(self):
        min_value=1
        max_value=6
        dice=random.randint(min_value, max_value)

        return dice
    
    def roll(self):
        if self.game_over:
            return self.get_state()

        dice = self.roll_dice()
        # self.last_dice = dice
        idx = self.current_player_index

        if dice == 1:
            self.scores[idx] = 0
            self.current_player_index = (idx + 1) % len(self.players)
        else:
            self.scores[idx] += dice
            if self.scores[idx] >= self.target:
                self.game_over = True
                self.winner = self.players[idx]

        return self.get_state()
    

    def hold(self):
        idx=self.current_player_index
        if self.game_over:
            return self.get_state()
        
        self.current_player_index = (idx + 1) % len(self.players)

        return self.get_state()
    
    def get_state(self):
        return{
            "players":[
                {"name":name, "score":score}
                for name, score in zip(self.players, self.scores)
            ],
            "current_player":self.players[self.current_player_index],
            "game_over": self.game_over,
            "winner":self.winner,
            # "last_dice":self.last_dice
        }
 
