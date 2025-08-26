import os
import sys


ROOT = "karakuri/"

def to_int(f,sz):
    return int.from_bytes(f.read(sz),byteorder="little")

def readString(f):
    str = []
    chr = 'a'
    while(chr!=b'\x00'):
        chr = f.read(1)
        if chr==b'\x00':
            break
        else:
            str.append(chr)
    return b"".join(str).decode("utf-8")

def printh(ls):
    for x in ls:
        print(hex(x),end = " ")

def hex_f(value):
    return f'0x{value:04x}'

def fopen(fname,mode):
    try:
        file = open(fname, mode)

    except Exception as e:
        print(e)
        quit()
    return file

class File():
    size = 0
    offset = 0
    type = 0
    unk = 0
    path = ""
    name = ""



debug = False
if len(sys.argv)>1:
    if sys.argv[1] == "debug":
        debug = True

with fopen("game/karakuri.fhd", 'rb') as fhd:
    bin = fopen("game/karakuri.bin", 'rb')

    fhd.seek(0x8)
    size = to_int(fhd,4)
    filecount = to_int(fhd,4)
    fhd.seek(0x10)
    offsets = []
    offsets.append(to_int(fhd,4)) # 30 - filesize
    offsets.append(to_int(fhd,4)) # 66d4 - filetypes
    offsets.append(to_int(fhd,4)) # 8080 - unk
    offsets.append(to_int(fhd,4)) # 14dc8 - filename offsets
    offsets.append(to_int(fhd,4)) # e724 - offset/0x800



    for i in range(0,filecount):
        struct = []

        file = File()

        fhd.seek(offsets[0]+4*i)
        file.size = to_int(fhd,4)

        fhd.seek(offsets[1]+1*i)
        file.type = to_int(fhd,1)

        fhd.seek(offsets[2]+4*i)
        file.unk = to_int(fhd,4)

        fhd.seek(offsets[3]+8*i) 
        path = to_int(fhd,4)
        name = to_int(fhd,4)

        fhd.seek(path)
        file.path = readString(fhd).split("../../")[1]

        fhd.seek(name) 
        file.name = readString(fhd)

        fhd.seek(offsets[4]+4*i)
        file.offset = to_int(fhd,4)
        
        if debug:
            print("struct:",hex_f(file.size),hex(file.type),hex_f(file.unk),hex_f(file.offset),file.path,file.name)
            
        else:
            os.makedirs(ROOT+file.path, exist_ok=True)
            out = fopen(ROOT+file.path+file.name,"wb")
            if file.size < 0xffffff00:
                bin.seek(file.offset*0x800)
                out.write(bin.read(file.size))
                out.close()
                print("Wrote",file.path,end="")
                print(file.name,"size:",hex(file.size))
            else:
                print("Wrote empty",file.path,end="")
                print(file.name)

    fhd.close()
    bin.close()
    

        


    

