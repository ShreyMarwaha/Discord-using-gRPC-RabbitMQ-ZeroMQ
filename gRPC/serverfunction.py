def add_User(name, servNo):
    MaxUsers = 5

    f = open("/home/kali/Desktop/DSCD/A1/Code/UserList"+str(servNo), "r")
    tempData = f.read()
    currusers = int(tempData[0])
    print("Current Users - ", currusers)
    print()
    if(currusers>= MaxUsers):
        return 0
    else:
        currusers+=1
        print(f"User Name - {name} Registered!")
        # name="temp"
        newText = str(currusers) + tempData[1:] + "|" + name + str(currusers)
        print("Current Users - ", newText)
        f = open("/home/kali/Desktop/DSCD/A1/Code/UserList"+str(servNo), "w")
        f.write(newText)
        f.close()
        return currusers

def remove_User(name, servNo):
    f = open("/home/kali/Desktop/DSCD/A1/Code/UserList"+str(servNo), "r")
    tempData = f.read()
    currusers = int(tempData[0])
    if currusers == 0:
        return 0
    user = tempData.find(name)
    if user == -1:
        return 0
    newText = str(currusers-1) + tempData[1:user-1] + tempData[user+len(name):]
    f = open("/home/kali/Desktop/DSCD/A1/Code/UserList"+str(servNo), "w")
    f.write(newText)
    f.close()
    return 1

def add_article(Type, Time, Author, Content, servNo):
    f = open("/home/kali/Desktop/DSCD/A1/Code/ArticleList"+str(servNo), "r")
    tempData = f.read()
    currarticles = int(tempData[0])
    currarticles+=1
    divider = "^~^"
    newText = str(currarticles) + tempData[1:] + "|" + Type + "|&*~" + str(Time) + "|" + Author + "|" + Content + divider
    print(newText)
    f = open("/home/kali/Desktop/DSCD/A1/Code/ArticleList"+str(servNo), "w")
    f.write(newText)
    f.close()
    return currarticles

def get_article(Type, Author, Time, TimeCondition, servNos):
    
    serv = len(servNos)
    ans = ""
    for i in range(serv):
        servNo = servNos[i]
        f= open("/home/kali/Desktop/DSCD/A1/Code/ArticleList"+str(servNo), "r")
        tempData = f.read()
        currarticles = int(tempData[0])
        if currarticles == 0:
            searchRes=""
            continue

        divider = "^~^"
        searchRes = tempData
        # if TimeCondition == 531:
        #     return tempData[1:]

        if Type != "<BLANK>":
            searchRes = ""
            offset = tempData.find(Type)
            while(offset != -1):
                start = tempData.rfind(divider, 0, offset)
                if start == -1:
                    start = 1
                else:
                    start += len(divider)
                end = tempData.find(divider, offset)
                if end == -1:
                    end = len(tempData)
                searchRes += tempData[start:end] + divider
                
                offset = tempData.find(Type, end)
        
        
        if Author != "<BLANK>":
            search = searchRes
            searchRes = ""
            offset = search.find(Author)
            while(offset != -1):
                start = search.rfind(divider, 0, offset)
                if start == -1:
                    start = 1
                else:
                    start += len(divider)
                end = search.find(divider, offset)
                if end == -1:
                    end = len(search)
                searchRes += search[start:end] + divider
                offset = search.find(Author, end)
        
        # print(searchRes)

        if Time != -1:
            search = searchRes
            searchRes = ""
            timeStamp = "|&*~"
            offset= search.find(timeStamp)
            while(offset != -1):
                date = int(search[offset+4:search.find("|", offset+1)])
                if (TimeCondition < 0 ):
                    if date < Time:
                        start = search.rfind(divider, 0, offset)
                        if start == -1:
                            start = 1
                        else:
                            start += len(divider)
                        end = search.find(divider, offset)
                        if end == -1:
                            end = len(search)
                        searchRes += search[start:end] + divider
                elif (TimeCondition > 0):
                    if date >= Time:
                        start = search.rfind(divider, 0, offset)
                        if start == -1:
                            start = 1
                        else:
                            start += len(divider)
                        end = search.find(divider, offset)
                        if end == -1:
                            end = len(search)
                        searchRes += search[start:end] + divider
                offset = search.find(timeStamp, offset+1)
        # print(searchRes)
        ans += searchRes
    if ans == "":
        return "No Articles Found"
    return ans


                    


# get_article("<BLANK>","<BLANK>",689990,-1, 5)