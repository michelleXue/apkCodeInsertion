import os
import core

def key_gen(key_path, rebuild_path):

    apk_list_path = core.apks_list_gen.folder_name_gen(rebuild_path)
    apk_name_list = []

    for line in open(
            apk_list_path).readlines():
        line = line.strip()
        apk_name_list.append(line)
    print("total number of apks: %d" % (len(apk_name_list)))

    i = 0
    files = os.listdir(key_path)
    for line in apk_name_list:
        print("key assigned: " + str(i))
        line = line + ".keystore"
        if line in files:
            print("%s exists!!!!" % line)
        else:
            cmd1 = "keytool -genkeypair -dname \"cn=Mark Jones, ou=JavaSoft, o=Sun, c=US\" \
            -alias abc.keystore -keyalg RSA -keypass 123456 -keystore %s -storepass 123456 -validity 20000" % (
                        key_path + line)
            print(cmd1)
            os.system(cmd1)
            i += 1
