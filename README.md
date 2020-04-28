# PDFOptimizerScript
Just a script for optimizing PDFs in a folder and outputing them into a new folder using GhostScript

## Usage
Run `main.py` with the source and destination folders like so
**Note:** Folder paths can be relative to where the script is being run
```
python3 main.py --inFolder source/Folder/Path --outFolder dest/folder/path
```

### Other options

- `--rename`
    - add "_Optimized" to the end of the destination filenames
- `--stats`
    - print out the percentage that each file has been reduced at the end of the job
- `--compression-level`
    - set the level of compression, range is from 0 (lowest) to 4 (highest)
- `--file-dialogue`
    - Open a file dialogue to pick input and output folders rather than using command line arguments
    - Two windows will open in succession, the first one being to pick the input folder, and the second for the output folder, the script will continue as normal after both folders have been selected
- `--image-res`
    - manually set image resolution in pixel dpi

Example command with all flags
```
python3 main.py --inFolder source/Folder/Path --outFolder dest/folder/path --rename --stats --compression-level 3 --image-res 150
```
Or like if you wish to pick folders with a file dialogue
```
python3 main.py --file-dialogue --rename --stats --compression-level 3 --image-res 150
```

## Technical Details

This script leverages the [GhostScript](https://www.ghostscript.com/) command line utility, and pythons [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) module for parallelization

The script compiles a list of all pdf files in the folder given by `--inputFolder`, and use the `multiprocessing.Pool` class to create a process pool with as many processes and `multiprocessing.cpu_count()` returns on the machine running the script

The process pool will then run the `optimize()` function on each file, running the GhostScript command

