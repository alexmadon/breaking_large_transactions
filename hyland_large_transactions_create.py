#!/usr/bin/env python3
import argparse
import json

import requests


def get_headers(opts):
    headers={}
    headers['Content-Type']='application/json'
    headers['Authorization']='Basic YWRtaW46YWRtaW4='
    return headers

def process_response(r):
    print("r",r)
    print("r.status_code",r.status_code)
    print("r.content",r.content)
    if len(r.content):
        rjson=r.json()
        print("rjson",json.dumps(rjson,indent=4))
    else:
        print("Status:",r.status_code)
        rjson=''
    return rjson

def do_post(url,data):
    r = requests.post(
        url,
        data=json.dumps(data),
        headers=get_headers(opts)
    )
    r=process_response(r)
    return r

def do_put(url,data):
    r = requests.put(
        url,
        data=json.dumps(data),
        headers=get_headers(opts)
    )
    r=process_response(r)
    return r

def do_get(url):
    r = requests.get(
        url,
        headers=get_headers(opts)
    )
    r=process_response(r)
    return r

def do_delete(url):
    r = requests.delete(
        url,
        headers=get_headers(opts)
    )
    r=process_response(r)
    return r

def create_folders(opts):
    """
    Create several folders in one transaction.
    as per the doc at: https://docs.alfresco.com/content-services/latest/develop/rest-api-guide/#creating-multiple-entities-items
    """
    url='http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-shared-/children'
    folders=[]
    foldernb=100
    for i in range(0,foldernb):
        folder={
            "nodeType":"cm:folder",
            "name":"Folder "+"{:04}".format(i),
            "properties":{
                "cm:title":"",
                "cm:description":""
            }
        }
        folders.append(folder)
        
    r=do_post(url,folders)
    return r


def list_folders(opts):
    url='http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-shared-/children'
    r=do_get(url)
    return r


def update_folders(opts):
    """
    Update several folders one by one (not batch as REST PUT API doesn't allow that)
    """
    r=list_folders(opts)
    print("rlist",json.dumps(r,indent=4))
    entries=r["list"]["entries"]
    
    
    for i,entry in enumerate(entries):
        folderid=entry['entry']['id']

        folder={
            # "nodeType":"cm:folder",
            # "name":"Folder "+"{:04}".format(i),
            "properties":{
                "cm:title":"",
                "cm:description":"updated description"
            }
        }
        url='http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/'+folderid
    
        r=do_put(url,folder)

def main(opts):
    if opts.createfolders:
        create_folders(opts)
    elif opts.updatefolders:
        update_folders(opts)
    else:
        print("Nothing to do")

def parse_cli():
    parser = argparse.ArgumentParser(description="""TOOL DESCRIPTION
A tool to create large transactions.
Then break them, then look at behaviour in FULL reindex.

  select  id,version,store_id, uuid, transaction_id  from alf_node order by id;
  
acs2332pgslr=# select transaction_id,count(transaction_id) from alf_node group by transaction_id order by transaction_id;
 transaction_id | count 
----------------+-------
              1 |     3
              2 |     3
              3 |     1
              4 |     1
              5 |     1
              6 |   566
              9 |     1
             10 |     1
             11 |   143
             12 |     1
             13 |     3
             14 |     1
             15 |   130
             16 |     1
             17 |     1
             18 |     1
             19 |     1
             20 |   100
             21 |     1
(19 rows)

acs2332pgslr=# select transaction_id,count(transaction_id),json_agg(id) from alf_node group by transaction_id order by transaction_id;

                 20 |   100 | [862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961]

select transaction_id,count(transaction_id),json_agg(alf_node.*) as ids from alf_node group by transaction_id order by transaction_id;

    with t1 as (select id,transaction_id,version from alf_node) select transaction_id,count(transaction_id),json_agg(t1.*) from t1 group by transaction_id order by transaction_id;

with t1 as (select id,transaction_id,version from alf_node), t2 as (select transaction_id,count(transaction_id),json_agg(t1.*) from t1 group by transaction_id order by transaction_id) select json_agg(t2) FROM t2;

psql -qAtX -c "with t1 as (select id,transaction_id,version from alf_node), t2 as (select transaction_id,count(transaction_id),json_agg(t1.*) from t1 group by transaction_id order by transaction_id) select json_agg(t2) FROM t2;" acs2332pgslr
    
AFTER UPDATE
    
psql -c 'select transaction_id,count(transaction_id) from alf_node group by transaction_id order by transaction_id;' acs2332pgslr

transaction_id | count 
----------------+-------
              1 |     3
              2 |     3
              3 |     1
              4 |     1
              5 |     1
              6 |   566
              9 |     1
             10 |     1
             11 |   143
             12 |     1
             13 |     3
             14 |     1
             15 |   130
             16 |     1
             17 |     1
             18 |     1
             19 |     1
             21 |     1
             24 |     1
             25 |     1
             26 |     1
             27 |     1
             28 |     1
             29 |     1
             30 |     1
             31 |     1
             32 |     1
             33 |     1
             34 |     1
             35 |     1
             36 |     1
             37 |     1
             38 |     1
             39 |     1
             40 |     1
             41 |     1
             42 |     1
             43 |     1
             44 |     1
             45 |     1
             46 |     1
             47 |     1
             48 |     1
             49 |     1
             50 |     1
             51 |     1
             52 |     1
             53 |     1
             54 |     1
             55 |     1
             56 |     1
             57 |     1
             58 |     1
             59 |     1
             60 |     1
             61 |     1
             62 |     1
             63 |     1
             64 |     1
             65 |     1
             66 |     1
             67 |     1
             68 |     1
             69 |     1
             70 |     1
             71 |     1
             72 |     1
             73 |     1
             74 |     1
             75 |     1
             76 |     1
             77 |     1
             78 |     1
             79 |     1
             80 |     1
             81 |     1
             82 |     1
             83 |     1
             84 |     1
             85 |     1
             86 |     1
             87 |     1
             88 |     1
             89 |     1
             90 |     1
             91 |     1
             92 |     1
             93 |     1
             94 |     1
             95 |     1
             96 |     1
             97 |     1
             98 |     1
             99 |     1
            100 |     1
            101 |     1
            102 |     1
            103 |     1
            104 |     1
            105 |     1
            106 |     1
            107 |     1
            108 |     1
            109 |     1
            110 |     1
            111 |     1
            112 |     1
            113 |     1
            114 |     1
            115 |     1
            116 |     1
            117 |     1
            118 |     1
            119 |     1
            120 |     1
            121 |     1
            122 |     1
            123 |     1
(118 rows)


select id,version, transaction_id from alf_node order by id;



    
""", # formatter_class=argparse.RawTextHelpFormatter)
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c','--createfolders', help="Create folders",action="store_true")
    parser.add_argument('-u','--updatefolders', help="Update folders",action="store_true")
    opts = parser.parse_args()
    return opts

if __name__ == "__main__":
    opts=parse_cli()
    main(opts)
