
''' *** special thank to project clanner/cocdp on github. '''

# This script helps you dump all resource stored in .sc file of Clash Royale
# 
#
# .sc file and resource contained within them are the assets of SUPERCELL Oy.
#
# The author of this script takes no responsibilities for how this script is used.
#
# you should know that:
#
#    Supercell Assets are developed and published by a Finnish company Supercell Oy.
#    All intellectual property rights to Supercell Assets are owned by Supercell Oy,
#    including copyright to the game characters and internationally registered
#    trademarks. Supercell Oy's copyright to Supercell Assets' characters and
#    international trademark registrations of the words "CLASH ROYALE", "HAY DAY"
#    and "BOOM BEACH" provide Supercell Oy with certain proprietary rights. This
#    includes the right to restrict the use of copyrighted works and/or trademarks,
#    or a confusingly similar works or trademarks, in association with confusingly
#    similar products or services.
#
#    (From DCMA-supercell: https://github.com/clanner/cocdp/blob/master/dmca-supercell.txt )

import io
import lzma
import sys
import argparse
import os


def dumpfile(inputfile, outputdir):

    # open input file in binary mode
    f = io.open(inputfile,'rb') 

    # read all bytes in file
    dat=[]
    dat = f.read(-1)
    dat = [d for d in dat]

    # skip .sc file header
    dat = dat[0x1A:] 

    # recover lzma file format
    for i in range(4):
        dat.insert(9,0)

    # decompress data
    ddata = lzma.decompress(bytearray(dat))
    

    # reconstruct file name
    n = inputfile.split('/')
    n = n[len(n)-1]   # get file name
    n = n.split('.')  
    n = n[0:len(n)-1] # exclude extension
    n = '.'.join(n)   # reconstruct file name

    # save decompressed data
    b = io.open(outputdir + '/' + n + '.decompressed','wb')
    b.write(ddata)
    b.close()

    # read file header.
    type0x12Ent = ddata[0]    # Polygon record, with header of (byte,byte,hword,hword), followed by type-11 records.
    type0xcEnt = ddata[2]     # Strings 
    type0x1Ent = ddata[4]     # bitmap 
    type0x7xfEnt = ddata[6]   # font info
    type0x8Ent = ddata[8]     # not documented
    type0x9Ent = ddata[0x0a]  # 7 byte records
    type0x11Ent = 0           # define Polygon

    count_names = ddata[0x11] # name count

    i = 0x13 + count_names * 2 

    # read all polygon name
    names = [] 
    for n in range(count_names):
        names.append(ddata[i+1:i+ddata[i]+1])
        i+=ddata[i]+1


    entries=[] # stored as [ [entryID, DataLength, Data[]], .. ]
    polygons=[]

    while i<len(ddata): # get all entries.
        did = ddata[i]
        i+=1
        dlen = int.from_bytes(ddata[i:i+4],'little',signed=False)
        i+=4
        entdata = [did,dlen,ddata[i:i+dlen]]
        i+=dlen
    
        entries.append(entdata) 
        if did==0x12:
            pd=[
                entdata[0],
                entdata[1],
                [
                    entdata[2][0],
                    entdata[2][1],
                    entdata[2][2:4],
                    entdata[2][4:6],
                    entdata[2][6],
                    entdata[2][7],
                    entdata[2][8:8+entdata[2][7]],
                    entdata[2][8+entdata[2][7]:len(entdata[2])]
                ]
            ]

            polygons.append(pd)
            pass

    print(names)
    #print(entries)
    print('names:' + str(len(names)))
    print(names)
    #print(entries)
    print('there are '+ str(len(entries)) + ' entries defined in this file.')
    print('with '+ str(len(polygons)) + ' Polygons defined')
    for i in polygons:
        print(i)
        print(len(i[2][6]))


def checkArgs():

    parser = argparse.ArgumentParser(description='Clash Royale .sc file resource dump')
    parser.add_argument('--sc', type=str,metavar='scfile', help='input .sc file')
    parser.add_argument('--output', type=str, metavar='outdir', help='output dir')

    parser.print_help()
    args = parser.parse_args()

    sc = args.sc.replace('\\','/')
    output = args.output.replace('\\','/')

    # ensure output directory exists
    if not os.path.exists(output):
        os.makedirs(output)

    return sc, output


     

if __name__ == '__main__':
    inputfile, outputdir = checkArgs()
    dumpfile(inputfile,outputdir)

