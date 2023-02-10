import grpc

import regpro_pb2
import regpro_pb2_grpc

cName = "Nick" #Enter 4 digit server code here

print("Client " + cName + " is requesting servers...")
channel = grpc.insecure_channel('localhost:50051')

stub = regpro_pb2_grpc.regFuncStub(channel)

response = stub.fetchServers(regpro_pb2.Name(code=cName))

print(response.code)

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

# print(response.value)

import datetime

if response.value == 0:
    print("REGISTRATION FAILED - Server Full")
else:
    print("REGISTRATION SUCCESSFUL")

    running= True    
    while running:
        print("Welcome!\n1 - Get Articles\n2 - Publish Article\n3 - Leave Server")
        choice = int(input("Enter Choice: "))

        if choice == 1:
            # response = stub.getArticles(serverpro_pb2.String(code=client_id))
            print(response.value)
        elif choice == 2:
            aType = int(input("Article Type - Sports (1) | Fashion (2) | Politics (3) : "))
            aAuthour= input("Article Authour: ")
            aYear = int(input("Article Year: "))
            aMonth = int(input("Article Month: "))
            aDay = int(input("Article Day: "))
            aContent = input("Article Content (Max Length - 200 chars): ")[0:200]

            aTime = (datetime.datetime(aYear, aMonth, aDay) - datetime.datetime(1, 1, 1)).days
            if(aType == 1):
                packet = serverpro_pb2.pubArticle(SPORTS=30, Author=aAuthour, Time=aTime, Content=aContent, User=client_id)
            elif(aType == 2):
                packet = serverpro_pb2.pubArticle(FASHION=30, Author=aAuthour, Time=aTime, Content=aContent, User=client_id)
            elif(aType == 3):
                packet = serverpro_pb2.pubArticle(POLITICS=30, Author=aAuthour, Time=aTime, Content=aContent, User=client_id)
            else:
                print("Invalid Article Type")
            response = stub.addArticle(packet)
            print(response.value)


        elif choice == 3:
            response = stub.removeUser(serverpro_pb2.String(code=client_id))
            # print(response.value)
            if response.value == 1:
                print("UNREGISTRATION SUCCESSFUL")
            else:
                print("UNREGISTRATION FAILED")
                
            running = False
            break
        else:
            print("Invalid Choice")