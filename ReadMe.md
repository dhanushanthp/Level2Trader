# BID and ASK 
The bid and ask should not be aggregared. Because those are not executed trades.
It's just display as a flash values. On other hand the last data should be aggregared
Because those are completed trades.

# Check List
1. Why some time delay between tws and api
    a. after chacing the terminal clearing to 100, the delay reducsd
2. If there is no delay, Is the values compare to tws is almost same match as the terminal values.
    1. Last on BID
    2. Last on ASK
    3. BID
    4. ASK
    5. Relevant sizes
3. Price Range: Works better without price range.
4. Check the tool on bigger price stocks - AAPL

# Expirement
1. What ist he block size
2. Time frame (20s, 15s, 10s)
3. What is the perfect size for histogram.
    a. using 10K is very high, at the same time this is could be proposanal to time frame. If we increase the time frame then the histogram size should be increased to 
    handle the screen size
    b. 20s is too much. Should be around 10 to 15 sec. 
    
    
    
# Questions or doubts
1. Some times the ask is less than bid price. and how that prints in terminal
    12.38AM in file 4. price at $5.92 
    12:46 same price