# Fabio Valentini extract LQvv5xgy_ik

## Rules

### FAB-LQvv5xgy_ik-R1: Low-variance risk geometry for prop firms
- Rule: In a prop-firm environment, use high win rate (60-70%), moderate risk per trade, and reward-to-risk from 1:1 down to 0.75:1, max 1.5:1.
- Topic: risk
> "having high win rate, okay? Moderate risk per trade and going for moderate risk reward, one to one, even one to 0.75, maximum one to 1.5"
**Source GPS: LQvv5xgy_ik | BEGIN**

### FAB-LQvv5xgy_ik-R2: Low variance beats high variance across samples
- Rule: Low-variance geometry wins over many samples because it lowers the risk of ruin and max drawdown, even if the high-variance path has larger peak returns.
- Topic: risk
> "the best approach that you can have is the low variance risk geometry"
**Source GPS: LQvv5xgy_ik | BEGIN**

### FAB-LQvv5xgy_ik-R3: Withdraw prop profits to personal account
- Rule: Do not compound on the prop firm; withdraw as much as possible into a personal account to reduce counterparty risk.
- Topic: risk
> "The best option is to withdraw as much as you can and put in your personal account"
**Source GPS: LQvv5xgy_ik | MIDDLE**

### FAB-LQvv5xgy_ik-R4: Multiple brokerages
- Rule: Use multiple brokerages for personal accounts to isolate tail risk of one broker failing.
- Topic: risk
> "I don't use only one broker"
**Source GPS: LQvv5xgy_ik | END**

### FAB-LQvv5xgy_ik-R5: Conservative per-trade risk
- Rule: Conservative personal-account risk per trade is 0.5% to 1.25%; moderate accounts can add risk only when a month has produced exceptional profit.
- Topic: risk
> "if you want to be really conservative, it should be 1.25%, 0.5% per trade"
**Source GPS: LQvv5xgy_ik | END**

### FAB-LQvv5xgy_ik-R6: Competition three-phase structure
- Rule: In a multi-month competition, phase 1 tests regimes on separate accounts (trend, mean-revert, volatility breakout), phase 2 validates and scales on the winner, phase 3 is convexity exploitation with maximum aggression.
- Topic: session
> "One account that trend following strategy I tested. One account that has the mean reverting and one account I tested the volatility breakout"
**Source GPS: LQvv5xgy_ik | MIDDLE**

### FAB-LQvv5xgy_ik-R7: Late-stage aggression
- Rule: In a competition, deploy maximum aggression late; early uncontrolled aggression raises variance before the regime is known.
- Topic: session
> "you need to deploy maximum aggression on this"
**Source GPS: LQvv5xgy_ik | END**

### FAB-LQvv5xgy_ik-R8: Keep drawdown low in time-limited contests
- Rule: In a time-limited equity contest, keep drawdown as low as possible to preserve margin for later trades.
- Topic: risk
> "the goal is to keep the drawdown as low as possible because the time is limited"
**Source GPS: LQvv5xgy_ik | MIDDLE**

### FAB-LQvv5xgy_ik-R9: Block max daily and weekly risk
- Rule: The execution model must automatically block the maximum risk per day and the maximum risk per week.
- Topic: risk
> "an execution model that should be also automated in terms of blocking the maximum risk per day, the maximum risk per week"
**Source GPS: LQvv5xgy_ik | END**

## Unclear
- "Release margin" for scaling is not numerically defined.
- The 3-phase competition structure depends on the specific competition, not a universal rule.
- No specific volatility-breakout or mean-reversion thresholds given.
- Risk-of-ruin calculations are referenced but not shown.