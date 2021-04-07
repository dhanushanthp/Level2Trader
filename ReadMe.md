# Information
* Level 2 will show full depth. The market data subscriptions for Depth of Book (Level 2) quotes on US stocks are NYSE OpenBook, NYSE ArcaBook, NASDAQ TotalView-OpenView, NASDAQ BX TotalView and Cboe BZX Depth of Book.
* Call reqMarketDepth instead of reqTickbyTick for level II data. https://interactivebrokers.github.io/tws-api/market_depth.html


Level 1 would be the current best bid/offer prices

Top sales on bid  and ask really helped to find the signal but we need to build this in a different timeframe along with a total sales which is sum on bid and ask ratios.

If the ratio more than 50 percentage on ask compared to bid then it’s a bullish signal otherwise it’s bearish accordingly


Using tick by tick  to data we pick only level one bid and ask and time in sales. The level one bid and ask gives the current market demand or supply. because the overall market demand and supply comes from level two. Which can be requested through request market Depth API.
So we use the level one data only to find the sales on bid and ask with respect to last transaction.  Eventually the top sales on bid or ask.

We are trying to implement the bit and ask on sales


is there any way to find my market data through api is limited already? While I’m using the api?
Kunal Sa: you can find the exact number of market data lines by pressing key combination Ctrl-Alt-= on TWS

# BID and ASK  VS Last
The bid and ask should not be aggregated. Because those are not executed trades. It's just display as a flash values. On other hand the last data 
should be aggregated. Because those are completed trades.

# Features
## Identification of Sales on BID and ASK
### Key function
* Identify the sales on BID by comparing the price with level II BID.
    * If the "last" price very close to Level II BID then the transaction considered as "price on BID"
    * This is a bearish signal
* Identify the sales on ASK by comparing the price with level II ASK.   
    * If the "last" price very close to Level II ASK then the transaction considered as "price on ASK"
    * This is a bullish signal
* Aggregate total number of sales on BID over 10seconds(Configurable) and show as "On Bid count" which updates every 1 second
    * Count the concurrent call on bid and show along with the title
* Aggregate total number of sales on ASK over 10seconds(configurable) and show as "On Ask count" which updates every 1 second
    * Count the concurrent call on ASK and show along with the title
* Show top sale size over the 10second(Configurable) period
    * Top sales on Bid in "Top on Bid"
    * Top sales on Ask in "Top on Ask"

## Track the Top sales on BID and ASK by each minute
### Key Function
* Plot the top sales by 1 min timeframe. The 1 min has been choosed to match the 1 min chart.


# Issues and fixes
1. Why some time delay between tws and API
   > **Cause    :** Delay because of terminal output, Not because of the processing algorithms <br>
   > **Question :** After changing the terminal clearing to 100, the delay reduced?<br>
   > **Answer   :** 100 also lagging at market opening. So changed to 50. So the delay is moved. If we have further delay
   > then we will reduce the refresh rate.
2. If there is no delay, Is the values compare to tws is almost same match as the terminal values.
    1. Last on BID
    2. Last on ASK
    3. BID
    4. ASK
    5. Relevant sizes

3. Price Range: 
   > Added price range. Because when the spread is very high or the price moves fast then the results are moving out of range and some time casuse
   > errors

4. Check the tool on bigger price stocks - AAPL
    
6. How to properly close the connection
    > The version update of api fix the peer connection error. So temp fix works

7. The price on bid ask is not working properly. Sometimes the bigger sales slip to bids and vice versa. But the signals are working fine.
    * The current level 1 bid and ask is not updating properly.

# Experiment
1. What is the block size to show in tape reading window?
    > 100s works better also this was kind of an default values in trading platforms
2. Time frame (20s, 15s, 10s)
   > 10S works best, even in market open timings
3. What is the perfect size for a histogram.
    a. using 10K is very high, at the same time this  could be proposal to time frame. If we increase the time frame then the histogram size should be increased to 
    handle the screen size
    > The block size has been decided dynamically by taking mean of size in sales on bid and sales on ask then average of both, <br>
    > bid_size = `[1,2,3,4,5]` -> mean=3 <br>
    > ask_size = `[2,3,10,2,3]` -> mean=4 <br>
    > block size = `(3+4)/2` = 3.5
    
   
# Questions or doubts
1. Some times the ask is less than bid price. And how that prints in terminal
    12.38AM in file 4. price at $5.92 
    12:46 same price
2. Why the time stamp 21:33:21 assign to 21:33:20 with the frequency of 2 seconds
    > Since we are doing the round with base of 2 seconds. This is happening.<br> Like wise if we use base frequency of 5 seconds. Then 
   > `21,22,23` will be assigned to `20` and `24,25,26` will be assigned to `25`
   


# Current Challenges
1. The application will not work on high spread stocks. Such as spread more than 2C~3C


# Backlog
1. Filter out the smaller size trades on time and sales
2. Change the top sales on bid and ask over period from 1 min to shorter time frame (10s). So we can enter and exit trade fast. Don’t need to wait for whole 1 min. But check whether it’s working on 1 min.
	def myround(x, base=5):
	 	return base * round(x/base)
3. Current implementation supports to forex as well since we use the level 1 data. Check on possibility
	1. May need to tune the block sizes. Because the forex trades high in size
1. Adding exchange in to the analysis
2. Development of rules based on extracted outputs
   1. If top sales more than x%  go long or short on bid or ask
2. Implementation of ML model or buy signal to predict the possible hike
4. Currently, the implementation is on level 1 (time and sales, current bid and ask). May need to extend to   level II data. Which has very depth of bid and ask.
5. Implementation of plots in proper UI
	1. 3D plots for time and sales (z-time, x-bid, y-ask)
	2. Bar chart to show realtime level II only based on Level II api call. Raw visuals
6. Automated trading
	1. Implementation of automated trading where If the size on price goes more than x% of last n  	    minutes of trades. Give a signal to user. To get in trade or not. Then the user can just decide 	    throu	gh API.