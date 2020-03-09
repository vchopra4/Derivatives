import pandas as pd
from scipy.stats import percentileofscore
import matplotlib.pyplot as plt

tick = 'AAPL'
frame = pd.read_csv('/Users/andrewpecjak/Desktop/MCAP/' + tick + '.csv')
quintiles = []

for i in range (110,len(frame.index.values)):
    vols = frame.loc[11:i,'Volatility'].values
    cvol = vols[len(vols)-1]
    perc = percentileofscore(vols,cvol)
    perc=perc/100
    quint = 0
    if (perc < 0.2):
        quint = 1
    elif (perc < 0.4):
        quint = 2
    elif (perc < 0.6):
        quint = 3
    elif (perc < 0.8):
        quint = 4
    else:
        quint = 5
    print (quint)
    quintiles.append(quint)

plt.plot(quintiles)
plt.show()



