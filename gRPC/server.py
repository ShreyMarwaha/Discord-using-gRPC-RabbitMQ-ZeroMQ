import grpc

import regpro_pb2
import regpro_pb2_grpc

sCode = input("Enter 4 letter server code... ") #Enter 4 digit server code here

while(len(sCode) != 4):
    sCode = input("Enter 4 letter server code... ")

sCode = sCode.upper()

print("Server " + sCode + " is requesting to register...")
channel = grpc.insecure_channel('localhost:50051')

stub = regpro_pb2_grpc.regFuncStub(channel)

response = stub.newServer(regpro_pb2.Name(code=sCode))

if (response.value == 0):
    print("Maximum Server Limit Reached")
    start=False
else:
    print("Server Registered Successfully! | Server Number - ", response.value)
    start=True
    
servNumber = response.value
serversToCheck = []
serversToCheck.append(servNumber)

if (start == True):
    import time
    from concurrent import futures

    import serverpro_pb2
    import serverpro_pb2_grpc

    import serverfunction

    class serverFuncServicer(serverpro_pb2_grpc.serverFuncServicer):
        def addUser(self, request, context):
            print()
            print("Request received to add user - ", request.code)
            response = serverpro_pb2.Ints()
            response.value = serverfunction.add_User(request.code, servNumber)
            if (response.value == 0):
                print("Maximum User Limit Reached! User Dropped")
            else:
                print("User Registered Successfully| User Number - ", response.value)
            print()
            return response

        def removeUser(self, request, context):
            print()
            print("Request received to remove user - ", request.code)
            response = serverpro_pb2.Ints()
            response.value = serverfunction.remove_User(request.code, servNumber)
            if (response.value == 0):
                print("User Not Found! User Dropped")
            else:
                print("User Removed Successfully")
            print()
            return response

        def addArticle(self, request, context):
            print()
            print("Request received to Publish Article from user - ", request.User)
            response = serverpro_pb2.Ints()
            response.value = serverfunction.add_article(request.WhichOneof("Type"), request.Time, request.Author, request.Content, servNumber)
            if (response.value == 0):
                print("Article Add failure, TRY AGAIN!")
            else:
                print("Article Added Successfully| Article Number - ", response.value)
            print()
            return response

        def fetchArticle(self, request, context):
            print()
            print("Request received to fetch article from user - ", request.User)
            response = serverpro_pb2.String()

            if(request.WhichOneof("Type") == "none"):
                print("Searching for Articles ... <BLANK> " , request.Author, request.Time)
                response.code = serverfunction.get_article("<BLANK>", request.Author , request.Time , request.Timebf, serversToCheck)
            else:
                print("Searching for Articles ... ", request.WhichOneof("Type") , request.Author, request.Time)
                response.code = serverfunction.get_article(request.WhichOneof("Type"), request.Author , request.Time , request.Timebf, serversToCheck)
            
            print("Articles Sent to User")
            return response

            

            

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    serverpro_pb2_grpc.add_serverFuncServicer_to_server(serverFuncServicer(), server)

    f = open("/home/kali/Desktop/DSCD/A1/Code/UserList"+str(servNumber), "w")
    f.write("0")
    f.close()

    f = open("/home/kali/Desktop/DSCD/A1/Code/ArticleList"+str(servNumber), "w")
    f.write("0")
    f.close()

    port = 50051 + servNumber
    print('Starting server ' + str(sCode) + ' . Listening on port ' + str(port))
    server.add_insecure_port('[::]:'+str(port))
    server.start()

    try:
        while True:
            par = -1
            try:
                par = int(input("Press -> 0 - Get Servers || 1 - Register to a Server - "))
            except ValueError:
                print("Invalid Input")
                continue

            if (par == 0):
                channel = grpc.insecure_channel('localhost:50051')
                stub = regpro_pb2_grpc.regFuncStub(channel)
                response = stub.fetchServers(regpro_pb2.Name(code="SERV"))
                print(response.code)
            elif (par == 1):
                NewServer = int(input("Enter Server Code to Register to - "))
                if(serversToCheck.count(NewServer) == 0):
                    serversToCheck.append(NewServer)


            
            
    except KeyboardInterrupt:
        server.stop(0)




