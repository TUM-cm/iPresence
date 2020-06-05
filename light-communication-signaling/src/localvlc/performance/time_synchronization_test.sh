#!/bin/bash
limit=100   # Set your limit in milliseconds here
offsets=$(ntpq -nc peers | tail -n +3 | cut -c 62-66 | tr -d '-')
for offset in ${offsets}; do
    if [ ${offset:-0} -ge ${limit:-100} ]; then
        echo "An NTPD offset is excessive - Please investigate"
        exit 1  
    fi  
done
# EOF