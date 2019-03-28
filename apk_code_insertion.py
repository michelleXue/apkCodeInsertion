import core as core

PATTERN = "Landroid/widget/EditText;->addTextChangedListener(Landroid/text/TextWatcher;)V"
PATTERN_LOCAL = ".local"
DECODE_PATH = ""
ORIGIN_PATH = ""
INSERT_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/insertions/"
KEY_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/keys/"
REBUILD_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/rebuild_apks/"
ASSIGNED_PATH = "/Users/xue/Documents/Research/InputGeneration/apkAnalysis/signed_apks/"


apk_list_path = core.apks_list_gen.apks_list_gen(ORIGIN_PATH)
# decode the apk files
core.decode.decode_apk(ORIGIN_PATH, DECODE_PATH)
# filter and insert
core.filter_and_insert.filter_and_insert_apk(DECODE_PATH, INSERT_PATH, apk_list_path, PATTERN)
# rebuild apks
core.rebuild.rebuild_apk(REBUILD_PATH, INSERT_PATH)
# key generation
core.key.key_gen(KEY_PATH, apk_list_path)
# assign key and ready to install
