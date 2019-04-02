import pandas as pd
import trueskill
import itertools
import math
import operator

DEBUG = 0


def debug(arg):
    if DEBUG == 1:
        print(arg)


def win_probability(team1, team2):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (trueskill.BETA * trueskill.BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)


def temp_unique():
    players = pd.read_csv('players.csv', encoding='latin-1')
    uniques = []
    df = pd.read_csv('games.csv')
    for elem in df:
        uniques += list(df[elem].unique())
    uniques = set(uniques)

    return len(uniques.difference(set(list(players['Player'].unique()))) -
               {0, 1, 2}) == 0


def calculate_ratings(ratings, player_list, games):

    for i, row in games.iterrows():
        team_a = []
        team_b = []
        result = 2  # 2 is tie in the csv
        for j, column in row.iteritems():
            if j.startswith("TeamA"):
                team_a.append(column)
            elif j.startswith("TeamB"):
                team_b.append(column)
            elif j == "Winner":
                result = column
            else:
                raise(Exception)

        rated_a = []
        rated_b = []

        for player in team_a:
            rated_a.append(ratings[player])
        for player in team_b:
            rated_b.append(ratings[player])

        debug('{:.1%} chance to draw'.format(trueskill.quality([rated_a,
                                                                rated_b])))

        if result == 0:
            rated_a, rated_b = trueskill.rate([rated_a, rated_b], ranks=[0, 1])
        elif result == 1:
            rated_a, rated_b = trueskill.rate([rated_a, rated_b], ranks=[1, 0])
        else:
            rated_a, rated_b = trueskill.rate([rated_a, rated_b], ranks=[0, 0])

        for player, rating in zip(team_a, rated_a):
            ratings[player] = rating

        for player, rating in zip(team_b, rated_b):
            ratings[player] = rating

    return ratings


def matchmake(ratings, players):
    rated_a = []
    rated_b = []
    ties = [0]
    matches_a = []
    matches_b = []
    attempt = 0
    for team_a in list(itertools.combinations(players, 5)):
        team_b = [x for x in players if x not in team_a]
        rated_a = []
        rated_b = []

        for player in team_a:
            rated_a.append(ratings[player])
        for player in team_b:
            rated_b.append(ratings[player])

        quality = trueskill.quality([rated_a, rated_b])
        if quality > ties[0]:
            matches_a.insert(0, team_a)
            matches_b.insert(0, team_b)
            ties.insert(0, quality)
            debug("{}: {:.1%} chance to draw".format(attempt, ties[0]))

        attempt += 1

    return matches_a, matches_b, ties


def print_matches(matches_a, matches_b, ties, top=1):
    for team_a, team_b, tie, cycle in zip(matches_a, matches_b, ties, range(top)):
        print('*' * 20)
        print("#{}".format(cycle + 1))
        print("Team A:")
        print(*team_a)
        print()
        print("Team B:")
        print(*team_b)
        print('_' * 20)
        print("{:.2%} chance to draw".format(tie))
        print('*' * 20)
        print()


def print_ratings(ratings, sorted=False):
    df = pd.DataFrame(columns=['Player', 'Mu', 'Sigma'])
    for player, rating in ratings.items():
        df.loc[len(df)] = [player, rating.mu, rating.sigma]

    if sorted:
        df = df.sort_values('Mu', ascending=0)

    print("{0: <20} | {1: <6} | {2: <6} |".format("Player", "Mu", "Sigma"))
    for index, row in df.iterrows():
        print("{0: <20} | {1: <6.3} | {2: <6.3} |".format(row['Player'],
                                                          row['Mu'], row['Sigma']))


def print_csv_ratings(ratings, sorted=False):
    df = pd.DataFrame(columns=['Player', 'Mu', 'Sigma'])
    for player, rating in ratings.items():
        df.loc[len(df)] = [player, rating.mu, rating.sigma]

    if sorted:
        df = df.sort_values('Mu', ascending=0)

    print("{0},{1},{2}".format("Player", "Mu", "Sigma"))
    for index, row in df.iterrows():
        print("{0},{1:.3},{2:.3}".format(row['Player'], row['Mu'], row['Sigma']))


def load_game_ratings():
    player_list = pd.read_csv('players.csv', encoding='latin-1')
    ratings = {}

    for player in player_list['Player'].unique():
        ratings[player] = trueskill.Rating()

    games = pd.read_csv('games_4vs4.csv', encoding='latin-1')
    ratings = calculate_ratings(ratings, player_list, games)
    games = pd.read_csv('games_5vs5.csv', encoding='latin-1')
    ratings = calculate_ratings(ratings, player_list, games)
    games = pd.read_csv('games_7vs7.csv', encoding='latin-1')
    ratings = calculate_ratings(ratings, player_list, games)
    return ratings


def get_team():
    players = ["teds","nram","rick","mig","bernardo","dias","mec","miguel","joao_martins","diegues"]
    ratings = load_game_ratings()
    matches_a, matches_b, ties = matchmake(ratings, players)
    print_matches(matches_a, matches_b, ties, top=4)


def get_ratings():
    ratings = load_game_ratings()
    print_ratings(ratings, sorted=True)
    # print_csv_ratings(ratings, sorted=True)


def main():
    get_team()
    get_ratings()


if __name__ == '__main__':
    main()
