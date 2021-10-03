import csv

def readCSVfromFile(csv_file_path) :
    repo_data = dict()
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0 :
                repo_data[line_count - 1] = row;
            line_count += 1
        print(f'Processed {line_count} lines.')
    return repo_data

def writeToCSV(csv_file_path, repo_data) :
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        length = len(repo_data)
        fieldname = ['chat_id', 'owner_name', 'repo_url']
        writer.writerow(fieldname)
        for i in range(length):
            writer.writerow(repo_data[i]);


        

