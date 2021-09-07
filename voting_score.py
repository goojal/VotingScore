from datetime import datetime
import requests
import math
import sys


MAX_SCORE_PER_PROTOCOL = 100

TIMESTAMP_COEFFICIENT = 0.0000001
MIN_VOTE_SCORE = 0
MAX_VOTE_SCORE = 1

DIVERSITY_COEFFICIENT = 0.1
MIN_DIVERSITY_MULTIPLIER = 1
MAX_DIVERSITY_MULTIPLIER = 2

VERBOSE = True


def get_votes(address):
    url = f"https://api.boardroom.info/v1/voters/{address}/votes"
    votes = []
    try:
        response = requests.get(url)
        data = response.json()
        votes.extend(data["data"])
        while "nextCursor" in data:
            next_cursor = data["nextCursor"]
            next_url = url + f"?cursor={next_cursor}"
            response = requests.get(next_url)
            data = response.json()
            votes.extend(data["data"])
    except Exception as err:
        print(f"Error in getting votes of address: {address}")
        print(err)

    return votes


def decreasing_exponential_decay(C, k, t, b):
    return C * math.exp(-k * t) + b


def increasing_exponential_decay(C, k, t, b):
    return C * (1 - math.exp(-k * t)) + b


def time_weighted_score(now_timestamp, vote_timestamp):
    timestamp_diff = now_timestamp - vote_timestamp
    if timestamp_diff < 0:
        return 0 # we don't support time travellers who have voted in the future!

    vote_score = decreasing_exponential_decay(MAX_VOTE_SCORE, TIMESTAMP_COEFFICIENT, timestamp_diff, MIN_VOTE_SCORE)
    return vote_score


def protocol_score(now_timestamp, votes_timestamps):
    total_score = 0
    for vote_timestamp in votes_timestamps:
        vote_score = time_weighted_score(now_timestamp, vote_timestamp)
        total_score += vote_score

    return min(total_score, MAX_SCORE_PER_PROTOCOL)


def diversity_multiplier(protocols_count):
    if protocols_count < 1:
        return 0

    multiplier = increasing_exponential_decay(
        MAX_DIVERSITY_MULTIPLIER - MIN_DIVERSITY_MULTIPLIER,
        DIVERSITY_COEFFICIENT,
        protocols_count - 1, # the reason of -1 is to get the exact MIN_DIVERSITY_MULTIPLIER for 1 protocol
        MIN_DIVERSITY_MULTIPLIER
        )
    return multiplier


def voting_score(address):
    raw_votes = get_votes(address)

    votes = {} # contains votes timestamps of each protocol seperately
    for raw_vote in raw_votes:
        protocol = raw_vote["protocol"]
        timestamp = raw_vote["timestamp"]
        if protocol not in votes:
            votes[protocol] = []
        votes[protocol].append(timestamp)

    total_vote_scores = 0
    now_timestamp = datetime.utcnow().timestamp() # use same now_timestamp for all votes for sake of consistency
    for protocol in votes:
        score = protocol_score(now_timestamp, votes[protocol])
        if VERBOSE: print("{}: {}".format(protocol, score))
        total_vote_scores += score

    multiplier = diversity_multiplier(len(votes))
    if VERBOSE: print("Diversity Multiplier: {}".format(multiplier))
    final_score = total_vote_scores * multiplier
    return final_score


if __name__ == "__main__":
   addresses = sys.argv[1:]

   if len(addresses) < 1:
       print("input address as an argument")

   for address in addresses:
       print("Address: {}".format(address))
       score = voting_score(address)
       print("Voting Score: {}\n".format(round(score, 2)))
