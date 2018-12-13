import os, xlsxwriter, csv, glob

for csvfile in glob.glob("*.csv"):

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(str.replace(csvfile, ".csv", ".xlsx"), {'strings_to_numbers': True})
    worksheet = workbook.add_worksheet()

    r=2

    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            c = 0
            for item in row:
                worksheet.write(r,c,item)
                c+=1
            r+=1


    #worksheet.write(0,0, '=GEMIDDELDE(A3:A'+str(r)+')')
    worksheet.write(0, 0, '=GEMIDDELDE(A4:A103)')
    worksheet.write(1, 0, '=STDEV.P(A4:A103)')


    workbook.close()
    os.remove(csvfile)