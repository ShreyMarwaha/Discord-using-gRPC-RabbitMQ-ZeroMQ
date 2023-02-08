import grpc

import regpro_pb2
import regpro_pb2_grpc

cName = "Nick" #Enter 4 digit server code here

print("Client " + cName + " is requesting servers...")
channel = grpc.insecure_channel('localhost:50052')

stub = regpro_pb2_grpc.regFuncStub(channel)

response = stub.fetchServers(regpro_pb2.Name(code=cName))

print(response.code)
