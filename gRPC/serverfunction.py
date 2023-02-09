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


