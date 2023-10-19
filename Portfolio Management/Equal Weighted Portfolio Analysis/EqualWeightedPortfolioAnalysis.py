#import libraries

import quantstats as qs, pandas as pd, numpy as np, yfinance as yf, matplotlib.pyplot as plt

# Portfolio Assets: J.P. Morgan, Nvdia, Eli Lilly, Walmart, Microsoft

assets = ['JPM', 'NVDA', 'LLY', 'WMT', 'MSFT']
n_assets = len(assets)

# Downloading historical adjusted close prices for each company

assetPrices = yf.download(
        assets,
        start='2023-01-01',
        end='2023-10-17'
        )['Adj Close'].reset_index()


# simple returns

assetReturns = (
    assetPrices
    .set_index('Date')
    .pct_change()
    .dropna()
    
)

# log returns
assetLogReturns = np.log(assetPrices.set_index('Date')/assetPrices.set_index('Date').shift(1)).dropna()

# cumulative returns
cumulativeLogReturns = assetLogReturns.cumsum()


# Generating the weights for each asset in our portfolio
portfolioWeights = n_assets*[1/n_assets]

# Display price action and returns

# Price Action by Date
fig, ax = plt.subplots(figsize=(12, 8))
for asset in assets:
    ax.plot(assetPrices['Date'], assetPrices[asset], label=asset)
ax.legend()
plt.ylabel('Adj Close Prices ($)')
plt.xlabel('Date')
plt.title('1/N Portfolio Companies Prices', fontsize =20,pad=20)
plt.show()


# Log Returns by Date
fig, ax = plt.subplots(figsize=(12, 8))
for asset in assets:
    ax.plot(cumulativeLogReturns.reset_index()['Date'], cumulativeLogReturns.reset_index()[asset], label=asset)
ax.legend()
plt.ylabel('Cumulative Log Returns')
plt.xlabel('Date')
plt.title('Cumulative Log Returns for our Portfolio Companies', fontsize =20,pad=20)
plt.show()

# get returns for our portfolio

portfolioReturns = pd.Series(
    np.dot(portfolioWeights, assetReturns.T),
    index= assetReturns.index
)

# View our Cumulative Returns, Daily Returns & Drawdowns

qs.plots.snapshot(portfolioReturns,
                  title='1/N Equal Weighted Portfolio Performance',
                  grayscale=True)

#Generate Metrics to Evaluate the performance of our portfolio vs the S&P 500

qs.reports.metrics(
    portfolioReturns,
    benchmark='SPY',
    mode='basic',
    prepare_returns=False
)

# get portfolio performance tearsheet

qs.reports.html(
    portfolioReturns,
    benchmark='SPY',
    title='1/N Portfolio - Hakeem Lawrence',
    download_filename='1/N Portfolio Eval.html'
)