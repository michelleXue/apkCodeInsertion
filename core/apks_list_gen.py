import os


# generate apk list based on the name of the .apk files
def apk_name_gen(apk_path):
    arr_apk = [x for x in os.listdir(apk_path) if x.endswith(".apk")]
    # write to apklist
    apk_list = apk_path + "apk_list.txt"
    f = open(apk_list, "w+")
    for apk in arr_apk:
        file_name = apk.replace(".apk", "")
        f.write("%s\n" % file_name)
    f.close()

    return apk_list


# generate apk list based on the name of the apk folders in insertion file
def folder_name_gen(apk_path):
    arr_apk = []
    for x in os.listdir(apk_path):
        if os.path.isdir(os.path.join(apk_path, x)):
            arr_apk.append(x)

    # write to apklist
    apk_list = apk_path + "apk_list.txt"

    with open(apk_list, "w") as f:
        for apk in arr_apk:
            file_name = apk.rstrip()
            f.write("%s\n" % file_name)
    f.close()

