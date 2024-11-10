import random
import time
import os

# For this program to work correctly, you need to make sure the path is correctly set to the location of the python file
path = "/Users/carat/Downloads/PYTHON/2024 Software MAC/HTW/"

class Entity:
    def __init__(self, position):
        self.position = position # Sets the position to the value provided

class Player(Entity):
    def __init__(self, start_pos):
        super().__init__(start_pos)
        self.arrows = 5 # Sets the starting number of arrows a player has 

class Wumpus(Entity):
    def __init__(self, game_map, player_start_pos):
        wumpus_pos = random.choice([room for room in range(1, 21) if room != player_start_pos]) # Chooses a random room from 1-20 to place the Wumpus
        super().__init__(wumpus_pos)
        self.game_map = game_map # Stores the game map for the object to use

    def wake_up(self):
        print("The Wumpus has woken!")
        chance = random.randint(1, 2) # Simulates a 50/50 chance
        if chance == 1:
            possible_moves = self.game_map.rooms[self.position] # Finds all the connected rooms that the Wumpus can potentially move into
            self.position = random.choice(possible_moves) # Randomly selects one room to move to 
            print("The Wumpus has moved. Phew!")
        if chance == 2:
            print("The Wumpus is surrounded by hazards and stays put.")
        time.sleep(4)

class Hazard(Entity):
    def __init__(self, positions):
        super().__init__(positions)

    def encounter_message(self):
        pass # Passes the code without disruption: https://www.w3schools.com/python/ref_keyword_pass.asp#:~:text=Definition%20and%20Usage,definitions%2C%20or%20in%20if%20statements

class Pits(Hazard):
    def __init__(self, game_map, player_start_pos, wumpus_pos):
        hazard_positions = [player_start_pos, wumpus_pos]
        available_rooms = [room for room in range(1, 21) if room not in hazard_positions] # Used ChatGPT to design this variable
        pits_pos = []
        while len(pits_pos) < 2:
            pos = random.choice(available_rooms) # Generates 2 random room numbers
            if pos not in pits_pos:
                pits_pos.append(pos) # Appends room numbers to list
        super().__init__(pits_pos)

    def encounter_message(self):
        return "You fell into a pit! Game over."

class Bats(Hazard):
    def __init__(self, game_map, player_start_pos, wumpus_pos, pits):
        hazard_positions = [player_start_pos, wumpus_pos] + pits.position # Defining all unavailable rooms
        available_rooms = [room for room in range(1, 21) if room not in hazard_positions] # Finding remaining avaliable rooms with no hazards
        bats_pos = []
        while len(bats_pos) < 2: # Checks how rooms have bats in them 
            pos = random.choice(available_rooms)
            if pos not in bats_pos:
                bats_pos.append(pos)
        super().__init__(bats_pos)

    def encounter_message(self):
        return "Bats carried you to a random room!"

class Skinwalker(Hazard):
    def __init__(self, game_map, player_start_pos, wumpus_pos, pits, bats):
        hazard_positions = [player_start_pos, wumpus_pos] + pits.position + bats.position
        available_rooms = [room for room in range(1, 21) if room not in hazard_positions] # Finding remaining avaliable rooms with no hazards
        skinwalker_pos = []
        while len(skinwalker_pos) < 1:
            position = random.choice(available_rooms)
            if position not in skinwalker_pos:
                skinwalker_pos.append(position)
        super().__init__(skinwalker_pos)

    def encounter_message(self):
        return "You encountered a Skinwalker! No more warnings will be given."

class Chest(Hazard):
    def __init__(self, game_map, player_start_pos, wumpus_pos, pits, bats, skinwalkers):
        hazard_positions = [player_start_pos, wumpus_pos] + pits.position + bats.position + skinwalkers.position
        available_rooms = [room for room in range(1, 21) if room not in hazard_positions]
        chest_pos = []
        while len(chest_pos) < 1: # Generates only 1 room number
            position = random.choice(available_rooms)
            if position not in chest_pos:
                    chest_pos.append(position)
        super().__init__(chest_pos)

    def encounter_message(self):
        return "You found a legendary chest! You are given 5 extra arrows!"
    
class Game:
    def __init__(self):
        self.rooms = {
            1: [2, 5, 8], 2: [1, 3, 10], 3: [2, 4, 12], 4: [3, 5, 14],
            5: [1, 4, 6], 6: [5, 7, 15], 7: [6, 8, 17], 8: [1, 7, 9],
            9: [8, 10, 18], 10: [2, 9, 11], 11: [10, 12, 19], 12: [3, 11, 13],
            13: [12, 14, 20], 14: [4, 13, 15], 15: [6, 14, 16], 16: [15, 17, 20],
            17: [7, 16, 18], 18: [9, 17, 19], 19: [11, 18, 20], 20: [13, 16, 19]
        }
        self.__start_room = random.randint(1, 20) # Selects a random room from 1-20, each room has 3 other connecting rooms
        self.__player = Player(self.__start_room)
        self.__wumpus = Wumpus(self, self.__player.position)
        self.__pits = Pits(self, self.__player.position, self.__wumpus.position)
        self.__bats = Bats(self, self.__player.position, self.__wumpus.position, self.__pits)
        self.__skinwalkers = Skinwalker(self, self.__player.position, self.__wumpus.position, self.__pits, self.__bats)
        self.__chest = Chest(self, self.__player.position, self.__wumpus.position, self.__pits, self.__bats, self.__skinwalkers)
        self.__encountered_skinwalker = False # Tracks if the player has encountered a skinwalker
        self.__foundchest = False  # Tracks if the player has found the chest
        self.__gameover = False # Tracks when the player has reached an ending

    @property
    def encountered_skinwalker(self):
        return self.__encountered_skinwalker
    
    @property
    def found_chest(self):
        return self.__foundchest
    
    def connected(self, current_room, target_room):
        return target_room in self.rooms[current_room] # Checks if one room is linked to another; this method is used for player movement 

    def find_path(self, start_room, distance): # Used ChatGPT for some assistance; this method is used for shooting arrow 
        path = [start_room] # Creating a list for arrow path
        current_room = start_room
        for step in range(distance): # Identifying the number of rooms needed (arrow distance)
            next_rooms = [room for room in self.rooms[current_room] if room not in path] # Includes all the rooms directly connected to the current room
            if next_rooms: 
                current_room = random.choice(next_rooms) 
                path.append(current_room) # Randomly chooses 1 of the connecting rooms and appends to the path
            else: 
                break # Code breaks if there are no further rooms
        return path
    
    def show_instructions(self):
        print("""
WELCOME TO 'Hunt The Wumpus' -
            
    The Wumpus resides in a cave with 20 rooms, each connected by three tunnels to other rooms. Beware of the Wumpus for he will eat you if you are found. 
    Your only chance to escape and win is to hunt down the Wumpus! 
    It's a challenging mission since the cave is under his control, but for the sake of the townspeople he terrorises, you must survive and bring back good news. Good luck!
            
\n! PLAYERS !
    Each turn you may move or shoot a crooked arrow ↓
    Moving: You can go one room (thru one tunnel) each turn
    Arrows: You have 5 arrows. You automatically lose when you run out.
        Chest - 1 room has a rare chest.
        IF YOU GO THERE: You will be given 5 extra arrows!
    Each arrow can go from 1 to 5 rooms: you aim by telling the computer the rooms you want the arrow to go to. 
        If the arrow hits the wumpus: you win.
        If the arrow hits nothing: you lose your arrow.
            
\n! HAZARDS !
    Wumpus - The wumpus is not bothered by the hazards as he has sucker feet, ultra awareness and is too big for a bat to lift. Usually he is asleep. 
        2 THINGS THAT WAKE HIM UP: You enter his room or shooting an arrow.
    If the wumpus wakes, he moves one room or stays still. IF the Wumpus moves to where you are, he will eat you up (& you lose!)
        Bottomless Pits - 2 rooms have bottomless pits in them.
            IF YOU GO THERE: You fall into the pit unable to return.
        Super bats - 2 rooms have super bats. 
            IF YOU GO THERE: A bat grabs you and takes you to another room at random. 
        Skinwalkers - 1 room has a skinwalker. 
            IF YOU GO THERE: Your senses will be taken away and you will no longer receive hazard warnings. 
            
\n! WARNINGS !
    When you are one room away from the hazards, you will be given warnings:
        Wumpus - “I smell a wumpus!”
        Bats - “Bats nearby!”
        Pits - “I feel a draft!”
        Skinwalkers - “A witch is crawling around…”
        Chest - “You sense something valuable nearby…”
        """)
        input("Enter to return: ")
        os.system("cls")
        
    def save_game(self, file=path+'SaveGame.txt'):
        try:
            with open(file, "w") as f:
                f.write(f"{self.__player.position}\n")
                f.write(f"{self.__wumpus.position}\n")
                f.write(f"{self.__pits.position[0]} {self.__pits.position[1]}\n")
                f.write(f"{self.__bats.position[0]} {self.__bats.position[1]}\n")
                f.write(f"{self.__skinwalkers.position[0]}\n")
                f.write(f"{self.__player.arrows}\n")
                f.write(f"{self.encountered_skinwalker}\n")
                f.write(f"{self.found_chest}\n")  # Saving game entity positions
            print("Game saved.")
            time.sleep(1)
            os.system("cls")
        except:
            print("Failure to save.")
            time.sleep(1)
            os.system("cls")

    def load_game(self, file=path+'SaveGame.txt'):
        try:
            with open(file, "r") as f:
                self.__player.position = int(f.readline().strip()) # Reads the line from the file: https://www.w3schools.com/python/ref_file_readline.asp
                self.__wumpus.position = int(f.readline().strip()) 
                self.__pits.position = [int(x) for x in f.readline().strip().split()]
                self.__bats.position = [int(x) for x in f.readline().strip().split()]
                self.__skinwalkers.position = [int(x) for x in f.readline().strip().split()]
                self.__player.arrows = int(f.readline().strip())
                self.__encountered_skinwalker = f.readline().strip() == 'True' # Compares the stripped line to the string 'True'; returns a boolean
                self.__foundchest = f.readline().strip() == 'True'
            print("Game loading...")
            time.sleep(1)
            os.system("cls")
            return True
        except ValueError:
            print("No loaded games.")
            time.sleep(1)
            os.system("cls")
            return False
        
    def loading(self):
        game = Game()
        if game.load_game():
            game.play()
            if game.__gameover:
                with open(path + 'SaveGame.txt', "w") as file:
                    pass  # Opening file in writing mode to cls the file: https://www.geeksforgeeks.org/difference-between-modes-a-a-w-w-and-r-in-built-in-open-function/

    def move_player(self, room):
        if self.connected(self.__player.position, room):
            self.__player.position = room # Updating player position
            self.check_hazards() # Showing the player the correct hazard warnings for the room
        else:
            print("You can't move to that room from here.")
            time.sleep(2)
            os.system("cls")
            return False

    def shoot_arrow(self, start_room, distance):
        if start_room not in self.rooms[self.__player.position]:
            print("You can only shoot from one of the room tunnels.")
            time.sleep(3)
            return [] # Ensures that the arrow path is empty 
        if distance < 1 or distance > 5: # Making sure arrow distance is between 1 & 5 before proceeding
            print("Distance must be between 1 and 5 rooms.")
            time.sleep(3)
            return False
        else: 
            self.__player.arrows -= 1
        path = self.find_path(start_room, distance)
        if path:
            if self.__wumpus.position in path: # If the arrow is in the same room as the Wumpus, you win
                print("You have slain the Wumpus! You win!")
                time.sleep(2)
                self.__gameover = True
                return True
            else: 
                print("Missed!") # Else, you miss
                time.sleep(2)
        if self.__player.arrows == 0: # If player runs out of arrows, game over
            print("You have run out of arrows. Game over.")
            time.sleep(3)
            os.system("cls")
            self.__gameover = True
            return True
        self.__wumpus.wake_up() # Wumpus wakes up when arrow is shot
        return False

    def en_wumpus(self):
        self.__wumpus.wake_up() # The first time player encounters Wumpus, it'll be a 50/50 chance of game over
        if self.__player.position == self.__wumpus.position:
            print("You have been eaten. Game over.") # If Wumpus does not move while player is in the same room, game over
            time.sleep(2)
            self.__gameover = True

    def en_pits(self):
        if self.__player.position in self.__pits.position:
            print(self.__pits.encounter_message()) # Calls enounter message from class
            time.sleep(2)
            self.__gameover = True

    def en_bats(self):
        if self.__player.position in self.__bats.position:
            print(self.__bats.encounter_message())
            time.sleep(2)
            new_pos = random.choice([room for room in range(1, 21) if room not in self.__bats.position])  # Bats carries player to a new room
            self.__player.position = new_pos
            self.check_hazards()  # Check hazards in the new room

    def en_skin(self):
        if self.__player.position in self.__skinwalkers.position:
            if self.__encountered_skinwalker == False:
                print(self.__skinwalkers.encounter_message())
                time.sleep(2)
            self.__encountered_skinwalker = True

    def en_chest(self):
        if self.__player.position in self.__chest.position:
            print(self.__chest.encounter_message())
            time.sleep(2)
            self.__foundchest = True
            self.__player.arrows += 5  # Player is given 5 extra arrows
        
    def check_hazards(self):
        if self.__player.position == self.__wumpus.position:
            return self.en_wumpus()
        elif self.__player.position in self.__pits.position:
            return self.en_pits()
        elif self.__player.position in self.__bats.position:
            return self.en_bats()
        elif self.__player.position in self.__skinwalkers.position:
            return self.en_skin()
        elif self.__player.position in self.__chest.position and not self.__foundchest:
            return self.en_chest()

    def print_status(self):
        print("--- Save & Exit (Q) ---\n"
              f"\nYou are in room {self.__player.position}.\n"
              f"Tunnels lead to {self.rooms[self.__player.position]}.\n"
              f"You have {self.__player.arrows} arrows left.")

        if self.__encountered_skinwalker == False:  # Only give warnings if skinwalker hasn't been encountered
            adjacent_rooms = self.rooms[self.__player.position] # Identifies rooms that are connected to the room player is currently in
            for room in adjacent_rooms: # If connected rooms contain hazards, the program will display a warning to the player accordingly
                if room == self.__wumpus.position:
                    print("I smell a Wumpus nearby...")
                if room in self.__bats.position:
                    print("Bats nearby!")
                if room in self.__pits.position:
                    print("I feel a draft!")
                if room in self.__skinwalkers.position:
                    print("A witch is crawling around...")
                if room in self.__chest.position and not self.__foundchest:
                    print("You sense something valuable nearby...")
   
    def play(self):
        while not self.__gameover:
            self.print_status()
            command = input("\nMove or Shoot? (M/S): ").lower()
            if command == "m":
                try:
                    room = int(input("Enter room number to move to: "))
                    if self.move_player(room):
                        os.system("cls")
                        break
                except ValueError:
                    print("Invalid room number. Please enter valid room number.")
                    time.sleep(3)
                os.system("cls")
            elif command == "s":
                try:
                    start_room = int(input("Enter room number to shoot from: "))
                    distance = int(input("How many rooms do you wanna shoot through? (1-5): "))
                    if self.shoot_arrow(start_room, distance):
                        os.system("cls")
                        break
                except ValueError:
                    print("Invalid input. Make sure room number and distance are correct.")
                    time.sleep(3)
                os.system("cls")
            elif command == "q":
                progress = input("Save & Quit? (Y/N): ").lower()
                if progress == "y":
                    self.save_game()
                    break
                else:
                    print("Saving cancelled.")
                    time.sleep(1)
                    os.system("cls")
                    pass
            else:
                print("Invalid command. Please enter 'm' to move, 's' to shoot, or 'q' to exit.\n")
                time.sleep(4)
                os.system("cls")

def main_menu():
    while True:
        game = Game()
        print("--- HUNT THE WUMPUS ---\n"
              "1. Instructions\n"
              "2. Play New Game\n"
              "3. Resume Saved Game\n"
              "4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            os.system("cls")
            game.show_instructions()
        elif choice == "2":
            os.system("cls")
            game.play()
        elif choice == "3":
            os.system("cls")
            game.loading()
        elif choice == "4":
            print("See you next time!")
            break
        else:
            print("Invalid Choice - Choose again.")
            time.sleep(1)
            os.system("cls")

main_menu()