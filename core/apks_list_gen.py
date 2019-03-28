import os


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


def folder_name_gen(folder_path):
    # TODO: generate apk list based on folder name.
    pass