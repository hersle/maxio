# How to get usable PDFs out of your reMarkable 
This is a fork of this https://github.com/phil777/maxio which is a fork of this https://github.com/reHackable/maxio

## Step 1: rM2pdf
Convert a .lines file to a pdf file

```
usage: rM2pdf [-h] -i FILENAME -p INPUTPDF -o OUTPUTPDF

optional arguments:
  -h, --help                        show this help message and exit
  -i FILENAME, --input FILENAME     .lines input file
  -p INPUTPDF, --pdf                Pdf file to which the lines file should be scaled
  -o OUTPUTPDF, --output OUTPUTPDF  output file
  --version                         show program's version number and exit

example (Terminal):
  ./rM2svg -i input.lines -p input.pdf -o annot.pdf
```
## Step 2: Combine with original
This will give you a pdf with only the annotations on it. Now you can use pdftk to combine the original with the annotation-pdf to get an annotated, non-huge, OCR'd PDF like such:
```
pdftk input.pdf multistamp annot.pdf output final.pdf 
```