#A tentative script that will run on the server side to handle the incoming and outgoing traffic of excel files
#along with keeping track of bid history

# keep copy of the lists in the franchise folder for every franchise

import pandas as pd
import random
import csv


code_read_path = "D:\\Resources\\IPL\\Common"
code_write_path = "D:\\Resources\\BidHistory"
code_team_path = "D:\\Controlled Experiment for IPL Auctions"
code_sold_write = "D:\\Resources"

master_df = None    #dataframe to store all the players from master.xlsx
# unsold_df = None    #data frame to store all the players from Unsold.xlsx
franchise = {}      #dictionary
values = {}         #dictionary
COUNT = 0           #global variable to store the count th time the franchises are submitting their lists
OFFSET = 17         #score given to a player not present in the list
LIMIT = 16
BUDGET = 5350  #budget for each franchise
INTERNATIONALS = 7  #limit of the number of international players in the squad
FRANCHISE_NAMES = ['KKR', 'DD', 'MI', 'RPS', 'GL', 'SRH', 'RCB', 'KXIP']    #the name of the franchises taking part in the auction
rounds = 10
sold_set = set()

class Franchise:
    def __init__(self, name, lst_players=[]):
        self.pl_lst = lst_players  # the total number of unsold players
        self.bought_lst = []  # The number of players bought by the franchise
        self.name = name  # just id of the franchises
        self.international_players = []  # Number of international players bought
        self.domestic_players = []  # number of domestic players bought
        self.budget_remaining = BUDGET
        # check_lst()
        # self.assign_values()

    def assign_values(self):
        for p_id in master_df["Id"]:
            if p_id in sold_set:
                continue
            if p_id not in values:
                values[p_id] = 0
            if p_id in self.pl_lst:
                values[p_id] += self.pl_lst.index(p_id) + 1  # creating the cumulative list
            else:
                values[p_id] += OFFSET  # adding the offset in case one player is not within the list

    def valid_list(self):
        problem = False
        multi_occ = set()

        for pid in self.pl_lst:
            # print(pid) #, end=',')
            try:
                player = get_player_info(pid)
            except Exception:
                print(f'{pid} is invalid\n')
                problem = True
                continue

            if player['BasePrice'] > self.budget_remaining:
                print(f"{self.name} cannot afford {player['PlayerName']}({pid})\n")
                problem = True

            if pid in sold_set:
                print(f"{player['PlayerName']} ({pid}) is already sold, wrong entry\n")
                problem = True

            if self.pl_lst.count(pid) > 1:
                multi_occ.add(pid)
                problem = True

        if len(multi_occ) > 0:
            print(f'These player ids occur more than once: {multi_occ}\n')

        return not problem

    def get_list(self):
        # check for validity of the player in a list sent by the franchises
        choice = input(f'Enter Y if {self.name} is ready: ')
        self.update_list()
        while not self.valid_list():
            # print(f'{self.name} has an invalid list.')
            self.update_list()


    def update_list(self):
        choice = input(f'\n\nEnter any key if {self.name} is ready: ')
        if choice.upper() == 'Y':
            filename = f'{code_team_path}\\{self.name}\\{self.name}.xlsx'  # reading each franchise one by one
            # print('\nfilename: ', filename, '\n')

            df = pd.read_excel(filename, header=None)
            bid_history = f'{code_write_path}\\{self.name}\\{COUNT}.xlsx'
            df.to_excel(bid_history)
            if len(df) == 0:
                df.to_excel(bid_history)
                self.pl_lst = []
            else:
                df = df.head(16 - len(self.bought_lst))
                df.to_excel(bid_history)
                d = df.to_dict()[0]
                self.pl_lst = list(d.values())

                print(f"{self.name} pl_list: ", self.pl_lst)
            # self.check_lst()


def init():
    global master_df
    global  COUNT, sold_set
    master_df = pd.read_excel(f"{code_read_path}\\master.xlsx")  # reading the files and creating the dataframes
    # unsold_df = master_df
    print(master_df)
    # print(master_df[master_df["Id"] == 34])

    for pid in master_df['Id']:     #picking up each id from the dataframe and storing it in the variable pid
        values[pid] = 0

    with open('sold.csv', 'w', encoding='utf-8') as fp:
        pass

    for f_name in FRANCHISE_NAMES:
        #print (f_name)
        filename = f'{code_team_path}\\{f_name}\\{f_name}.xlsx'  # reading each franchise one by one
        #print(filename)

        while True:
            df = pd.read_excel(filename, header=None)
            if len(df) > 0:
                bid_history = f'{code_write_path}\\{f_name}\\{COUNT}.xlsx'
                df.to_excel(bid_history)
                break
            print(f'{f_name}\'s list is empty')
            _ = input(f"\n\nEnter any key when {f_name} is ready.. ")
        # print (df)
        d = df.to_dict()[0]
        #print(d)
        franchise[f_name] = Franchise(f_name, list(d.values()))
        print(f'Reading {f_name}\n\n')
        while not franchise[f_name].valid_list():
            # print(f'{self.name} has an invalid list.')
            franchise[f_name].update_list()
        franchise[f_name].assign_values()

    print(f'In init(), values ({len(values)}): {values}')
    COUNT += 1

    ############# ROLLBACK ########################
    sold_set = {30, 34, 178, 25, 106, 150, 151, 51, 114, 19, 27, 44, 98, 97, 8, 173, 108, 127, 73, 186, 125, 142, 68, 33, 174, 1, 39, 57, 188, 75, 159, 24,
                85, 177, 71, 100, 104, 101, 83, 3, 91, 35, 95, 168, 79, 56, 194}

    franchise['KKR'].budget_remaining = 2210
    franchise['MI'].budget_remaining = 1280
    franchise['KXIP'].budget_remaining = 1090
    franchise['RCB'].budget_remaining = 645
    franchise['GL'].budget_remaining = 945
    franchise['RPS'].budget_remaining = 620
    franchise['DD'].budget_remaining = 720
    franchise['SRH'].budget_remaining = 895

    franchise['KKR'].bought_lst = [(114, 'Morris'), (27, 'Maxwell'), (44, 'Henriques'), (85, 'Parthiv'), (56, 'Dhawan')]
    franchise['MI'].bought_lst = [(8, 'Yuvraj'), (186, 'Watson'), (1, 'Uthappa'), (57, 'Cutting'), (75, 'Roy'), (177, 'Krunal'), (71, 'Zaheer'),
                                  (104, 'Yusuf')]
    franchise['KXIP'].bought_lst = [(106, 'Warner'), (39, 'Lynn'), (188, 'Malinga'), (108, 'Pant'), (142, 'Hardik')]
    franchise['RCB'].bought_lst = [(34, 'ABD'), (97, 'Stokes'), (33, 'Jadeja'), (24, 'Samson'), (101, 'Umesh'), (168, 'Shami'), (91, 'Dwyane Smith')]
    franchise['GL'].bought_lst = [(30, 'Kohli'), (173, 'Gayle'), (68, 'Bumrah'), (100, 'N Rana'), (159, 'Fizz')]
    franchise['RPS'].bought_lst = [(25, 'Rohit'), (150, 'Steve Smith'), (98, 'Dhoni'), (95, 'Nabi'), (194, 'Southee'), (73, 'Rahane')]
    franchise['DD'].bought_lst = [(151, 'Raina'), (51, 'McCullum'), (127, 'Pollard'), (3, 'Woakes'), (35, 'Narine'), (79, 'Y Chahal')]
    franchise['SRH'].bought_lst = [(178, 'Gambhir'), (19, 'Shakib'), (83, 'D Bravo'), (125, 'Bhuvi'), (174, 'Manish')]

    franchise['KKR'].international_players = [(114, 'Morris'), (27, 'Maxwell'), (44, 'Henriques')]
    franchise['MI'].international_players = [(186, 'Watson'), (57, 'Cutting'), (75, 'Roy')]
    franchise['KXIP'].international_players = [(106, 'Warner'), (39, 'Lynn'), (188, 'Malinga')]
    franchise['RCB'].international_players = [(34, 'ABD'), (97, 'Stokes'), (91, 'Dwyane Smith')]
    franchise['GL'].international_players = [(173, 'Gayle'), (159, 'Fizz')]
    franchise['RPS'].international_players = [(150, 'Steve Smith'), (95, 'Nabi'), (194, 'Southee')]
    franchise['DD'].international_players = [(51, 'McCullum'), (127, 'Pollard'), (3, 'Woakes'), (35, 'Narine')]
    franchise['SRH'].international_players = [(19, 'Shakib'), (83, 'D Bravo')]

    franchise['KKR'].domestic_players = [ (85, 'Parthiv'), (56, 'Dhawan')]
    franchise['MI'].domestic_players = [(8, 'Yuvraj'), (1, 'Uthappa'), (177, 'Krunal'), (71, 'Zaheer'), (104, 'Yusuf')]
    franchise['KXIP'].domestic_players = [(108, 'Pant'), (142, 'Hardik')]
    franchise['RCB'].domestic_players = [(33, 'Jadeja'), (24, 'Samson'), (101, 'Umesh'), (168, 'Shami')]
    franchise['GL'].domestic_players = [(30, 'Kohli'), (68, 'Bumrah'), (100, 'N Rana')]
    franchise['RPS'].domestic_players = [(98, 'Dhoni'), (25, 'Rohit'), (73, 'Rahane')]
    franchise['DD'].domestic_players = [(151, 'Raina'), (79, 'Y Chahal')]
    franchise['SRH'].domestic_players = [(178, 'Gambhir'), (125, 'Bhuvi'), (174, 'Manish')]
    ##################################################################

# To get details of any player from master list
def get_player_info(idx):
    d = master_df.loc[master_df['Id'] == idx].to_dict()
    new_d = {}
    idx = list(d['Id'].keys())[0]
    for key in d:
        new_d[key] = d[key][idx]
    return new_d


def auction(player, ineligible_teams):
    # global unsold_df
    while True:
        franchise_sold_to = input("Name of the franchise sold to? ").upper()
        if franchise_sold_to not in FRANCHISE_NAMES or franchise_sold_to in ineligible_teams:
            print(f'{franchise_sold_to} can\'t take part in the auction')
            continue

        selling_price = int(input('Winning bid (in lacs)? '))
        choice = input(f'Press Y to confirm selling price: {selling_price} (lacs): ').upper()
        if choice != 'Y':
            selling_price = int(input('Enter correct winning bid (in lacs)? '))

        if selling_price > franchise[franchise_sold_to].budget_remaining:
            print(f"{franchise_sold_to} can\'t afford {player['PlayerName']}")
            continue
        break

    print(f"The player {player['PlayerName']} is sold to {franchise_sold_to} for {selling_price}")
    franchise[franchise_sold_to].budget_remaining -= selling_price
    franchise[franchise_sold_to].bought_lst.append((player['Id'], player['PlayerName']))

    if player['Type'] == 'I':
        franchise[franchise_sold_to].international_players.append((player['Id'], player['PlayerName']))
    else:
        franchise[franchise_sold_to].domestic_players.append((player['Id'], player['PlayerName']))

    # u_df = unsold_df.drop(unsold_df.index[[player['Id']]])
    # unsold_df = u_df
    sold_set.add(player['Id'])

    print(f'International players ({len(franchise[franchise_sold_to].international_players)}): {franchise[franchise_sold_to].international_players}')
    print(f'Domestic players ({len(franchise[franchise_sold_to].domestic_players)}): {franchise[franchise_sold_to].domestic_players}')
    print(f'Budget remaining for {franchise_sold_to}: {franchise[franchise_sold_to].budget_remaining} lacs')
    print("_______________________________________________________________________________________\n")
    if len(franchise[franchise_sold_to].bought_lst) >= 16:
        print(f'{franchise_sold_to} has a full roster. Please switch off your terminal!')

    return franchise_sold_to, selling_price


def get_next_player():
    # store the next player
    global values
    if len(values) == 0:
        return

    best_players = set()
    min_val = min(values.items(), key=lambda x: x[1])[1]

    for pid, val in values.items():
        if val == min_val:
            best_players.add(pid)
    print(f'Values: {sorted(values.items(), key=lambda  x: x[-1])}')
    print(f'Min valued players: {best_players}')
    print('min valued player: ', min(values.items(), key=lambda x: x[-1]))
    best_player_id = random.choice(list(best_players))

    ix = master_df['Id'] == best_player_id
    master_df.loc[ix, 'Count'] += 1
    best_pl = get_player_info(best_player_id)

    with open(f'{code_read_path}\\auction.csv', 'a') as fp:
        csv_writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow([COUNT, best_player_id, best_pl['PlayerName']])

    print(f"{best_pl['PlayerName']} ({best_player_id}) base price: {best_pl['BasePrice']} lacs\n")

    ineligible_teams = set()

    if best_pl['Type'] == 'I':
        for name in FRANCHISE_NAMES:
            if len(franchise[name].international_players) > INTERNATIONALS:
                ineligible_teams.add(name)

    for name in FRANCHISE_NAMES:
        if BUDGET - best_pl['BasePrice'] <= 0:
            ineligible_teams.add(name)

        if len(franchise[name].bought_lst) >= 16:
            ineligible_teams.add(name)

    if len(ineligible_teams) != 0:
        print('Ineligible teams: ', ineligible_teams)
    # print(f'next player id: {best_player_id}')


    c = input("Is the player sold?[y/n]: ")

    if c.lower() == 'y':
        team, win_bid = auction(best_pl, ineligible_teams)

        try:
            fp = open(f'{code_sold_write}\\sold.csv', 'a', encoding='utf-8')

        except PermissionError:
            print("Please close both 'sold.csv' and 'master.xlsx' \n")
            choice = input('Enter Y if files are closed: ').upper()
            if choice == 'Y':
                fp = open(f'{code_sold_write}\\sold.csv', 'a', encoding='utf-8')

        finally:
            csv_writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow([best_pl['Id'], best_pl['PlayerName'], best_pl['Type'], team, win_bid])
            master_df.to_excel('.\\Common\\master.xlsx')
    else:
        pass
    values = {} # resetting the value dictionary after each round

#test clause
if __name__ == '__main__':
    COUNT = 48
    init()
    while True:
        end_choice = input('\nPress Y to continue the auction if the franchises have incomplete and/or unsatisfied squad: ').upper()
        if end_choice != 'N':
            print('\n\n\n')
            get_next_player()
            for f in franchise:
                franchise[f].get_list()
                franchise[f].assign_values()
            COUNT += 1
        else:
            print("Thank people for coming in, the end")
            break
