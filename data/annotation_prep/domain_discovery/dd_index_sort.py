from __future__ import print_function
import smart_open
import boto
import json
import gzip
import argparse

nyu_keys = ['nyu-ddindex-fall2016qpr-cdr-deduped.gz']

jpl_keys = ['jpl-dd-index-corrected.gz']

hg_keys = [u'hg_0037925d0d0c_items_deduped.jl.gz',
 u'hg_03dc0ca4fc58_items_deduped.jl.gz',
 u'hg_043492dce16d_items_deduped.jl.gz',
 u'hg_05543b85e404_items_deduped.jl.gz',
 u'hg_0a813cf5effc_items_deduped.jl.gz',
 u'hg_0cc657f0f82f_items_deduped.jl.gz',
 u'hg_1361cf21721a_items_deduped.jl.gz',
 u'hg_171c2a0db5f4_items_deduped.jl.gz',
 u'hg_187f84e8b3e7_items_deduped.jl.gz',
 u'hg_19a299e0a65a_items_dedupe_fixed.jl.gz',
 u'hg_1a4d5162f4d1_items_dedupe.jl.gz',
 u'hg_1b547c4e588a_items_deduped.jl.gz',
 u'hg_1fa5611c3e38_items_deduped.jl.gz',
 u'hg_2ffe62142c65_items_deduped.jl.gz',
 u'hg_3d62a784adee_items_deduped.jl.gz',
 u'hg_43f23a06cdbb_items_deduped.jl.gz',
 u'hg_49cc2d4b103b_items_deduped.jl.gz',
 u'hg_527f7b8f482c_items_deduped.jl.gz',
 u'hg_563f2079be40_items_deduped.jl.gz',
 u'hg_5d1f7750b216_items_deduped.jl.gz',
 u'hg_5f4ead52fd9f_items_deduped.jl.gz',
 u'hg_60326a8d93b2_items_deduped.jl.gz',
 u'hg_65ace84577ae_items_deduped.jl.gz',
 u'hg_681307ea872d_items_deduped.jl.gz',
 u'hg_6a168e0930b5_items_deduped.jl.gz',
 u'hg_6bab44eb0f10_items_deduped.jl.gz',
 u'hg_77a2afbf64fd_items_dedupe.jl.gz',
 u'hg_7a7b9f457473_items_deduped.jl.gz',
 u'hg_81338607b19f_items_deduped.jl.gz',
 u'hg_82f141f26429_items_dedupe.jl.gz',
 u'hg_82fc64dc8c41_items_deduped.jl.gz',
 u'hg_835e8d336a91_items_deduped.jl.gz',
 u'hg_844078a3470c_items_deduped.jl.gz',
 u'hg_8737ba37d9fd_items_deduped.jl.gz',
 u'hg_91b6b9e87aff_items_deduped.jl.gz',
 u'hg_9776ef1d86fd_items_deduped.jl.gz',
 u'hg_9e17c10b20ce_items_deduped.jl.gz',
 u'hg_9e37412e2ad4_items_deduped.jl.gz',
 u'hg_a2f1b461f9b9_items_deduped.jl.gz',
 u'hg_a8f015b18bb6_items_deduped.jl.gz',
 u'hg_aggr_1_6_2_items_0_dedupe.jl.gz',
 u'hg_aggr_1_6_2_items_1_dedupe.jl.gz',
 u'hg_aggr_1_6_2_items_2_dedupe.jl.gz',
 u'hg_aggr_1_6_2_items_3_dedupe_fixed.jl.gz',
 u'hg_b12a5c417820_items_deduped.jl.gz',
 u'hg_b5465f9f493a_items_deduped.jl.gz',
 u'hg_be6729dc656b_items_deduped.jl.gz',
 u'hg_c44af01d4bdd_items_deduped.jl.gz',
 u'hg_c49c6f113963_items_deduped.jl.gz',
 u'hg_c53da6903eca_items_deduped.jl.gz',
 u'hg_d80d213a2219_items_deduped.jl.gz',
 u'hg_dbd48f133da7_items_deduped.jl.gz',
 u'hg_dd4373a79845_items_deduped.jl.gz',
 u'hg_e71e039adf22_items_deduped.jl.gz',
 u'hg_ee9e1732e9be_items_deduped.jl.gz',
 u'hg_f0624e91c930_items_deduped.jl.gz',
 u'hg_f8054ee2fdfb_items_deduped_fixed.jl.gz',
 u'hg_fcbaae09eebf_items_deduped.jl.gz',
 u'hg_fd1ec80fa726_items_deduped.jl.gz',
 u'hg_ff60e33ea268_items_deduped.jl.gz',
 u'hg_files-top-50.jl.gz',
 u'hg_items-fixed-deduped-deep-deep-urls-1468287374.jl.gz',
 u'hg_items-fixed-deduped-deep-deep-urls-1468447284.jl.gz',
 u'hg_mk_try1_0cf94ddb7544_items_deduped.jl.gz',
 u'hg_mk_try1_24c75243bea4_items_deduped.jl.gz',
 u'hg_mk_try1_39833f809736_items_deduped.jl.gz',
 u'hg_mk_try1_5e7cca4e1fa7_items_deduped.jl.gz',
 u'hg_mk_try1_6002556977ec_items_deduped.jl.gz',
 u'hg_mk_try1_6d4931440c0c_items_deduped.jl.gz',
 u'hg_mk_try1_7172c8ae746f_items_deduped.jl.gz',
 u'hg_mk_try1_e31260e05990_items_deduped.jl.gz',
 u'hg_mk_try1_eaf10d20045a_items_deduped.jl.gz',
 u'hg_mk_try2_186faddee614_items_deduped.jl.gz',
 u'hg_mk_try2_2dfe4d7db7e0_items_deduped.jl.gz',
 u'hg_mk_try2_37480b552676_items_deduped.jl.gz',
 u'hg_mk_try2_5c2b9f817e53_items_deduped.jl.gz',
 u'hg_mk_try2_5cd382d1b525_items_deduped.jl.gz',
 u'hg_mk_try2_5fec4fccf55b_items_deduped.jl.gz',
 u'hg_mk_try2_629b7d6d265b_items_deduped.jl.gz',
 u'hg_mk_try2_96f9226967c8_items_deduped.jl.gz',
 u'hg_mk_try3_115aaccb630b_items_deduped.jl.gz',
 u'hg_mk_try3_34d8344f3901_items_deduped.jl.gz',
 u'hg_mk_try3_5b0f5e98e41a_items_deduped.jl.gz',
 u'hg_mk_try3_62dfa1308b14_items_deduped.jl.gz',
 u'hg_mk_try3_76eb772d06bc_items_deduped.jl.gz',
 u'hg_mk_try3_85d623edfa8f_items_deduped.jl.gz',
 u'hg_mk_try3_8a0516caca44_items_deduped.jl.gz',
 u'hg_mk_try3_f5be0c325ea4_items_deduped.jl.gz',
 u'hg_mk_try4_0444795255ab_items_deduped.jl.gz',
 u'hg_mk_try4_7c754c2284d7_items_deduped.jl.gz',
 u'hg_mk_try4_87b115138e48_items_deduped.jl.gz',
 u'hg_mk_try4_89e2ea9985d6_items_deduped.jl.gz',
 u'hg_mk_try4_a820aece54c9_items_deduped.jl.gz',
 u'hg_mk_try4_c45233adff05_items_deduped.jl.gz',
 u'hg_mk_try4_d1f0c127c9ea_items_deduped.jl.gz',
 u'hg_mk_try4_f49ce10ec538_items_deduped.jl.gz',
 u'hg_mk_try5_19d7b4e973d4_items_deduped.jl.gz',
 u'hg_mk_try5_1ff573aed6e1_items_deduped.jl.gz',
 u'hg_mk_try5_23d90802c26a_items_deduped.jl.gz',
 u'hg_mk_try5_3af14eeded45_items_deduped.jl.gz',
 u'hg_mk_try5_5473bb0b49cf_items_deduped.jl.gz',
 u'hg_mk_try5_6420b36da47e_items_deduped.jl.gz',
 u'hg_mk_try5_6803b3016684_items_deduped.jl.gz',
 u'hg_mk_try5_6e79957bfb4c_items_deduped.jl.gz',
 u'hg_mk_try5_7c2486b65711_items_deduped.jl.gz',
 u'hg_mk_try5_824dbeeb18e8_items_deduped.jl.gz',
 u'hg_mk_try5_8e6c54febc9a_items_deduped.jl.gz',
 u'hg_mk_try5_933bde4911db_items_deduped.jl.gz',
 u'hg_mk_try5_9c78a08ee80b_items_deduped.jl.gz',
 u'hg_mk_try5_abd09ead812c_items_deduped.jl.gz',
 u'hg_mk_try5_c1d1f320e939_items_deduped.jl.gz',
 u'hg_mk_try5_c3101a32fba7_items_deduped.jl.gz',
 u'hg_try_2_1k_234ff915ac40_items_deduped.jl.gz',
 u'hg_try_2_1k_5d9a5e67689b_items_deduped.jl.gz',
 u'hg_try_2_1k_632c0f6347d1_items_deduped.jl.gz',
 u'hg_try_2_1k_88069ea8dfb9_items_deduped.jl.gz',
 u'hg_try_2_1k_b1f79e326eec_items_deduped.jl.gz',
 u'hg_try_2_1k_d4742513d576_items_deduped.jl.gz',
 u'hg_try_5_1a0803eb3895_items_deduped.jl.gz',
 u'hg_try_5_3438c921200e_items_deduped.jl.gz',
 u'hg_try_5_60763d9308bf_items_deduped.jl.gz',
 u'hg_try_5_6436846f8a9e_items_deduped.jl.gz',
 u'hg_try_5_b7174f1678a4_items_deduped.jl.gz',
 u'hg_try_5_b837b2a80c5f_items_deduped.jl.gz',
 u'hg_try_5_bf8ff669902e_items_deduped.jl.gz',
 u'hg_try_5_d0023fb033f4_items_deduped.jl.gz',
 u'hg_try_5_d0b79a1775a8_items_deduped.jl.gz',
 u'hg_try_5_f9e0a70b805f_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_30d0f7166318_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_36de4b2c998e_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_5d721c6eb37c_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_6a6c648ef93d_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_75430c98be57_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_984d662abe48_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_9981d8733a55_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_d90f073ae9e6_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_e9f3ccded985_items_deduped.jl.gz',
 u'hg_try_alexa_10k_09_f00a34cddc9e_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_13684e8ddd4b_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_1468562b6d29_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_54dcc0717192_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_60d095907206_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_7e8dbbbe86e5_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_a05946b26859_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_be16318d8dc4_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_c400255a6692_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_cedc53498c1e_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_2_da3c6ee1eeb6_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_3_1f3f088fb55f_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_3_636ab950c3ad_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_3_74d22d6c2743_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_3_899b81d0b10a_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_3_a2ec16f0d317_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_3_d48d5919dbd6_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_2437abf7f555_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_2c05447f5b1a_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_38328c1de58b_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_413b17b1f20c_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_6f6398bb2fc9_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_9988f2e5b9c1_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_e96075eae066_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_eead14527d2d_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_f2f73feb35ce_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_10k_4_f64266f36867_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_12b8735eaafa_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_27051b29c9fc_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_596f0c2e3171_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_73f132ef0b14_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_777c4216f1ac_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_7e572a09bbdb_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_d26b112769e5_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_ed14a4d2f4bf_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_f5880891cb88_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_15k_fab90e7624a9_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_8b4e85450893_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_9c338ac6c1f8_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_a739372eccf8_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_b8817309bfdb_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_c57767923e0c_items_deduped.jl.gz',
 u'hg_try_exp_max_domains_eafc1432c220_items_deduped.jl.gz']

def process_key(_key, s3_key, s3_secret, index):
    key = boto.connect_s3(aws_access_key_id=s3_key, aws_secret_access_key=s3_secret).get_bucket("memex-fall2016-qpr").get_key(_key)
    with smart_open.smart_open(key) as f:
        for line in f:
            try:
                doc = json.loads(line.split('\n')[0])
                _id = doc.get('_id')
                if _id in _id_set:
                    with gzip.open(index + '_sorted_jsonl.gz','a') as f:
                        f.write(json.dumps(doc)+'\n')
            except Exception as e:
                print(str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", help="either nyu, jpl, or hg")
    parser.add_argument("--s3_key", help="aws access key")
    parser.add_argument("--s3_secret", help="aws secret key")

    args = parser.parse_args()

    f = open(args.index + '_dd_ids.txt','r').read()
    _ids = [i for i in f.split('\n') if i != '']
    _id_set = frozenset(_ids)

    if args.index == 'hg':
        for _key in hg_keys:
            print('Operating on {0}: {1}'.format(args.index,_key))
            process_key(_key, args.s3_key, args.s3_secret, args.index)
    
    if args.index == 'nyu':
        for _key in nyu_keys:
            print('Operating on {0}: {1}'.format(args.index,_key))
            process_key(_key, args.s3_key, args.s3_secret, args.index)
            
    if args.index == 'jpl':
            for _key in jpl_keys:
                print('Operating on {0}: {1}'.format(args.index,_key))
                process_key(_key, args.s3_key, args.s3_secret, args.index)