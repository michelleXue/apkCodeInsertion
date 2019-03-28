import os
import core


def decode_apk(root_path, decode_path):
    # get apk list file
    apk_list_file = core.apks_list_gen(root_path)

    # decode each apk file to decode path according to the apk list
    with open(apk_list_file) as f:
        for line in f:
            apk_origin_path = root_path + line.rstrip()
            apk_decode_path = decode_path + line.rstrip()
            if os.path.exists(apk_decode_path):
                print(line + "Decode path already exists!!")
                continue
            else:
                cmd = "apktool d %s.apk -o %s" % (apk_origin_path, apk_decode_path)
                print(cmd)
                os.system(cmd)