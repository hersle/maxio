# maxio: a toolset for reMarkable management

Series of tools to manage files produced by the reMarkable paper table (.rm extension, also known as "lines" files).


# 1. Operation

## 1.1 Rsync all the raw files from a remarkable tablet into a local directory

Connect tablet to usb (tablet must be on). Get access:

```
$ sudo ip addr add 10.11.99.2/24 dev enp0s20u1u1u4
```

Copy all the raw files into a directory in your host:

```
$ rsync -avut --progress --rsync-path=/opt/bin/rsync remarkable:/home/root/.local/share/remarkable/xochitl/ ~/personal/notebook/raw/
```


## 1.2 Convert all raw all the files from a remarkable tablet into a local directory

Convert all raaw files into pdf files:

```
$ rm_tools/rmtool.py convert-all --root ~/personal/notebook/raw/ --outdir ~/personal/notebook/pdf -dd
```


## 1.3. List all the raw file names

```
$ rm_tools/rmtool.py --root ~/personal/notebook/raw/ list
<uuid1> <data1> <name1>
  <uuid11> <data11> <name11>
  <uuid12> <data12> <name12>
  ...
<uuid2> <data2> <name2>
  <uuid21> <data21> <name21>
  ...
```


## 1.4. Convert a single raw file into svg/pdf

Convert into svg:

```
$ rm_tools/rm2svg.py -i ./rm_tools/convert_procedure/paper/93ce11cf-31e6-4a6c-ac67-7214c6be96ab.rm -o /tmp/foo.svg
```

Convert into pdf:
```
$ rm_tools/convert ~/personal/notebook/raw/<uuid> out/pdf
```
