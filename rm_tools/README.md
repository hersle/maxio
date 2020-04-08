# Use in Terminal
Convert a .rm file to an svg file. This will only be one page of your document.

    usage: rM2svg [-h] -i FILENAME -o NAME -c

    optional arguments:
      -h, --help                      show this help message and exit
      -i FILENAME, --input FILENAME   .lines input file
      -o NAME, --output NAME          prefix for output file
      -c COLOUR, --coloured_annotations Colour annotations for document markup
      --version                       show program's version number and exit

# Use as python import / get Annotated PDFs
![alt text](annot_pdf.png "Conceptual combine")

...see `convert.ipynb` in convert_procedure.

You can install rm_tools by cd-ing into the maxio folder and typing
`pip3 install .`.

# Notes
8.4.2020
- Unfortunately the direct-to-pdf code is deprecated with the new .rm format.
- The rm2svg code works with version 2.0.2 (rm file format 5). The updates were taken from https://github.com/peerdavid/rmapi/blob/master/tools/rM2svg
- The difference to that version is mainly that this version converts only one rm file (I handle multiple pages in my rMsync script: https://github.com/lschwetlick/rMsync)
