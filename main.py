import pandas as pd
import trueskill
import itertools
import math


def win_probability(team1, team2):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (trueskill.BETA * trueskill.BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)


def main():
    print(trueskill.Rating())
    r1 = trueskill.Rating()
    r2 = trueskill.Rating()
    p1 = trueskill.Rating()
    p2 = trueskill.Rating()
    t1 = [r1, r2]
    t2 = [p1, p2]
    print('{:.1%} chance to draw'.format(trueskill.quality([t1, t2])))
    (r1, r2), (p1, p2) = trueskill.rate([t1, t2], ranks=[0, 1])
    t1 = [r1, r2]
    t2 = [p1, p2]

    # players = pd.read_csv('players.csv')
    # uniques = []
    # df = pd.read_csv('games.csv')
    # for elem in df:
    #     uniques += list(df[elem].unique())
    # uniques = set(uniques)
    # print(df)
    # print(uniques.difference(set(list(players['Player'].unique()))))

    players = pd.read_csv('players.csv')
    games = pd.read_csv('games.csv')
    ratings = {}

    for player in players['Player'].unique():
        ratings[player] = trueskill.Rating()

    print(ratings)

    for i, row in games.iterrows():
        team_a = []
        team_b = []
        result = 2 # 2 is tie in the csv
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

        print('{:.1%} chance to draw'.format(trueskill.quality([rated_a,
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

    todays_players = ["rick", "mig", "leugim", "luisao", "bernardo",
                      "teds", "dig", "kenps", "miguel", "dias"]

    rated_a = []
    rated_b = []
    tie_chance = 0
    potential_a = []
    potential_b = []
    attempt = 0
    for team_a in list(itertools.combinations(todays_players, 5)):
        team_b = [x for x in todays_players if x not in team_a]
        rated_a = []
        rated_b = []

        for player in team_a:
            rated_a.append(ratings[player])
        for player in team_b:
            rated_b.append(ratings[player])

        quality = trueskill.quality([rated_a, rated_b])
        if quality > tie_chance:
            potential_a = team_a
            potential_b = team_b
            tie_chance = quality

        attempt += 1
        print("{}: {:.1%} chance to draw".format(attempt, tie_chance))

    print()
    print("FINISHED!")
    print("Team A")
    print(*potential_a)
    print("Team B")
    print(*potential_b)
    print("{:.1%} chance to draw".format(tie_chance))


if __name__ == '__main__':
    main()
