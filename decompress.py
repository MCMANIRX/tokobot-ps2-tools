import os
import sys
import struct


GAME_ROOT = "game/"
ROOT = "karakuri/"
OUT_ROOT = "karakuri_new/"


class File():
    size = 0
    offset = 0
    type = 0
    unk = 0
    path = ""
    name = ""
    poff = 0
    noff = 0

typeToByte = {
        "hxd" : 0x0,
        "at3" : 0x1,
        "spk" : 0x2,
        "mmg" : 0x3,
        "pak" : 0x4,
        "phf" : 0x5,
        "emd" : 0x6,
        "tm2" : 0x7,
        "guc" : 0x9,
        "mpk" : 0xb,
        "gmo" : 0xd,
        "epk" : 0xf,
        "phd" : 0x12,
        "pbd" : 0x13,
        "ico" : 0x14,
        "efp" : 0x16,
        "obj" : 0x17,
        "gim" : 0x18,
        "rct" : 0x19,
        "pss" : 0x1c,
}



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

# entry

debug = False
repack = False
if len(sys.argv)>1:
    for arg in sys.argv:
        if '-' in arg:
            option = arg.split('-')[1]
            if option == "debug" or option == "d":
                debug = True
            if option == "repack" or option == "r":
                repack = True

if not repack:
    ftypes = {}
    with fopen(GAME_ROOT+"karakuri.fhd", 'rb') as fhd:
        bin = fopen(GAME_ROOT+"karakuri.bin", 'rb')

        fhd.seek(0x8)
        size = to_int(fhd,4)
        filecount = to_int(fhd,4)
        fhd.seek(0x10)
        offsets = []
        offsets.append(to_int(fhd,4)) # 30 - filesize
        offsets.append(to_int(fhd,4)) # 66d4 - filetypes
        offsets.append(to_int(fhd,4)) # 8080 - unk (file size * 2)
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
                if file.type not in ftypes and "." in file.name:
                    ftypes[file.type] = file

            else:
                os.makedirs(ROOT+file.path, exist_ok=True)
                out = fopen(ROOT+file.path+file.name,"wb")
                if file.size < 0xffffff00: # detect null(?)
                    bin.seek(file.offset*0x800)
                    out.write(bin.read(file.size))
                    out.close()
                    print("Wrote",file.path,end="")
                    print(file.name,"size:",hex(file.size))
                else:
                    print("Wrote empty",file.path,end="")
                    print(file.name)
        if debug:
            print("\n")
            print("typeToByte = {")
            for type in ftypes.values():
                print(f"\t\"{type.name.split('.')[1]}\" : {hex(type.type)},")
                #print("types:   ",hex(type.type),"  ",type.path,end="")
               # print(type.name)
            print("}")

        fhd.close()
        bin.close()
        
else:
    os.makedirs(OUT_ROOT, exist_ok=True)

    files = []
    totalsize = 0
    bin_ptr = 0
    fhd_ptr = 0

    size_ptr = 0x30
    types_ptr = 0
    unk_ptr = 0
    name_ptr = 0
    offsets_ptr = 0

    new_bin = fopen(OUT_ROOT+"KARAKURI.BIN","wb")
    new_fhd = fopen(OUT_ROOT+"KARAKURI.FHD","wb")

    # Naive approach for testing
    with fopen("game/karakuri.fhd", 'rb') as fhd:

        fhd.seek(0xc)
        filecount = to_int(fhd,4)

        fhd.seek(0x1c)
        pathpathptr = to_int(fhd,4)
        fhd.seek(pathpathptr)
        last_file = File()
        for i in range(0,filecount):
            file = File()
            file.size =0xffffffff
            file.type = 0xff
            file.offset = 0xfffffffe

            fhd.seek(pathpathptr+i*8)

            pathptr = to_int(fhd,4)
            nameptr = to_int(fhd,4)

            fhd.seek(pathptr)
            file.path = readString(fhd).split("../../")[1]
            fhd.seek(nameptr) 
            file.name = readString(fhd)

            fbuf = fopen(ROOT+file.path+file.name,"rb")
            file.size = os.path.getsize(ROOT+file.path+file.name)
            if file.size == 0:
                file.size =0xffffffff
            
            ext = file.name.split(".")
            if len(ext)>1 and file.size < 0xffffff00:
                file.type = typeToByte[ext[1]]

                offset = totalsize
                blocks = 0
                print(totalsize)
                while True:
                    blocks+=1
                    if blocks*0x800 > file.size:
                        offset+=blocks*0x800
                        break
                print(blocks,"blokk",hex(totalsize),hex(file.size))
                file.offset = offset
                data = fbuf.read(file.size)

                new_bin.seek(file.offset)
                file.offset = int(file.offset/0x800)
                print(f"Writing {file.path}{file.name} of size {hex(file.size)} to {hex(new_bin.tell())}...")
                new_bin.write(data)

                files.append(file)
                last_file = file
                totalsize+=file.size


        new_fhd.seek(size_ptr)


        print("Writing new FHD sizes...")
        for file in files:
            new_fhd.write(struct.pack("<I",file.size))
        

        types_ptr = new_fhd.tell()
        print("Writing new FHD types...")
        for file in files:
            new_fhd.write(struct.pack("<B",file.type)) 

        while new_fhd.tell()%0x10!=0:
            new_fhd.seek(new_fhd.tell()+1)

        unk_ptr = new_fhd.tell()
        print("Writing new FHD unks...")           
        for file in files:
            new_fhd.write(struct.pack("<I",file.size*2 if file.size != 0xffffffff else 0xffffffff))  

        offsets_ptr = new_fhd.tell()
        for i in range(0,filecount):
            new_fhd.write(struct.pack("<I",0xaa))  # debug

        paths_ptr = new_fhd.tell()
        print("Writing new FHD paths and names...")
        for i in range(0,filecount*2):
            new_fhd.write(struct.pack("<I",0xea))  # debug

        paths = {}
        for file in files:
            if(file.path not in paths):
                paths[file.path] = new_fhd.tell()
                new_fhd.write(("../../"+file.path).encode("utf-8") + b'\x00') 
            file.poff = paths[file.path]
        

        for file in files:
            file.noff = new_fhd.tell()
            new_fhd.write(file.name.encode("utf-8") + b'\x00')
        totalsize = new_fhd.tell()

        new_fhd.seek(paths_ptr)
        for file in files:

            new_fhd.write(struct.pack("<I",file.poff))   
            new_fhd.write(struct.pack("<I",file.noff))   


        print("Writing new FHD file offsets...")
        new_fhd.seek(offsets_ptr)
        for file in files:

            new_fhd.write(struct.pack("<I",file.offset))   
        
        print("Writing header information...")

        new_fhd.seek(0x1)
        new_fhd.write("DHFd".encode("utf-8"))

        new_fhd.seek(0x8)
        new_fhd.write(struct.pack("<I",totalsize))
        new_fhd.write(struct.pack("<I",len(files)))

        new_fhd.write(struct.pack("<I",size_ptr))
        new_fhd.write(struct.pack("<I",types_ptr))
        new_fhd.write(struct.pack("<I",unk_ptr))
        new_fhd.write(struct.pack("<I",paths_ptr))
        new_fhd.write(struct.pack("<I",offsets_ptr))
        new_fhd.write(struct.pack("<I",0x1))



        print("Done.")

        new_fhd.close()
        new_bin.close()
        fhd.close()


        '''files = []
        for root, _, files in os.walk(ROOT):
            for file in files:
                file = fopen(os.path.join(root,file))'''

