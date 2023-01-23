import csv

def filecaller():
    filename = []
    for speedtxt in range(3,6):
        for degrees in range (0,300,60):
            filename.append("data/data-{degree}-0{speeddecimal}mps.csv".format(degree = degrees, speeddecimal = speedtxt))
    return filename

filename = filecaller()
train_files = [name for idx,name in enumerate(filename) if (((idx+1)!=2) and ((idx+1)!= 6 and ((idx+1)!=13)))]
print(train_files)