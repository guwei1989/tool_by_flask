pkill -f irain_tools
source vv/bin/activate
nohup python irain_tools_web.py >> server.log &
