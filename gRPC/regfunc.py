def new_Server(name):
	MaxServers = 5

	f = open("/home/kali/Desktop/DSCD/A1/Code/serverList", "r")
	tempData = f.read()
	currservers = int(tempData[0])
	print("Current Servers - ", currservers)
	print()
	if(currservers>= MaxServers):
		return 0
	else:
		currservers+=1
		print(f"Server Number - {currservers} Online!")
		# name="temp"
		newText = str(currservers) + tempData[1:] + "|" + name.upper() + str(currservers)
		print("Current Servers - ", newText)
		f = open("/home/kali/Desktop/DSCD/A1/Code/serverList", "w")
		f.write(newText)
		f.close()
		return currservers


def fetch_Servers():
	f = open("/home/kali/Desktop/DSCD/A1/Code/serverList", "r")
	tempData = f.read()
	data = ""
	if (int(tempData[0]))>0:
		data += "Servers Online: " + tempData[0] + "\nName | Server Number \n"

		for i in range(0, int(tempData[0])):
			data+= tempData[(2+i*6):(6+i*6)] + " | " + tempData[(6+i*6)] + "\n"
		return data
	else:
		return "No servers online"
	
		
		





