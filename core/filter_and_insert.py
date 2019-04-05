import os
import errno
import subprocess

CONST_PATTERN_LOCAL = ".local"


# filter the apk files, only insert to the one that has the target line of code.
# insert type: insert at the beginning, insert after the target line of code.
def filter_and_insert_apk(decode_path, insert_path, apk_list_path, pattern):
    with open(apk_list_path) as apk_list:
        for apk in apk_list:
            print(apk)
            apk_insert_file_list = _get_insert_files(apk, pattern, decode_path, insert_path)
            if apk_insert_file_list is not None:
                for apk_insert_file_decode_path in apk_insert_file_list:
                    if 'android/support' not in apk_insert_file_decode_path:
                        apk_insert_file_insert_path = apk_insert_file_decode_path.replace("/decoded", "/insertion")
                        # scan_and_insert_file(insertion_file_path, decode_file_path)
                        # insert_at_beginning(apk_insert_file_insert_path, apk_insert_file_decode_path, pattern, '')
                        _insert_in_situ(apk_insert_file_insert_path, apk_insert_file_decode_path, pattern, 'EditText')
                        # insert_every_method(insertion_file_path, decode_file_path)
    apk_list.close()


# get an apk's inserted files
# if inserted file is None, do not copy to insert folder;
# if not None, copy decode files to insert folder, and return inserted file list.
def _get_insert_files(apk, pattern, decode_path, insert_path):
    apk_decode_path = decode_path + apk.rstrip()
    apk_insert_path = insert_path + apk.rstrip()

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
        cmd = "cp -r %s %s" % (apk_decode_path, apk_insert_path)
        print(cmd)
        os.system(cmd)
        return result.rstrip().split("\n")
    except subprocess.CalledProcessError:
        # no copy, since no pattern has been found.
        return None


# insert code segement at the beginning of the method
def _insert_at_beginning(insertion_file_path, decode_file_path, pattern, type):

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
                            method_local = _update_local(method_local, type)
                            method_body = method_body + line
                            added_part = _inserted_text(method_name, decode_file_path, type)
                            continue
                        else:  # case 1.2.1, others line, just directly append at method
                            method_body = method_body + line
                            continue
                else:  # case 2: is not in the middle of a method
                    if _is_method_start(line):  # case 2.1: method start line, get Default to print
                        method_name = _get_method_name(line)
                        method_head = line
                        is_buffer = True
                    else:
                        f_insertion_write.write(line)

    f_insertion_write.close()
    f_decode_read.close()


# insert code segement right after the patten line of code
def _insert_in_situ(insertion_file_path, decode_file_path, pattern, type):

    # method_body_before is the method lines before pattern line of code. including pattern line
    # method_body_after is the method lines after pattern line of code. 
    is_buffer = False
    found_pattern = False
    method_name = ""
    method_head, method_local, method_body_before, method_body_after, method_end = "", "", "", "", "" 
    added_part = ""

    with open(insertion_file_path, "w") as f_insertion_write:
        with open(decode_file_path, "r") as f_decode_read:
            for line in f_decode_read:
                # case 1: is in the middle of a method
                if is_buffer:
                    if _is_method_end(line):  # case 1.1, meet endline of a method
                        is_buffer = False
                        found_pattern = False
                        method_end = line
                        method = method_head \
                                 + method_local \
                                 + method_body_before \
                                 + added_part \
                                 + method_body_after \
                                 + method_end
                        f_insertion_write.write(method)
                        #  need to clean up the parameters
                        method_name = ""
                        method_head, method_local, method_body_before, method_body_after, method_end = "", "", "", "", ""
                        added_part = ""
                    else:  # case 1.2, in the body of a method
                        if CONST_PATTERN_LOCAL in line:  # case 1.2.1, find .local in method
                            method_local = line
                            continue
                        if pattern in line:  # if pattern detected, then insert code, otherwise, do not insert.
                            found_pattern = True
                            method_body_before = method_body_before + line
                            added_part, new_local = _inserted_text(method_name, decode_file_path, line, type)
                            method_local = _update_local(method_local, new_local)
                            continue
                        else:  # case 1.2.1, others line, just directly append at method
                            if found_pattern:
                                method_body_after = method_body_after + line
                            else:
                                method_body_before = method_body_before + line
                            continue
                else:  # case 2: is not in the middle of a method
                    if _is_method_start(line):  # case 2.1: method start line, get Default to print
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


def _update_local(old_local, new_local_num):
    # maximum register is v15, then local number will not exceed this amount
    pattern_local = ".locals "
    # get old number of local
    var_number = int(old_local[len(pattern_local) + old_local.find(pattern_local):])

    if new_local_num == 0:
        final_local = old_local
    else:
        if new_local_num > var_number:
            final_local = "    .locals " + str(new_local_num)
        else:
            final_local = old_local

    return final_local


def _get_invoke_first_arg(line):
    if ',' in line:
        var = line[line.find('{') + 1:line.find(',')]
    elif '...' in line:
        var = line[line.find('{') + 1:line.find(',')]
    else:
        var = ""
    return var


# return var1, var2 and new local number
def _get_vars(var):
    if 'p' in var:
        var1 = 'v0'
        var2 = 'v1'
        return var1, var2, 2
    elif 'v' in var:
        var_number = int(var[var.find('v') + 1:])
        if var_number == 1:
            var1 = 'v2'
            var2 = 'v3'
            return var1, var2, 4
        elif var_number == 2:
            var1 = 'v1'
            var2 = 'v3'
            return var1, var2, 4
        elif var_number == 0:
            var1 = 'v1'
            var2 = 'v2'
            return var1, var2, 3
        else:
            var1 = 'v1'
            var2 = 'v2'
            return var1, var2, 0


# insert Default and file path in each method.
# print text name with decode file path
def _inserted_text(method_name, decode_file_path, line, type):

    new_local = 0
    if type == "Default":

        text_to_be_added = "\n\
            const-string v1, \"Xue: print Default: \" \n\
            const-string v2, \"Xue: print Method Path: \" \n\
            const-string v3, \" %s \"\n\
            const-string v4, \" %s \" \n\
            invoke-static{v1, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n\
            invoke-static{v2, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n" % (
        method_name, decode_file_path)

    elif type == "EditText":
        edittext_var = _get_invoke_first_arg(line)
        var1, var2, new_local = _get_vars(edittext_var)
        if edittext_var == '':
            text_to_be_added = ''
        else:
    #         text_to_be_added = " \n\
    # invoke-virtual {%s}, Landroid/widget/EditText;->getHint()Ljava/lang/CharSequence; \n\
    # move-result-object %s \n\
    # invoke-virtual {%s}, Ljava/lang/CharSequence;->toString()Ljava/lang/String; \n\
    # move-result-object %s \n\
    # const-string %s, \"Print Hint: \" \n\
    # invoke-static{%s, %s}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n\
    # invoke-virtual {%s}, Landroid/widget/EditText;->getId()I \n\
    # move-result-object %s \n\
    # invoke-static {%s}, Ljava/lang/String;->valueOf(I)Ljava/lang/String; \n\
    # move-result-object %s \n\
    # const-string %s, \"Print Id: \" \n\
    # invoke-static{%s, %s}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n\
    # const-string %s, \"Print Default: \" \n\
    # const-string %s, \"%s\" \n\
    # invoke-static{%s, %s}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n" % (
    #             edittext_var, var1, var1, var1, var2, var2, var1,
    #             edittext_var, var1, var1, var1, var2, var2, var1,
    #             var1, var2, method_name, var1, var2)

            text_to_be_added = " \n\
            invoke-virtual {%s}, Landroid/widget/EditText;->getId()I \n\
            move-result-object %s \n\
            invoke-static {%s}, Ljava/lang/String;->valueOf(I)Ljava/lang/String; \n\
            move-result-object %s \n\
            const-string %s, \"Print Id: \" \n\
            invoke-static{%s, %s}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n\
            const-string %s, \"Print Method Name: \" \n\
            const-string %s, \"%s\" \n\
            invoke-static{%s, %s}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I \n" % (
        edittext_var, var1, var1, var1, var2, var2, var1,
        var1, var2, method_name, var1, var2)
    else:
        text_to_be_added = ""

    return text_to_be_added, new_local

