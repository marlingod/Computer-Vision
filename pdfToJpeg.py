# create a function that will scan a folder read the files and create the 
# function will receive 2 arguments. the reading folder and the saving folder

    # for each file in the inputpath:
        # process only files with PDF extension.
        # output the image page to the output path with contract_number+ page1+ with    
import PyPDF2
import struct
import os 

def tiff_header_for_CCITT(width, height, img_size, CCITT_group=4):
    tiff_header_struct = '<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
    return struct.pack(tiff_header_struct,
                       b'II',  # Byte order indication: Little indian
                       42,  # Version number (always 42)
                       8,  # Offset to first IFD
                       8,  # Number of tags in IFD
                       256, 4, 1, width,  # ImageWidth, LONG, 1, width
                       257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                       258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                       259, 3, 1, CCITT_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                       262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                       273, 4, 1, struct.calcsize(tiff_header_struct),  # StripOffsets, LONG, 1, len of header
                       278, 4, 1, height,  # RowsPerStrip, LONG, 1, lenght
                       279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                       0  # last IFD
                       )


def transformPdf(inputPath, outputPath):
    inputPath =inputPath
    outputPath = outputPath
    # get every file in that folder:
    for filenameFull in os.listdir(inputPath):
        filename, file_extension = os.path.splitext(filenameFull)
        if file_extension.lower()=='.pdf':
            #get the contractnumber 
            contractNumber = (filename.split("-")[0]).strip()
            pdf_filename = os.path.join(inputPath,filenameFull)
            pdf_file = open(pdf_filename, 'rb')
            cond_scan_reader = PyPDF2.PdfFileReader(pdf_file)
            for i in range(0, cond_scan_reader.getNumPages()):
                page = cond_scan_reader.getPage(i)
                xObject = page['/Resources']['/XObject'].getObject()
                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        """
                        The  CCITTFaxDecode filter decodes image data that has been encoded using
                        either Group 3 or Group 4 CCITT facsimile (fax) encoding. CCITT encoding is
                        designed to achieve efficient compression of monochrome (1 bit per pixel) image
                        data at relatively low resolutions, and so is useful only for bitmap image data, not
                        for color images, grayscale images, or general data.

                        K < 0 --- Pure two-dimensional encoding (Group 4)
                        K = 0 --- Pure one-dimensional encoding (Group 3, 1-D)
                        K > 0 --- Mixed one- and two-dimensional encoding (Group 3, 2-D)
                        """
                        if xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                            if xObject[obj]['/DecodeParms']['/K'] == -1:
                                CCITT_group = 4
                            else:
                                CCITT_group = 3
                            width = xObject[obj]['/Width']
                            height = xObject[obj]['/Height']
                            data = xObject[obj]._data  # sorry, getData() does not work for CCITTFaxDecode
                            img_size = len(data)
                            tiff_header = tiff_header_for_CCITT(width, height, img_size, CCITT_group)
                            img_name = str(contractNumber) + '-page'+str(i+1) + '.jpeg'
                            completeName =os.path.join(outputPath,img_name)
                            with open(completeName, 'wb') as img_file:
                                img_file.write(tiff_header + data)
                        #print (contractNumber,img_name)
            pdf_file.close()
