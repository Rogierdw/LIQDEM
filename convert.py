import os, xlsxwriter, csv, glob

csvfile = glob.glob("bounded*.csv")[0]
for csvfile in glob.glob("bounded*.csv"):

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(csvfile+".xlsx", {'strings_to_numbers': True})
    worksheet = workbook.add_worksheet()

    r=0

    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            c = 0
            for item in row:
                worksheet.write(r,c,item)
                c+=1
            r+=1


    worksheet.write(r+1,0, '=GEMIDDELDE(A2:A11)')

    workbook.close()
    os.remove(csvfile)