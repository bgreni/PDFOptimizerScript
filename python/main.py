from os import path, system, mkdir
from sys import platform, stdout
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


class PDFOptimizer:
    def __init__(self, args):
        self.args = args
        # quality options for GhostScript 4 is the highest compression level
        self.qualityOptions = {
            0: '/default',
            1: '/prepress',
            2: '/printer',
            3: '/ebook',
            4: '/screen'
        }
        self.filesTotal = 0

    def optimize(self, filename: str):

        if self.args.rename:
            # add "_Optimized to end of the filename"
            # print('Filename: ',filename)
            split = filename.split('/')[-1].split('.pdf')
            # print ('split:',split)
            split[0] += '_Optimized'
            newName = ''.join(split) + '.pdf'
            # print ('selfargsoutFolder:',self.args.outFolder)
            # print ('newName:',newName)
            outFile = self.args.outFolder + '/' + newName
            # outFile = newName
            # print ('outFile:',outFile)
        else:
            outFile = self.args.outFolder + '/' + filename.split('/')[-1]

        # Average Subsample Bicubic
        downSampleType = 'Bicubic'

        compressLevel = self.args.compressionLevel

        if self.args.imageRes != -1:
            imageRes = self.args.imageRes
        else:
            if compressLevel == 4:
                imageRes = 72
            elif compressLevel == 3:
                imageRes = 150
            else:
                imageRes = 300

        # format ghostscript command string
        if platform == 'win32':
            command = (f'gswin64c -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS={self.qualityOptions[self.args.compressionLevel]}'
            f' -dNOPAUSE -dQUIET -dBATCH -sOutputFile=\"{outFile}\" \"{filename}\"')
        else:
            command = (f'gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 -dPDFSETTINGS={self.qualityOptions[self.args.compressionLevel]}'
            f' -dNOPAUSE -dQUIET -dBATCH'
            f' -dColorImageDownsampleType=/{downSampleType} -dColorImageResolution={imageRes}'
            f' -dGrayImageDownsampleType=/{downSampleType} -dGrayImageResolution={imageRes} -dMonoImageDownsampleType=/{downSampleType}'
            f' -dMonoImageResolution={imageRes} -dImageDownsampleThreshold=1.0 -dEmbedAllFonts=true -dInterpolateControl=-1'
            f' -sOutputFile=\"{outFile}\" -c \"100000000 setvmthreshold\" -f \"{filename}\"') 
        
        # run command
        system(command)

        # get size stats
        if self.args.stats:
            beforeSize = path.getsize(filename)
            afterSize = path.getsize(outFile)
            return filename, beforeSize, afterSize

    def run(self):
        # kinda gross but whatever
        filesList = list(filter(lambda x: x.endswith('.pdf'), [str(Path(f).resolve()) for f in Path(self.args.inFolder).iterdir()]))

        self.filesTotal = len(filesList)
        # create destination folder if it doesn't already exist
        if not path.exists(self.args.outFolder):
            mkdir(self.args.outFolder)

        returns = []
        with Timer() as t:
            with Pool(cpu_count()) as p:
                for i, item in enumerate(p.imap_unordered(self.optimize, filesList), 1):
                    returns.append(item)
                    stdout.write('\rdone {0:%}'.format(i/self.filesTotal))
        # new line
        print()

        # print time it took
        print('Time taken:', str(timedelta(seconds=t.interval)))

        # print out size improvement of each file processed
        if self.args.stats:
            for filename, beforeSize, afterSize in returns:
                print('file: ' + filename.split('/')[-1] + ' is now ' + str(round((1 - (afterSize / beforeSize)) * 100, 2)) + '%% smaller, ' + str(beforeSize) + ' - ' + str(afterSize))

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
    parser.add_argument('--file-dialogue', dest='openFiles', action='store_true', default='False', 
        help='Open file dialogue to pick folder rather than pass as args.')
    parser.add_argument('--image-res', dest='imageRes', type=int, default=-1,
        help='Manually set image resolution.')


    arguments = parser.parse_args()

    if arguments.openFiles == True:
        # open file dialogue with tkinter
        from tkinter import filedialog
        from tkinter import *
        root = Tk()
        root.withdraw()
        arguments.inFolder = filedialog.askdirectory()
        arguments.outFolder = filedialog.askdirectory()
    else:
        # check folder args exist
        if not arguments.inFolder:
            raise Exception('You have not specified in inFolder')

        if not arguments.outFolder:
            raise Exception('You have not specified in outFolder')

    optimizer = PDFOptimizer(arguments)
    optimizer.run()