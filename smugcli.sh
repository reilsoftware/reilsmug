#!/bin/bash

export PYTHON_PATH=$PYTHON_PATH:/Users/reil/Library/Python/3.8/lib/python/site-packages/smugcli

export PATH=$PATH:/Users/reil/Library/Python/3.8/lib/python/site-packages/smugcli

#cd /Users/reil/Library/Python/3.8/lib/python/site-packages/smugcli

#smugcli.py login --key Hb8zfX4V6XLJzgJFnzmqK5m2BCfKwGZp --secret HDXJnLHmjrpZwDR9GZsTnZz8LG8rB7wn

#smugcli.py ls
smugcli.py sync -f $HOME/Pictures/year/
