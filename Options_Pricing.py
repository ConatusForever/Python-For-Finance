from scipy.stats import norm
import math


# pricing the call option

def call(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    return round(S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2), 3)


# pricing the put option

def put(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    return round(K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1), 3)


# Implementation

if __name__ == "__main__":
    underlying_price = 100  # Current price of the underlying asset
    strike_price = 95       # Strike price of the option
    time_to_expiration = 0.25 # Time to expiration (in years)
    risk_free_rate = 0.05   # Risk-free interest rate
    volatility = 0.2       # Implied volatility of the underlying asset

    call_price = call(underlying_price, strike_price, time_to_expiration, risk_free_rate, volatility)
    put_price = put(underlying_price, strike_price, time_to_expiration, risk_free_rate, volatility)

    print("Call option price:", call_price)
    print("Put option price:", put_price)
