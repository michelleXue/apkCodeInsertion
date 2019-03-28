import os


apkNameList = []


def rebuild_apk(rebuild_path, insert_path):
    for file in os.listdir(insert_path):
        if os.path.isfile(os.path.join(insert_path, file)):
            continue

        if file in os.listdir(rebuild_path):
            print("Exists!!!!")

        else:
            # rebuild
            cmd = "apktool b %s%s -o %s%s.apk" % (insert_path, file, rebuild_path, file)
            print(cmd)
            os.system(cmd)


if __name__ == "__main__":
    rebuild_apk_path = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/rebuild_apks/"
    decode_file_path = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/insertions/"
    rebuild_apk(rebuild_apk_path, decode_file_path)
