import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from .common import *

def exp_aggr(args):

    flowcellid = args.flowcellid
    data_type = args.data_type
    directory = args.directory
    outdir = args.outdir
    gene_path = args.genelist
    inclusion = [x.strip() for x in args.inclusion.split(',') if not x.strip() == '']
    exclusion = [x.strip() for x in args.exclusion.split(',') if not x.strip() == '']

    if gene_path is not None :

        if os.path.isfile(gene_path) :
            with open(gene_path, 'r') as file:
                genes = [line.strip() for line in file if line.strip()]
        else:
            print("The specified file does not exist.")
            print("Do you want to continue? (Y/N): ", end='', flush=True)
            rlist, _, _ = select.select([sys.stdin], [], [], 60)
            if rlist :
                answer = sys.stdin.readline().strip().lower()
                if answer in ['y','yes']:
                    genes = []
                elif answer in ['n', 'no']:
                    init("Process aborted by the user.")
                else:
                    init("Invalid input. Process aborted.")
    else:
        genes = []

    if len(inclusion) > 0 and len(exclusion) > 0:
        init('ERROR: Inclusion and exclusion cannot be specified simultaneously.')

    df_info = getinfo(SelectData(flowcellid))
    if df_info.shape[0] == 0 : init()

    if len(inclusion) > 0:
        print ("inclusion sample:" + "\n".join(inclusion))
        df_info = df_info[ df_info['SAMPLE_ID'].isin(inclusion)]
        if df_info.shape[0] == 0 : init("No corresponding sample IDs.")

    if len(exclusion) > 0:
        print ("exclusion sample:" + ",".join(exclusion))
        df_info = df_info[ ~df_info['SAMPLE_ID'].isin(exclusion)]
        if df_info.shape[0] == 0 : init("No corresponding sample IDs.")

    df_info = df_info[ df_info['PRJ_TYPE'] == "WTS" ]
    if df_info.shape[0] == 0 : init("Test type error: no sample ID corresponds.")

    df_info = df_info[~df_info['SAMPLE_ID'].str.contains('_PCE_|_NCE_|_PCT_|_NCT_', regex=True, na=False)]
    if df_info.shape[0] == 0 : init("No clinical specimens match the criteria.")

    uniq_info = fcDir_table(df_info, directory)
    if uniq_info.shape[0] == 0: init()

    df_info = pd.merge(df_info, uniq_info, on=['sub_name','PRJ_TYPE'])
    anal_dir = os.path.join(directory,"WTS",df_info['seqDir'][0])
    out_folder = os.path.join(outdir, df_info['seqDir'][0])

    if os.path.isdir(out_folder) : shutil.rmtree(out_folder)
    os.makedirs(out_folder, exist_ok=True)

    for i, item in df_info.iterrows() :
        if data_type == 'gene' :
            file = os.path.join(anal_dir, item['SAMPLE_ID'], 'Expression', 'RSEM', item['SAMPLE_ID']+'.genes.results')
        elif data_type == 'isoform' :
            file = os.path.join(anal_dir, item['SAMPLE_ID'], 'Expression', 'RSEM', item['SAMPLE_ID']+'.isoforms.results')

        if not os.path.isfile(file):
            print('file not exists: ' + file)
            continue

        data = pd.read_csv(file, header=0, sep="\t")
        data['gene_name'] = data['gene_id'].str.split('_').str[1]
        if data_type == 'gene' :
            data['ENSG_ID'] = data['gene_id'].str.split('.').str[0]
            data = data[['ENSG_ID','gene_name','length','effective_length','expected_count','TPM','FPKM']]
        elif data_type == 'isoform' :
            data['ENST_ID'] = data['transcript_id'].str.split('.').str[0]
            data = data[['ENST_ID','gene_name','length','effective_length','expected_count','TPM','FPKM']]

        if len(genes) > 0 :
            match_genes = list(set(data['gene_name']) & set(genes))
            if len(match_genes) == 0:
                print("All listed genes are not included in the analysis. Write down all genes.")
            else:
                data = data[data['gene_name'].isin(match_genes)]

        data.to_csv(os.path.join(outdir, df_info['seqDir'][0], '.'.join([item['SAMPLE_ID'],data_type,'csv'])), header=True, index=False)


