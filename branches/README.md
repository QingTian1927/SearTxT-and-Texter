# Differences between the Branches
## Attention
I don't really recommend using any of these branches as they are maintained with minimal effort. 

If you still want to use them, please be aware that **you may experience various kinds of bugs that may or may not damage your system.** 

(This should not be the case though as I've programmed SearTxT & Texter to be as non-destructive as possible)

### SearTxT Mix-threaded 
In this branch, the `exact searcher` is single-threaded, whereas the `approximate searcher` is multi-threaded.

During my testing, I noticed that the exact searcher performs significantly better single-threaded than multi-threaded when the search database is relatively small (~ `0.01807s` vs. `0.02647s`). 

However, this doesn't scale well at all with large databases, and using the exact searcher becomes rather tedious when it has to go through hundreds of files at once (took roughly 2s to return 220 results from a set of 81 files)

### SearTxT Single-threaded
In this branch, both the `exact searcher` and the `approximate searcher` are single-threaded.

This helps to reduce the size of the executable as well as the amount of memory that is used. However, the searchers perform *very* poorly and the searching process becomes *very* tedious.

I don't really recommend using this branch for production purposes as it is maintained with minimal effort.

### SearTxT & Texter Pre-Coreutils
This is the original version of SearTxT & Texter prior to the Coreutils Refactor, which comes only in one single file and is much more portable as a result.

