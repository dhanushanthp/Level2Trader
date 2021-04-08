ps -ef | grep tape_reader.sh | grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep tape_reader_api_call | grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep forex_reader.sh | grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep forex_api_call | grep -v grep | awk '{print $2}' | xargs kill
