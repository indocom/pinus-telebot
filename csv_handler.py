import csv

def readCSVfromFile(csv_file_path) :
    storage = dict()
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0 :
                storage[line_count - 1] = row;
            line_count += 1
        print(f'Processed {line_count} lines.')
    return storage

def writeToCSV(csv_file_path, storage, fieldname) :
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        length = len(storage)
        writer.writerow(fieldname)
        for i in range(length):
            writer.writerow(storage[i]);


        

