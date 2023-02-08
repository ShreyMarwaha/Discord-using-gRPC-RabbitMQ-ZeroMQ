import grpc
import time
from concurrent import futures

import regpro_pb2
import regpro_pb2_grpc

import regfunc

class regFuncServicer(regpro_pb2_grpc.regFuncServicer):
    def newServer(self, request, context):
        # print("Request received from IP - ", request.ip)
        print()
        print("Request received from Server - ", request.code)
        response = regpro_pb2.Number()
        response.value = regfunc.new_Server(request.code)
        if (response.value == 0):
            print("Maximum Server Limit Reached! Server Dropped")
        else:
            print("Server Registered Successfully| Server Number - ", response.value)
        print()
        return response

    def fetchServers(self, request, context):
        # print("Request received from IP - ", request.ip)
        print()
        print("Request received to fetch Server list")
        response = regpro_pb2.Name()
        response.code = regfunc.fetch_Servers()
        print("Server List Sent")
        print()
        return response
    
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

regpro_pb2_grpc.add_regFuncServicer_to_server(regFuncServicer(), server)

f = open("/home/kali/Desktop/DSCD/A1/Code/serverList", "w")
f.write("0")
f.close()

print('Starting server. Listening on port 50051...')
server.add_insecure_port('[::]:50051')
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)

