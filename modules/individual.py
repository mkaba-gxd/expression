import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from .common import *

def search_sample(samples) :
    query = f"""
    SELECT tesh.run_id, concat(tesh.equip_side, tesh.fc_id) AS sub_name, gp.PRJ_TYPE, gp.SAMPLE_ID
    FROM gxd.tb_expr_seq_header tesh
    INNER JOIN gxd.gc_qc_sample gqs
    ON tesh.run_id = gqs.run_id
    INNER JOIN gxd.gc_project gp
    ON gqs.SAMPLE_ID = gp.SAMPLE_ID
    INNER JOIN gxd.gc_history_log ghl
    ON gqs.SAMPLE_ID = ghl.SAMPLE_ID
    AND ghl.idx = (SELECT MAX(idx) FROM gc_history_log WHERE SAMPLE_ID = gqs.SAMPLE_ID)
    WHERE gp.SAMPLE_ID IN({samples})
    """
    return query


def exp_ind(args) :
    
    samples = [x.strip() for x in args.sample.split(',') if not x.strip() == '']
    genes = [x.strip() for x in args.gene.split(',') if not x.strip() == '']
    data_type = args.data_type
    directory = args.directory
    outfile = os.path.abspath(args.outfile)
    merge_data = None

    if len(samples) == 0 or len(genes) == 0 : init('wrong argument.')

    df_info = getinfo(search_sample( "'" + "\',\'".join(samples) + "'" ))
    df_info = df_info[ df_info['PRJ_TYPE']=='WTS' ]

    if df_info.shape[0] == 0 : init('All samples are not in the database.')

    lost = list(set(samples) - set(df_info['SAMPLE_ID'].to_list()))
    if len(lost) > 0: print('not registered in the database: ' + ",".join(lost))

    uniq_info = fcDir_table(df_info, directory)
    if uniq_info.shape[0] == 0: init()

    df_info = pd.merge(df_info, uniq_info, on=['sub_name','PRJ_TYPE'])

    for i, item in df_info.iterrows() :

        anal_dir = os.path.join(directory, item['PRJ_TYPE'], item['seqDir'], item['SAMPLE_ID'])
        if data_type == 'gene' :
            file = os.path.join(anal_dir, 'Expression', 'RSEM', item['SAMPLE_ID']+'.genes.results')
            use_colums = ['ENSG_ID','gene_name','length','effective_length','expected_count','TPM','FPKM']
        elif data_type == 'isoform' :
            file = exp_isform = os.path.join(anal_dir, 'Expression', 'RSEM', item['SAMPLE_ID']+'.isoforms.results')
            use_colums = ['ENST_ID','gene_name','length','effective_length','expected_count','TPM','FPKM']

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

        match_genes = list(set(data['gene_name']) & set(genes))
        lost_genes = list(set(genes) - set(data['gene_name']))
        if len(match_genes) == 0 :
            print(item['SAMPLE_ID'] + ' : there are no applicable genes.')
            continue
        if len(lost_genes) > 0 :
            print(item['SAMPLE_ID'] + ': some genes do not apply. ' + ','.join(lost_genes))

        data = data[data['gene_name'].isin(genes)]
        data.insert(0, 'sample_id', item['SAMPLE_ID'])
        if merge_data is None :
            merge_data = data
        else :
            merge_data = pd.concat([merge_data, data], axis=0)

    if not merge_data is None :
        if os.path.isfile(outfile) :
            choice = prompt_choice("Output file exists. Do you want to append/overwrite? (yes[Y]/no[N]): ", ['yes', 'y', 'no', 'n'])
            if choice in ['no', 'n']:
                 init('Suspend operation.')

        if not os.path.isdir(os.path.dirname(outfile)) :
             os.makedirs(os.path.dirname(outfile), exist_ok=True)

        try :
            with pd.ExcelWriter(outfile, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer :
                merge_data.to_excel(writer, sheet_name=data_type, index=False)
        except FileNotFoundError:
            with pd.ExcelWriter(outfile, engine="openpyxl") as writer :
                merge_data.to_excel(writer, sheet_name=data_type, index=False)


