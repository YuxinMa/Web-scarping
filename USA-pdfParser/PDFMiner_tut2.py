# importing required modules
import PyPDF2

pdfFile = '/home/yikang/Dropbox/disclosures-data/Yikang-Yang/United_States/data_2014/2014_Beatty,Hon.Joyce_OH03_FD Original.pdf'
# creating a pdf file object
pdfFileObj = open(pdfFile, 'rb')

# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

# printing number of pages in pdf file
print(pdfReader.numPages)

# creating a page object
pageObj = pdfReader.getPage(0)

# extracting text from page
print(pageObj.extractText())

# closing the pdf file object
pdfFileObj.close()
