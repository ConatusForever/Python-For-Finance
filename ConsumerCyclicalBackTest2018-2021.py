import pytz
from datetime import datetime, timedelta
import pandas as pd, numpy as np, vectorbt as vbt


# Builidng my variables
# Home Depot, Amazon, McDonald's, Tesla, Lowe's

symbols = [
            'HD',
            'AMZN',
            'MCD',
            'TSLA',
            'LOW'
        ]

start_date = datetime(2018, 1, 1, tzinfo=pytz.utc)
end_date = datetime(2021, 1, 1, tzinfo=pytz.utc)

traded_count = 3
window_len = timedelta(days=12 * 21)


window_count = 400
exit_types = ["SL", "TS", "TP"] # Stop Loss, Trailing Stop, Take Profit
stops = np.arange(0.01, 1 + 0.01, 0.01)


yfdata = vbt.YFData.download(symbols, start=start_date, end=end_date)
ohlcv = yfdata.concat()

split_ohlcv = {}

for k, v in ohlcv.items():
    split_df, split_indexes = v.vbt.range_split(
        range_len=window_len.days, n=window_count
    )
    split_ohlcv[k] = split_df
ohlcv = split_ohlcv


# Building the momentum strategy

momentum=ohlcv['Close'].pct_change().mean()

sorted_momentum = (
    momentum
    .groupby(
    'split_idx',
    group_keys=False,
    sort=False
    )
    .apply(
        pd.Series.sort_values
    )
.groupby('split_idx')
.head(traded_count)
)

selected_open= ohlcv['Open'][sorted_momentum.index]
selected_high= ohlcv['High'][sorted_momentum.index]
selected_low= ohlcv['Low'][sorted_momentum.index]
selected_close= ohlcv['Close'][sorted_momentum.index]



# Testing my order types

entries = pd.DataFrame.vbt.signals.empty_like(selected_close)
entries.iloc[0, :] = True

sl_exits = vbt.OHLCSTX.run(
    entries,
    selected_open,
    selected_high,
    selected_low,
    selected_close,
    sl_stop =list(stops),
    stop_type=None,
    stop_price=None
).exits

ts_exits = vbt.OHLCSTX.run(
    entries,
    selected_open,
    selected_high,
    selected_low,
    selected_close,
    sl_stop=list(stops),
    sl_trail=True,
    stop_type=None,
    stop_price=None
).exits

tp_exits = vbt.OHLCSTX.run(
    entries,
    selected_open,
    selected_high,
    selected_low,
    selected_close,
    tp_stop=list(stops),
    stop_type=None,
    stop_price=None
).exits


sl_exits.vbt.rename_levels({'ohlcstx_sl_stop': 'stop_value'}, inplace=True)
ts_exits.vbt.rename_levels({'ohlcstx_sl_stop': 'stop_value'}, inplace=True)
tp_exits.vbt.rename_levels({'ohlcstx_tp_stop': 'stop_value'}, inplace=True)
ts_exits.vbt.drop_levels('ohlcstx_sl_trail', inplace=True)

sl_exits.iloc[-1,:]=True
ts_exits.iloc[-1,:]=True
tp_exits.iloc[-1,:]=True

sl_exits =sl_exits.vbt.signals.first(reset_by=entries, allow_gaps=True)
ts_exits =ts_exits.vbt.signals.first(reset_by=entries, allow_gaps=True)
tp_exits =tp_exits.vbt.signals.first(reset_by=entries, allow_gaps=True)


exits = pd.DataFrame.vbt.concat(
    sl_exits,
    ts_exits,
    tp_exits,
    keys=pd.Index(exit_types, name='exit_type')
)

# Optimizing the strategy


portfolio = vbt.Portfolio.from_signals(selected_close, entries, exits)

total_return = portfolio.total_return()

total_return_by_type = total_return.unstack(level='exit_type')[exit_types]


#Viewing the distribution of returns

total_return_by_type[exit_types].vbt.histplot(
    xaxis_title='Total Return',
    xaxis_tickformat='%',
    yaxis_title='Count'

)

# Viewing the returns as a boxplot

total_return_by_type.vbt.boxplot(
    yaxis_title='Total return',
    yaxis_tickformat='%'
)

# Viewing the returns as a table

total_return_by_type.describe(percentiles=[])