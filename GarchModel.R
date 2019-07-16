

#GARCH vol predictive models
#Mustang Capital, 2019

library(rugarch)

options(warn=-1)


historical_vol = function(returns, window_size){#fio how to select window size
  n = length(returns)

  temp_returns = numeric(window_size)
  sd_returns = numeric(n/window_size - 1)
  
  for(i in seq(2,(n-window_size), by=window_size)){
    temp_returns = returns[i:(i+window_size-1)]
    sd_returns[ceiling(i/window_size)] = sd(temp_returns)*sqrt(252)#scale sd to get annual
  }
  
  return(sd_returns)
}

BIC = function(n.loglike, params){
  return(2*log(params) + 2*n.loglike)
}

fit_garch = function(historical_dat, max_iter){#takes sd of returns from above function
  sd_returns = historical_dat[-1]
  garch11        <- ugarchspec(variance.model = list(model = "sGARCH", garchOrder = c(1, 0)), distribution.model = "norm")
  garchfit       <- ugarchfit(spec = garch11, data = sd_returns, solver = "hybrid")
  optim_model = garchfit

  new_model = optim_model

  optim_BIC = BIC(-log(likelihood(garchfit)), 2)#sum orders to get number of parameters

  new_BIC = optim_BIC
  g_order = 1
  a_order = 0
  
  optimal_g = g_order
  optimal_a = a_order
  

  while(g_order <= max_iter){#10% relative difference was selected arbitrarily
    a_order = 0
    while(a_order <= max_iter ){
      garch11        <- ugarchspec(variance.model = list(model = "sGARCH", garchOrder = c(g_order, a_order)), distribution.model = "norm")
      garchfit       <- ugarchfit(spec = garch11, data = sd_returns, solver = "hybrid")
      new_BIC = BIC(-likelihood(garchfit), (g_order + a_order))

      if(new_BIC < optim_BIC){ #objective is to minimize BIC
        optim_model = garchfit
        optim_BIC = new_BIC
        optimal_g = g_order
        optimal_a = a_order
      }
      a_order = a_order+1
    }
    
    g_order = g_order+1
  }
  
  return (c(optim_model, optimal_g, optimal_a))
}

forecast_vol = function(model, historical_dat, n_ahead, window_size) {#takes optimal garch model as input
  l = unlist(model[2:3], recursive=TRUE, use.names=TRUE)
  print(c('Model Order: ', l))
  hist_data_size = max(l)
  
  model = model[[1]]
  
  hist_data = historical_dat[(length(historical_dat)-hist_data_size + 1):length(historical_dat)]

  spec           <- getspec(model)
  setfixed(spec) <- as.list(coef(model))
  garchforecast1 <- ugarchforecast(model, n.ahead = ceiling(n_ahead/window_size), data = hist_data)
  unclassed = unclass(garchforecast1)
  sigma = attr(unclassed, 'forecast')$sigmaFor
  series = attr(unclassed, 'forecast')$seriesFor
  
  s = 0
  for(i in 1:ceiling(n_ahead/window_size)){
    s = s+(series[i]^2)*window_size/252
  }
  s = sqrt(s)*sqrt(252)/sqrt(n_ahead)
  
  sigmas = 0
  for(i in 1:ceiling(n_ahead/window_size)){
    sigmas = sigmas + (sigma[i]^2)
  }

  sigmas = sqrt(sigmas)
  
  sigma_one = cbind(series - sigma, series + sigma)
  colnames(sigma_one) = c('Lower Bound -1', 'Upper Bound + 1')
  sigma_two = cbind(series - 2*sigma, series + 2*sigma)
  colnames(sigma_two) = c('Lower Bound -2', 'Upper Bound + 2')
  
  print('Confidence Intervals')
  print(sigma_one)
  print(sigma_two)
  
  print('Total Prediction (2 std CI)')
  print(c(s - 2*sigmas, s + 2*sigmas))

  return(garchforecast1)
}

#Call this function with your ticker, number of days that you'd like to predict and the window size
run_all = function(ticker, n_ahead, window_size) {
  print(ticker)
  #Make sure you change the path to the file
  data = as.numeric(read.csv(paste(c('/Users/vishalchopra/Desktop/Predictions/', ticker, '.csv'), sep="", collapse=""))[['Returns']])
  window = window_size
  arr = historical_vol(data, window)
  model = fit_garch(arr, 15)
  prediction = forecast_vol(model, arr, n_ahead, window)
}

run_all('S', 10, 5)

