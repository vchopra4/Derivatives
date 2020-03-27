import pandas as pd
import numpy as np
import scipy.stats as st

tick1 = 'AAPL'
tick2 = 'SNA'
frame1 = pd.read_csv('/Users/andrewpecjak/Desktop/MCAP/' + tick1 + '.csv')
frame2 = pd.read_csv('/Users/andrewpecjak/Desktop/MCAP/' + tick2 + '.csv')
total1 = 0
total2 = 0
count1 = 0
count2 = 0
avg1 = 0
avg2 = 0
sd1num = 0
sd2num = 0
sd1 = 0
sd2 = 0
cov = 0
corr = 0
covnum = 0
sdcount = 0
curtotal1 = 0
curtotal2 = 0
curcount1 = 0
curcount2 = 0
curavg1 = 0
curavg2 = 0
cursd1num = 0
cursd2num = 0
cursd1 = 0
cursd2 = 0
curcov = 0
curcorr = 0
cursdcount = 0
curcovnum = 0

for i in range(0, len(frame1.index.values)):
    price1 = frame1.loc[i, ['Close']].values
    if price1 > 0 and i<=(len(frame1.index.values)-90):
        total1 = total1 + price1
        count1 = count1 + 1
    if price1 > 0 and i>(len(frame1.index.values)-90):
        curtotal1 = curtotal1 + price1
        curcount1 = curcount1 + 1

for i in range(0, len(frame2.index.values)):
    price2 = frame2.loc[i, ['Close']].values
    if price2 > 0 and i<=(len(frame2.index.values)-90):
        total2 = total2 + price2
        count2 = count2 + 1
    if price2 > 0 and i>(len(frame2.index.values)-90):
        curtotal2 = curtotal2 + price2
        curcount2 = curcount2 + 1

avg1 = total1/count1
avg2 = total2/count2


curavg1 = curtotal1/curcount1
curavg2 = curtotal2/curcount2


if len(frame1.index.values) > len(frame2.index.values):
    length = len(frame2.index.values)
else:
    length = len(frame1.index.values)


for i in range(0, length):
    price1 = frame1.loc[i, ['Close']].values
    price2 = frame2.loc[i, ['Close']].values
    if price1 > 0 and price2 > 0 and i <= (length - 90):
        dev1 = price1 - avg1
        dev2 = price2 - avg2
        sd1num = sd1num + (dev1) ** 2
        sd2num = sd2num + (dev2) ** 2
        covnum = covnum+(dev1*dev2)
        sdcount = sdcount + 1
    if price1 > 0 and price2 > 0 and i > (length - 90):
        curdev1 = price1 - curavg1
        curdev2 = price2 - curavg2
        cursd1num = cursd1num + (curdev1) ** 2
        cursd2num = cursd2num + (curdev2) ** 2
        curcovnum = curcovnum+(curdev1*curdev2)
        cursdcount = cursdcount + 1

#for trading history up to last 3 months
sd1 = (sd1num/(sdcount-1))**(1/2)
sd2 = (sd2num/(sdcount-1))**(1/2)
cov=covnum/(sdcount-1)
corr = cov/(sd1*sd2)

#for last 3 months
cursd1 = (cursd1num/(cursdcount-1))**(1/2)
cursd2 = (cursd2num/(cursdcount-1))**(1/2)
curcov=curcovnum/(cursdcount-1)
curcorr = curcov/(cursd1*cursd2)

corrdisplay = str(corr)

print ("Historical Correlation:")
print(corrdisplay+"\n")

zrnum = float((1+corr)/(1-corr))
zr = (np.log(zrnum))/2
se = ((1/(sdcount-3))**(1/2))
zl = zr - st.norm.ppf(.95)*se
zu = zr + st.norm.ppf(.95)*se
corrl = ((np.exp(2*zl)-1)/(np.exp(2*zl)+1))
corru = ((np.exp(2*zu)-1)/(np.exp(2*zu)+1))
corrldisplay = str(corrl)
corrudisplay = str(corru)

print ("Confidence Interval:")
print ("[ "+corrldisplay+" , "+corrudisplay+" ]\n")

print ("Current Correlation:")
print (curcorr)




