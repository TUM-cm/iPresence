#!/bin/bash

OPT=${1:-"nothing"}
ACTION=${2:-"nothing"}
CMD="python -u mysqldump_to_parquet.py"

if [ "$OPT" == "start" ] && [ "$ACTION" != "nothing" ]; then
	echo "Starting Pyconvert, logs can be found in nohup"
	rm nohup.out
	sudo nohup $CMD $ACTION > nohup.out 2>&1 </dev/null &
	exit
fi

if [ "$OPT" == "stop" ]; then
	echo "Stopping Pyconvert"
	sudo pkill -f "$CMD"
fi

if [ "$OPT" == "nothing"  ]; then
	echo "Please input \"start\" to launch Pyconvert or \"stop\" to stop it."
fi

if [ "$ACTION" == "nothing"  ]; then
	echo "Please specify action \"convert\" or \"join\"."
fi
