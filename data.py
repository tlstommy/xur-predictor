import matplotlib.pyplot as plt
#data from DCV of Io, Titan etc after season 11:


#0 == THE HANGAR 
#1 == WINDING COVE
#2 == WATCHER'S GRAVE

#each item is a week starting 9/13/2020 corresponding to nums above
locations = [0, 2, 0, 1, 0, 1, 0, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 2, 0, 2, 1, 0, 0, 0, 0, 2, 0, 1, 2, 0, 2, 1, 0, 2, 0, 2, 0, 2, 1, 0, 0, 2, 1, 0, 0, 2, 1, 0, 2, 0, 1, 2, 0, 2, 0, 2, 1, 0, 1, 0, 1, 2, 0, 1, 2, 1, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2, 0, 2, 0, 2, 0, 2, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 1, 0, 0, 2, 1, 2, 1, 2, 1, 0, 1, 1, 0, 2, 0, 2, 0, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 2, 0, 2, 1, 2, 1, 1, 0, 1, 2, 0, 1, 2, 0, 1, 0, 1, 2, 1, 2, 0, 1]
xAx = []

for i in range(len(locations)):
    xAx.append(i)


plt.plot(xAx, locations, '-')
plt.scatter(xAx,locations)
plt.show()