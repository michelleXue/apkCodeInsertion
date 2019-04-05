import os
import core


def assign_key_to_apk(key_path, assigned_path, rebuild_path):

    rebuild_apk_list_path = core.apk_list.apk_gen(rebuild_path)
    rebuild_apk_name_list = []

    for line in open(rebuild_apk_list_path).readlines():
        line = line.strip()
        rebuild_apk_name_list.append(line)

    files = os.listdir(assigned_path)

    i = 0
    for apk_name in rebuild_apk_name_list:
        key_file = key_path + apk_name + ".keystore"
        apk_assigned_file = assigned_path + apk_name + ".apk"
        apk_rebuild_file = rebuild_path + apk_name + ".apk"
        print("assigned apk: " + str(i))
        if apk_name in files:
            print("%s exists!!!!" % apk_name)
        else:
            cmd = "jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
             -storepass 123456 -keystore %s -signedjar %s %s abc.keystore" % (
                key_file, apk_assigned_file, apk_rebuild_file)
            print(cmd)
            os.system(cmd)
            i += 1
