import pandas as pd
import yfinance as yfin
from utils.weights import weights
from pandas import DataFrame
from datetime import datetime, timedelta
from pandas_datareader import data as web

yfin.pdr_override()
start_date, end_date=(
    str(datetime.now()-timedelta(days=3*366))[:10],
    str(datetime.now())[:10]
)

def get_data():
    data=[]
    for k,v in weights.items():
        _data=web.DataReader(
            k,start=start_date,end=end_date
        ).reset_index()
        # _data=_data[['Date','Adj Close']]
        _data['Adj Close']=_data['Adj Close']*v # reweight based on percentage occupied within SPY
        _data['ticker']=k
        data.append(_data)
    data=pd.concat(data)
    return data
