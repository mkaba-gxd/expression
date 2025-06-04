# expression
WTS 解析工程で作成される発現量値をファイル出力する

| command        | 概要                                               |
|:---------------|:---------------------------------------------------|
|batch, BC       |指定のバッチで解析された発現量値を検体別に出力する  |
|individual, IND |検体番号と遺伝子を指定して発現量値一覧を作成する    |

## 変数の定義(共通)
```bash
img=/data1/labTools/labTools.sif
SCRIPT=/data1/labTools/expression/latest/expression.py
```

## マニュアルの表示
全体の概要表示
```bash
$ singularity exec --bind /data1 $img python $SCRIPT --help
version: v1.0.0
usage: expression.py [-h] [--version] {batch,BC,individual,IND} ...

Create an expression value file for each specimen in the relevant batch.

positional arguments:
  {batch,BC,individual,IND}
    batch (BC)          Create a list of expression values for the batch.
    individual (IND)    Specify samples and genes (small scale).

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
```
コマンド別の詳細表示
```
singularity exec --bind /data1 $img python $SCRIPT <command> --help
```

## 1\. バッチ単位で処理
flowce IDを指定して、該当するバッチに含まれる検体毎に発現量値一覧のcsvファイルを作成する。
```
singularity exec --bind /data1 $img python $SCRIPT batch -fc <flowcellid>
singularity exec --bind /data1 $img python $SCRIPT BC -fc <flowcellid>
```
### オプションの詳細
```
$ singularity exec --bind /data1 $img python $SCRIPT batch --help
version: v1.0.0
usage: expression.py batch [-h] --flowcellid FLOWCELLID [--inclusion INCLUSION] [--exclusion EXCLUSION] [--genelist GENELIST]
                           [--data_type {gene,isoform}] [--directory DIRECTORY] [--outdir OUTDIR]

optional arguments:
  -h, --help            show this help message and exit
  --flowcellid FLOWCELLID, -fc FLOWCELLID
                        flowcell id (default: None)
  --inclusion INCLUSION, -i INCLUSION
                        sample IDs to include (comma separated) (default: )
  --exclusion EXCLUSION, -e EXCLUSION
                        sample IDs to exclude (comma separated) (default: )
  --genelist GENELIST, -g GENELIST
                        genes list (default: )
  --data_type {gene,isoform}, -t {gene,isoform}
                        where each simulated read comes from. (default: gene)
  --directory DIRECTORY, -d DIRECTORY
                        parent analytical directory (default: /data1/data/result)
  --outdir OUTDIR, -o OUTDIR
                        output directory path (default: /data1/work/expression)
```
| option          | required | 概要          |default         |
|:----------------|:---------|:--------------|:---------------|
|--flowcellid/-fc |True      |flowcel ID     |None            |
|--inclusion/-i   |False     |除外するSample IDを指定。カンマ区切りで複数指定可能         |None |
|--exclusion/-e   |False     |アップロードするSample IDを指定。カンマ区切りで複数指定可能 |None |
|--genelist/-g    |False     |遺伝子リストファイルのパス      |None                       |
|--data_type/-t   |False     |発現量の計測単位 [gene,isoform] |gene                       |
|--directory/-d   |False     |解析フォルダの親ディレクトリ    |/data1/data/result         |
|--outdir/-o      |False     |データの出力先ディレクトリ      |/data1/work/expression     |

--genelist を指定しない場合はすべての全遺伝子の発現量を書き出す。

## 2\. sample IDと遺伝子名を指定
Sample IDと遺伝子を指定し、まとめて1つのExcelファイルに書き出す。
(カンマ区切りで複数指定可能)
```
singularity exec --bind /data1 $img python $SCRIPT individual --sample <sample IDs> --gene <genes>
singularity exec --bind /data1 $img python $SCRIPT IND --sample <sample IDs> --gene <genes>
```
### オプションの詳細
```
$ singularity exec --bind /data1 $img python $SCRIPT individual --help
version: v1.0.0
usage: expression.py individual [-h] --sample SAMPLE --gene GENE [--data_type {gene,isoform}]
                                [--directory DIRECTORY] [--outfile OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  --sample SAMPLE, -s SAMPLE
                        Sample ID (comma separated) (default: None)
  --gene GENE, -g GENE  genes (comma separated) (default: None)
  --data_type {gene,isoform}, -t {gene,isoform}
                        where each simulated read comes from. (default: gene)
  --directory DIRECTORY, -d DIRECTORY
                        parent analytical directory (default: /data1/data/result)
  --outfile OUTFILE, -o OUTFILE
                        output file path (default: /data1/work/expression/expression.xlsx)
```
| option        | required | 概要            |default            |
|:--------------|:---------|:----------------|:------------------|
|--sample/-s    |True      |sample ID        |None (カンマ区切りで複数指定可)        |
|--gene/-g      |True      |gene name        |None (カンマ区切りで複数指定可)        |
|--data_type/-t |False     |発現量の計測単位 [gene,isoform]      |gene               |
|--directory/-d |False     |解析フォルダの親ディレクトリへのパス |/data1/data/result |
|--outfile/-o   |False     |出力ファイルパス |/data1/work/expression/expression.xlsx |

