# BID and ASK  VS Last
The bid and ask should not be aggregated. Because those are not executed trades. It's just display as a flash values. On other hand the last data 
should be aggregated. Because those are completed trades.

# Features
## Identification of Sales on BID and ASK
### Key function
* Identify the sales on bid
* Identify the sales on ask
* Aggregate total number of sales on bid over 10seconds(Configurable) and show as "On Bid count" every 1 second
    * Count the concurrent call on bid and show along with the title
* Aggregate total number of sales on ask over 10seconds(configurable) and show as "On Ask count" every 1 second
    * Count the concurrent call on ask and show along with the title
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
   


# Current Challenges
1. The application will not work on high spread stocks. Such as spread more than 2C~3C