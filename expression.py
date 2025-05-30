import os
import sys
import argparse
from pathlib import Path
from modules import *

VERSION = "v1.0.0"

def run_aggr(args) :
    exp_aggr(args)

def run_indivi(args) :
    exp_ind(args)

def main():

    if '--help' in sys.argv or '-h' in sys.argv:
        print(f"version: {VERSION}")

    parser = argparse.ArgumentParser(
        description="Create a list of expression amount values."
    )
    parser.add_argument('--version','-v', action='version', version=f'%(prog)s {VERSION}')
    subparsers = parser.add_subparsers(dest="command", required=True)

    # aggregation
    parser_ag = subparsers.add_parser("batch",  aliases=['BH'], help="Create a list of expression values for the batch.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_ag.add_argument("--flowcellid","-fc", required=True, help="flowcell id")
    parser_ag.add_argument("--inclusion","-i", required=False, help="sample IDs to include (comma separated)", default="")
    parser_ag.add_argument("--exclusion","-e", required=False, help="sample IDs to exclude (comma separated)", default="")
    parser_ag.add_argument("--genelist","-g", required=False, help="genes list", default="")
    parser_ag.add_argument("--data_type","-t", required=False, help="where each simulated read comes from.", default="gene", choices=["gene","isoform"])
    parser_ag.add_argument("--directory","-d", required=False, help="parent analytical directory", default="/data1/data/result")
    parser_ag.add_argument("--outdir","-o", required=False, help="output directory path", default="/data1/work/expression")
    parser_ag.set_defaults(func=run_aggr)

    # individual
    parser_id = subparsers.add_parser("individual",  aliases=['IND'], help="Specify samples and genes (small scale).", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_id.add_argument("--sample","-s", required=True, help="Sample ID (comma separated)")
    parser_id.add_argument("--gene","-g", required=True, help="genes (comma separated)")
    parser_id.add_argument("--data_type","-t", required=False, help="where each simulated read comes from.", default="gene", choices=["gene","isoform"])
    parser_id.add_argument("--directory","-d", required=False, help="parent analytical directory", default="/data1/data/result")
    parser_id.add_argument("--outfile","-o", required=False, help="output file path", default="/data1/work/expression/expression.xlsx")
    parser_id.set_defaults(func=run_indivi)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":

    main()


