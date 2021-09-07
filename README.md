# VotingScore

VotingScore is a reputation score that represents the voting participation of an account based solely on its voting history data that is provided by boardroom's API.

There are many different methods to calculate reputation scores. Most of them are based on the contribution of user on other platforms and the whole ecosystem, but VotingScore model tries to calculate a score based on a user's voting activity in DAOs.

A python implementation of this method is provided as a proof of concept. But, this method can be easily implemented in other languages, or served as an standalone API or (in best case scenario) be integrated into Boardroom's API.

## How to calculate such score?

We consider these three factors in calculating the VotingScore:
1. **Count**: More votes means more score (obviously!).
2. **Time**: More recent voting participation should get more score.
3. **Diversity**: Voting for various protocols gets more score than just voting for one protocol.

We calculate the VotingScore of an address as sum of scores of each of its votes. This summation maps the count factor into the score value.

To map time factor into the score, we use a decreasing exponential decay function for calculating score of each vote.

And for diversity, we calculate a multiplier and multiply the final score by it, in order to give more value to diverse voters.

## Calculation details

To calculate score of each vote we apply decreasing exponential decay function to the difference between timestamp of vote and now. It has a starting value of 1 and its lower bound is 0. So, if you cast a vote right now you get the maximum score which is 1 and if you have voted years ago you get almost 0 score for that.

The reason to use exponential function here is the value of a vote cast yesterday is a lot more than value of a vote cast last month, but the value of a vote cast a year ago is just a little more than value of a vote cast 13 months ago.

This function has a shape like this:
![decreasing exponential decay](https://people.richland.edu/james/lecture/m116/logs/decay.gif)


---
To calculate the diversity multiplier we apply an increasing exponential function to the number of protocols an address have voted. For 1 protocol the multiplier is the minimum amount which is 1 and it increases exponentially with a upper bound of 2.

The reason to use exponential function here is the value of participating in 5 protocols is a lot more than value of participating in 1 protocol, but the value of participating in 105 protocols is just a little more than value of participating in 101 protocols.

This function has a shape like this:
![increasing exponential decay](https://people.richland.edu/james/lecture/m116/logs/decay2.gif)


More information about these exponential functions can be found [here](https://people.richland.edu/james/lecture/m116/logs/models.html).

A `MAX_SCORE_PER_PROTOCOL` constant has been set in code to limit the maximum score an address can get for each protocol. The reason is to prevent getting infinite score from just one protocol by participating in infinite number of fake proposals. This maximum is set to 100 which is equivalent score of voting each day for the past 8 months.

## Examples

In all of the following scenarios address `A` gets more score than address `B`:

- Address `A` has voted 5 times yesterday at timestamp `X` for protocol `aave`.
- Address `B` has voted 2 times yesterday at timestamp `X` for protocol `aave`.

---

- Address `A` has voted 3 times yesterday for protocol `aave`.
- Address `B` has voted 3 times last week for protocol `aave`.

---

- Address `A` has voted 2 times yesterday at timestamp `X`. 1 for protocol `aave` and 1 for protocol `balancer`.
- Address `B` has voted 2 times yesterday at timestamp `X` both for protocol `aave`.


## How to run

Install this requirement first:

```
pip install requests
```

Then run the code using this command and give address (or addresses) as command line arguments:

```
python voting_score.py 0x000...
```

There is a constant named `VERBOSE` in the code. Which can be set to `True` to print the diversity multiplier and score of each protocol separately.

## Notes

* This is a dynamic score and changes over time even for same inputs. Because it uses the current time in calculations.
* All the timestamps received from Boardroom's API are considered to be in UTC timezone.
* Maximum possible score an address can get is equal to `number of protocols available in Boardroom * MAX_SCORE_PER_PROTOCOL`. Which is currently equal to `62 * 100 = 6200`.

## Future works

* There is always room for improvements. This is the first thing that came to my mind when I tried to tackle this problem.
* Can be integrated into Boardroom's API or dashboard.
* A new score can be calculated for proposals by aggregating the VotingScore of its voters. This score can represents the legitimacy of a proposal. Same idea applies for a new score for protocols too. Currently, there are more than 37000 unique voters on Boardroom and this amount of requests for getting their voting data is not feasible for a standalone project. But, this can be achieved if we implement it as a feature in Boardroom's codebase.
