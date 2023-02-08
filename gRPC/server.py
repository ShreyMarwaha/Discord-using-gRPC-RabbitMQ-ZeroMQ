import grpc

import regpro_pb2
import regpro_pb2_grpc

sCode = "GOTM" #Enter 4 digit server code here

print("Server " + sCode + " is requesting to register...")
channel = grpc.insecure_channel('localhost:50051')

stub = regpro_pb2_grpc.regFuncStub(channel)

response = stub.newServer(regpro_pb2.Name(code=sCode))

if (response.value == 0):
    print("Maximum Server Limit Reached")
else:
    print("Server Registered Successfully! | Server Number - ", response.value)
