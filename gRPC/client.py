import grpc

import regpro_pb2
import regpro_pb2_grpc

cName = "Nick" #Enter 4 digit server code here

print("Client " + cName + " is requesting servers...")
# channel = grpc.insecure_channel('localhost:50051')

# stub = regpro_pb2_grpc.regFuncStub(channel)

# response = stub.fetchServers(regpro_pb2.Name(code=cName))

# print(response.code)

import uuid
client_id = str(uuid.uuid1())
import serverpro_pb2
import serverpro_pb2_grpc

print("Client ID: ", client_id)
server_id = input("Enter Server ID: ")
port = 50051 + int(server_id)
channel = grpc.insecure_channel('localhost:'+str(port))

stub = serverpro_pb2_grpc.serverFuncStub(channel)

response = stub.addUser(serverpro_pb2.String(code=client_id))

print(response.value)