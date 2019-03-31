import os
import errno
import subprocess

CONST_PATTERN_LOCAL = ".local"


# filter the apk files, only insert to the one that has the target line of code.
# insert type: insert at the beginning, insert after the target line of code.
def filter_and_insert_apk(decode_path, insert_path, apk_list_path, pattern):
    with open(apk_list_path) as apk_list:
        for apk in apk_list:
            apk_insert_file_list = _get_insert_files(apk, pattern, decode_path, insert_path)
            if apk_insert_file_list is not None:
                for apk_insert_file_decode_path in apk_insert_file_list:
                    if 'android/support' not in apk_insert_file_decode_path:
                        apk_insert_file_insert_path = apk_insert_file_decode_path.replace("/decode", "/insertion")
                        # scan_and_insert_file(insertion_file_path, decode_file_path)
                        _insert_at_beginning(apk_insert_file_insert_path, apk_insert_file_decode_path, pattern)
                        # insert_every_method(insertion_file_path, decode_file_path)
    apk_list.close()


# get an apk's inserted files
# if inserted file is None, do not copy to insert folder;
# if not None, copy decode files to insert folder, and return inserted file list.
def _get_insert_files(apk, pattern, decode_path, insert_path):
    apk_decode_path = decode_path + apk
    apk_insert_path = insert_path + apk

    # create a new folder for each apk file to insert, read from old decode file to make copy
    if not os.path.exists(os.path.dirname(apk_insert_path)):
        try:
            os.makedirs(os.path.dirname(apk_insert_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # search the inserted files in insertion path
    cmd = "grep -lr \"%s\" %s" % (pattern, apk_decode_path)
    try:
        byte_output = subprocess.check_output(cmd, shell=True)
        result = str(byte_output, 'utf-8')

        # copy all the files to insertion
        cmd = "cp -a %s %s" % (apk_decode_path, apk_insert_path)
        print(cmd)
        os.system(cmd)
        return result.rstrip().split("\n")
    except subprocess.CalledProcessError:
        # no copy, since no pattern has been found.
        return None


# insert code segement at the beginning of the method
def _insert_at_beginning(insertion_file_path, decode_file_path, pattern):

    is_buffer = False
    method_name = ""
    method_head, method_local, method_body, method_end = "", "", "", ""
    added_part = ""

    with open(insertion_file_path, "w") as f_insertion_write:
        with open(decode_file_path, "r") as f_decode_read:
            for line in f_decode_read:
                # case 1: is in the middle of a method
                if is_buffer:
                    if _is_method_end(line):  # case 1.1, meet endline of a methodß
                        is_buffer = False
                        method_end = line
                        method = method_head + method_local + added_part + method_body + method_end
                        f_insertion_write.write(method)
                        #  need to clean up the parameters
                        method_name = ""
                        method_head, method_local, method_body, method_end = "", "", "", ""
                        added_part = ""
                    else:  # case 1.2, in the body of a method
                        if CONST_PATTERN_LOCAL in line:  # case 1.2.1, find .local in method
                            method_local = line
                            continue
                        if pattern in line:  # if pattern detected, then insert code, otherwise, do not insert.
                            method_local = _update_local(method_local)
                            method_body = method_body + line
                            added_part = _inserted_text(method_name, decode_file_path)
                            continue
                        else:  # case 1.2.1, others line, just directly append at method
                            method_body = method_body + line
                            continue
                else:  # case 2: is not in the middle of a method
                    if _is_method_start(line):  # case 2.1: method start line, get method name to print
                        method_name = _get_method_name(line)
                        method_head = line
                        is_buffer = True
                    else:
                        f_insertion_write.write(line)

    f_insertion_write.close()
    f_decode_read.close()


def _is_method_start(line: str) -> bool:
    return line.startswith(".method")


def _is_method_end(line):
    return line.startswith(".end method")


def _get_method_name(line):
    return line[len('.method '):line.find('(')]


def _update_local(old_local, added_var_num):
    # maximum register is v15, then local number will not exceed this amount
    pattern_local = ".locals "
    # get old number of local
    var_number = int(old_local[len(pattern_local) + old_local.find(pattern_local):])

    # update number of local
    # max register is 15
    if var_number < (15 - added_var_num + 1):
        var_new = str(var_number + added_var_num)
    else:
        # do not update the var_new
        var_new = str(var_number)

    new_local = "    .locals " + var_new

    return new_local


# insert method name and file path in each method.
# print text name with decode file path
def _inserted_text(method_name, decode_file_path):

    # var_number: int = int(line[len('.locals ') + line.find('.locals'):])  # find variable name number of EditText
    # var_name_tag = "v" + str(var_number + 1)
    # var_path_tag = "v" + str(var_number + 2)
    # var_name = "v" + str(var_number + 3)
    # var_path = "v" + str(var_number + 4)

    text_to_be_added = "\n\
    const-string v1, \"Xue: print Method Name: \" \n\
    const-string v2, \"Xue: print Method Path: \" \n\
    const-string v3, \" %s \"\n\
    const-string v4, \" %s \" \n\
    invoke-static{v1, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n\
    invoke-static{v2, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n" % (method_name, decode_file_path)

    return text_to_be_added

