### Order Book
order book implemented in both heap and fixedarray alogrithm for different products and market condition
the program consists of
1) MatchEngine - handling userinput or automation test file to orderrouter
2) OrderRouter - routing different requests to orderbook
3) orderbook - determin cross event as well as position management on life cycle of orders
4) MarketDepth - it implements two alogrithm heap and fixedarray with predefined price range. 
   it is pluggable to orderbook


#### usage
requirement: python 3.6 and above required

```
for interactive mode: python matchengine.py --method heap|fixedarray
for automatic test:   python matchengine.py --testfile data\test-basic.csv
to generate orders:   python python ordergenerator.py num_iter price_from price_to
```
to use heap based orderbook, orderid needs to be ascending

to use fixedarray method (price range needs to be same as defined in order generator)

`python matchengine.py --testfile data\test-generated.csv --method fixedarray --range 9000,11000`

#### testing
unit tests can be found in tests folder

there are generated data in data folder. refer to usage section to test them. 
output_fixedarray.log and output_heap.log are sample outputs
output_basic_heap is ouput from exercise example

#### performance
heap method: It is binary tree. so insert takes O(log n) time. select is O(1). for delete operation, first it marks
orders unexecutable (cancelled and filled). it deletes only if order is root and delete until executable. 
so if orderbook flooded with cancelled and filled orders near price action, it will cause slow performance

fixedarray method: it is implemented with array for all price points with each attached to fifo queue. 
it keeps track of best price level (buy->max, sell->min) . select and insert is O(1) but delete will cause search 
for next best price which worst case can be O(n)




