import datetime
from dateutil import relativedelta
import pandas as pd
import re
from urllib.request import urlopen, Request, URLError
import calendar
import datetime
from urllib.error import HTTPError
import time
import io
import numpy as np
import requests
import json

class download_stock():
    
    crumble_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
    crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
    cookie_regex = r'set-cookie: (.*?); '
    quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events={}&crumb={}'
    
    def get_crumble_and_cookie(self, symbol):
        try:
            link = self.crumble_link.format(symbol)
            
            response = urlopen(link)
            match = re.search(self.cookie_regex, str(response.info()))
            cookie_str = match.group(1)
            text = response.read().decode("utf-8")
            match = re.search(self.crumble_regex, text)
            if match is not None:
                crumble_str = match.group(1)
                return crumble_str , cookie_str
            else:
                return False, False
        except HTTPError:
            return False, False
        except URLError:
            return False, False
    
    def download_quote(self, symbol, date_from, date_to,events):
        time_stamp_from = calendar.timegm(datetime.datetime.strptime(date_from, "%Y-%m-%d").timetuple())
        next_day = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
        time_stamp_to = calendar.timegm(next_day.timetuple())
    
        attempts = 0
        while attempts < 5:
            crumble_str, cookie_str = self.get_crumble_and_cookie(symbol)
            
            if not isinstance(crumble_str, bool):
                link = self.quote_link.format(symbol, time_stamp_from, time_stamp_to, events,crumble_str)
                #print link
                r = Request(link, headers={'Cookie': cookie_str})
                try:
                    response = urlopen(r)
                    text = response.read()
                    frame = pd.read_csv(io.StringIO(text.decode('utf-8')))
                    return frame
                except URLError:
                    time.sleep(0.500)
                    
            attempts += 1
        return pd.DataFrame()
    
    def save(self, symbol, date_from, date_to, keep_earnings):
        url = 'https://www.optionslam.com/tv/marks?symbol=' + symbol + '&from=1409736600&to=2114398800&resolution=D'
    
    
        dates = []
        after_close = False
        
        if not keep_earnings:
            json_l = json.loads(requests.get(url).text)
            dates = json_l['time']
            
            for d in range(len(dates)):
                dates[d] = datetime.datetime.utcfromtimestamp(dates[d]).strftime('%Y-%m-%d')
            
            market = json_l['text']
        
            count_after_close = 0
            count_before_open = 0
            for m in market:
                if 'After Market Close' in m:
                    count_after_close = count_after_close + 1
                elif 'Before Market Open' in m:
                    count_before_open = count_before_open + 1
            
            
            if count_after_close > count_before_open:
                after_close = True
            
            

        frame = self.download_quote(symbol, date_from, date_to, 'history')
        
        returns = []
        for f in range(len(frame.index.values)-1):
            if after_close and frame.loc[f+1, 'Date'] not in dates:
                first_close_price = frame.loc[f, 'Close']
                second_close_price = frame.loc[f+1, 'Close']
                
                val = (second_close_price/first_close_price)-1
                if not np.isnan(val):
                    returns.append(val)
            elif f-1 < 0 or (not after_close and frame.loc[f-1, 'Date'] not in dates):
                first_close_price = frame.loc[f, 'Close']
                second_close_price = frame.loc[f+1, 'Close']
                
                val = (second_close_price/first_close_price)-1
                if not np.isnan(val):
                    returns.append(val)
        
        if len(returns) != 0:
            returns.insert(0, 'NA')
        
        df = pd.DataFrame(data=returns, columns={'Returns'})
        return df

def get_historical(num, tick):
    num_months = num
    
    #Location to save in
    save_location = '/Users/vishalchopra/Desktop/Predictions/' + tick + '.csv'
    
    today = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
    past = datetime.datetime.strftime(datetime.datetime.today()-relativedelta.relativedelta(months=num_months), '%Y-%m-%d')
    
    download = download_stock()
    
    #ticker, date_from, date_to, whether it should keep earnings dates (False = remove earnings)
    df = download.save(tick, past, today, False)
    
    #location to save in
    df.to_csv(save_location)

get_historical(12, 'S')