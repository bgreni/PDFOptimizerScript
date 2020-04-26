from os import path, system, mkdir
from multiprocessing import Pool, cpu_count
import time
import argparse
from pathlib import Path
from datetime import timedelta

class Timer:    
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start

# quality options for GhostScript 4 is the highest compression level
quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

args = None

def optimize(filename: str):

    if args.rename:
        # add "_Optimized to end of the filename"
        split = filename.split('/')[-1].split('.')
        split[0] += '_Optimized'
        newName = '.'.join(split)
        outFile = args.outFolder + '/' + newName
    else:
        outFile = args.outFolder + '/' + filename.split('/')[-1]

    # format ghostscript command string
    command = (f'gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS={quality[args.compressionLevel]}'
        f' -dNOPAUSE -dQUIET -dBATCH -sOutputFile=\"{outFile}\" \"{filename}\"')

    # run command
    system(command)

    # get size stats
    if args.stats:
        beforeSize = path.getsize(filename)
        afterSize = path.getsize(outFile)
        return filename, beforeSize, afterSize


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Compress all PDFs in folder and put them in a new one.')
    parser.add_argument('--inFolder', dest='inFolder', type=str, 
        help='The folder containing the original files, relative to this file, or full path')
    parser.add_argument('--outFolder', dest='outFolder', type=str,
        help='The folder you wan the compressed files to be copied to.')
    parser.add_argument('--rename', dest='rename', action='store_true', default='False',
        help='Add flag to add \"_Optimized\" to the end of the filenames')
    parser.add_argument('--stats', dest='stats', action='store_true', default='False',
        help='Print out reduction stats for each file after execution')
    parser.add_argument('--compression-level', dest='compressionLevel', type=int, default=4,
        help='The compression level to use.')

    args = parser.parse_args()

    if not args.inFolder:
        raise Exception('You have not specified in inFolder')

    if not args.outFolder:
        raise Exception('You have not specified in outFolder')

    # kinda gross but whatever
    filesList = list(filter(lambda x: x.endswith('.pdf'), [str(Path(f).resolve()) for f in Path(args.inFolder).iterdir()]))

    # create destination folder if it doesn't already exist
    if not path.exists(args.outFolder):
        mkdir(args.outFolder)

    with Timer() as t:
        with Pool(cpu_count()) as p:
            returns = p.map(optimize, filesList)

    # print time it took
    print('Time taken:', str(timedelta(seconds=t.interval)))

    # print out size improvement of each file processed
    if args.stats:
        for filename, beforeSize, afterSize in returns:
            print('file: ' + filename.split('/')[-1] + ' is now ' + str(round(1 - (afterSize / beforeSize), 2)) + '%% smaller')