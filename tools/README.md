# Scripts
## rM2pdf 
This is a fork of this https://github.com/phil777/maxio which is a fork of this https://github.com/reHackable/maxio

What can it do? It can transform .lines files into pdfs using the pdf generation library Cairo pretty quickly. It scales the lines to the correct format given a reference pdf (input pdf). It's well suited transform annotations. which can then be added to the original pdf (see below).

What can't it do? Cairo doesn't really support pen types that change width or darkness. This script will do it's best with these pen types but they won't translate terribly well. It's not very well suited to transform intricate drawings. For those it may be best to use the rM2svg function and turn it into a pdf using pdftk.


```
usage: rM2pdf [-h] -i FILENAME -p INPUTPDF -o OUTPUTPDF

optional arguments:
  -h, --help                        show this help message and exit
  -i FILENAME, --input FILENAME     .lines input file
  -p INPUTPDF, --pdf                Pdf file to which the lines file should be scaled
  -o OUTPUTPDF, --output OUTPUTPDF  output file
  -c COLOUR, --coloured_annotations Colour annotations for document markup
  --version                         show program's version number and exit
```

## rM2svg 
https://github.com/reHackable/maxio

Convert a .lines file to an svg file

    usage: rM2svg [-h] -i FILENAME -o NAME -c

    optional arguments:
      -h, --help                      show this help message and exit
      -i FILENAME, --input FILENAME   .lines input file
      -o NAME, --output NAME          prefix for output file
      -c COLOUR, --coloured_annotations Colour annotations for document markup
      --version                       show program's version number and exit

# How to get usable annotated PDFs out of your reMarkable 

## Step 1: rM2pdf
Convert a .lines file to a pdf file

example (Terminal):
```
  python3 rM2pdf -i test/tools-source.lines -p input.pdf -o annot.pdf -c;
```
This will give you a pdf with only the annotations on it. 

## Step 2: Combine with original
Now you can use pdftk to combine the original with the annotation-pdf to get a nice, annotated, non-huge, OCR'd PDF like such:
```
pdftk input.pdf multistamp annot.pdf output final.pdf 
```
