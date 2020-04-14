import json
import requests
from datetime import datetime
from diskcache import Cache
import pandas as pd
from tqdm import tqdm
import os
from private_keys import api_keys
# from PyPDF2 import PdfFileWriter, PdfFileReader

START = datetime(2016,1,1) # year, month, day as integers
END = datetime(2017,12,31)

def params_unique_combination(baseurl,params,private_keys=['data_gov_key']):
    kvs = []
    alpha_keys = sorted(params.keys())
    for k in alpha_keys:
        if k not in private_keys:
            kvs.append('{}-{}'.format(k, params[k]))
    return baseurl + '_'.join(kvs)

def request_json(baseurl,params={}):
    uid = params_unique_combination(baseurl,params)
    with Cache('cache') as ref:
        if uid in ref:
            return ref.get(uid)
        else:
            response = requests.get(baseurl,params)
            try:
                data = json.loads(response.text)
            except:
                data = response
            ref.set(uid,data)
            return data

def request_and_save_pdf(baseurl,params,out_dir,filename):
    response = requests.get(baseurl,params)
    with open(out_dir+'/'+filename, 'wb') as outfile:
        outfile.write(response.content)
        # print('Success')

def request_and_save_mods(baseurl,params,out_dir,filename):
    response = requests.get(baseurl,params)
    with open(out_dir+'/'+filename, 'wb') as outfile:
        outfile.write(response.content)

def get_out_dir():
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    dir_name = "outputs/batch-" + ts

    if not os.path.exists("outputs"):
        os.mkdir("outputs")

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    return dir_name

def get_cr_metadata(start, end):

    range = pd.date_range(start, end)
    out_dir = get_out_dir()

    for d in tqdm(range):

        packageId = f'CREC-{d.year}-{str(d.month).zfill(2)}-{str(d.day).zfill(2)}'

        try:
            base = f'https://api.govinfo.gov/packages/{packageId}/summary'
            params = {"api_key" : api_keys["data_gov_key"]}
            data = request_json(base, params)
            if "message" in data.keys():
                print(base)
                print(data['message'][:50])
                print('\n')
            else:
                with open(out_dir +'/'+ f'{packageId}.json', 'w') as outfile:
                    json.dump(data, outfile, indent=2)
                pdf_base = data['download']['pdfLink']
                # request_and_save_pdf(pdf_base, params, out_dir, f'{packageId}.pdf')
                mods_base = data['download']['modsLink']
                request_and_save_mods(mods_base, params, out_dir, f'{packageId}.xml')

        except:
            print('Something happened with',packageId)

if __name__ == "__main__":
    get_cr_metadata(START, END)
