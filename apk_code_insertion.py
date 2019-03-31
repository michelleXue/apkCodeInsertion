import core as core

PATTERN = "Landroid/widget/EditText;->addTextChangedListener(Landroid/text/TextWatcher;)V"
PATTERN_LOCAL = ".local"
DECODE_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/decoded/"
ORIGIN_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/origin/"
INSERT_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/insertion/"
KEY_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/keys/"
REBUILD_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/rebuild/"
ASSIGNED_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/signed/"


apk_list_path_origin = core.apks_list_gen.apk_name_gen(ORIGIN_PATH)
# decode the apk files
core.decode.decode_apk(ORIGIN_PATH, DECODE_PATH)
# filter and insert
core.filter_and_insert.filter_and_insert_apk(DECODE_PATH, INSERT_PATH, apk_list_path_origin, PATTERN)
# rebuild apks
core.rebuild.rebuild_apk(REBUILD_PATH, INSERT_PATH)
# key generation
core.key.key_gen(KEY_PATH, REBUILD_PATH)
# assign key and ready to install
core.assign.assign_key_to_apk(KEY_PATH, ASSIGNED_PATH, REBUILD_PATH)
