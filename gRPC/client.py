import grpc

import regpro_pb2
import regpro_pb2_grpc

import uuid
client_id = str(uuid.uuid1())
cName = client_id
print("Client " + cName + " is requesting servers...")
channel = grpc.insecure_channel('localhost:50051')

stub = regpro_pb2_grpc.regFuncStub(channel)

response = stub.fetchServers(regpro_pb2.Name(code=cName))

print(response.code)


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
        print()
        print(
            "------------------------------------------------------------"
        )
        print("Welcome!\n1 - Get Articles\n2 - Publish Article\n3 - Leave Server")
        choice = int(input("Enter Choice: "))

        if choice == 1:
            # response = stub.getArticles(serverpro_pb2.String(code=client_id))
            aType = int(input("Article Type - Sports (1) | Fashion (2) | Politics (3) : | All (4) : "))
            temp=0
            aAuthor = input("Article Author (enter all to leave blank): ")
            if(aAuthor == "all"):
                temp+=1
                aAuthor = "<BLANK>"
            aYear = int(input("Article Year (enter 13 to leave blank): "))
            
            if(aYear != 13):
                aMonth = int(input("Article Month: "))
                aDay = int(input("Article Day: "))
                aTimers = int(input("Article Before (1) or On and After (2): "))
                if (aTimers == 1):
                    aTimers = -1
                else:
                    aTimers = 1
                aTime = (datetime.datetime(aYear, aMonth, aDay) - datetime.datetime(1, 1, 1)).days
            else:
                temp+=1
                aTime = -1
                aTimers = -1

            if(aType == 1):
                packet = serverpro_pb2.getArticle(SPORTS=30, Author=aAuthor, Time=aTime, Timebf=aTimers,  User=client_id)
            elif(aType == 2):
                packet = serverpro_pb2.getArticle(FASHION=30, Author=aAuthor, Time=aTime, Timebf=aTimers,  User=client_id)
            elif(aType == 3):
                packet = serverpro_pb2.getArticle(POLITICS=30, Author=aAuthor, Time=aTime, Timebf=aTimers,  User=client_id)
            elif(aType == 4):
                if(temp == 2):
                    print("Invalid Input - ALL BLANKS NOT ALLOWED")
                    continue
                packet = serverpro_pb2.getArticle(none=30, Author=aAuthor, Time=aTime, Timebf=aTimers,  User=client_id)
            else:
                print("Invalid Input")
            
            response = stub.fetchArticle(packet)
            
            articlesList = response.code
            # print(articlesList)
            timeStamp = "&*~"
            offset= articlesList.find(timeStamp)

            while offset != -1:
                start = offset
                end = articlesList.find("|", offset+1)
                days = int(articlesList[offset+3:end])

                date = datetime.datetime(1, 1, 1) + datetime.timedelta(days=days)

                # print("Date: ", date.strftime("%d/%m/%Y"))

                articlesList = articlesList[0:start] + date.strftime("%d/%m/%Y") + articlesList[end:]
                offset = articlesList.find(timeStamp, offset+1)

            divider = "^~^"
            
            finalList = articlesList.replace(divider, "\n")
            # print(articlesList)
            print("Articles:\n", finalList)

            

        elif choice == 2:
            aType = int(input("Article Type - Sports (1) | Fashion (2) | Politics (3) : "))
            aAuthor= input("Article Author: ")

            aContent = input("Article Content (Max Length - 200 chars): ")[0:200]

            aTime = (datetime.datetime.now() - datetime.datetime(1, 1, 1)).days
            if(aType == 1):
                packet = serverpro_pb2.pubArticle(SPORTS=30, Author=aAuthor, Time=aTime, Content=aContent, User=client_id)
            elif(aType == 2):
                packet = serverpro_pb2.pubArticle(FASHION=30, Author=aAuthor, Time=aTime, Content=aContent, User=client_id)
            elif(aType == 3):
                packet = serverpro_pb2.pubArticle(POLITICS=30, Author=aAuthor, Time=aTime, Content=aContent, User=client_id)
            else:
                print("Invalid Article Type")
            response = stub.addArticle(packet)
            if response.value >0:
                print("PUBLISH SUCCESSFUL")
            else:
                print("PUBLISH FAILED. TRY AGAIN")
            # print(response.value)


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