# Support for Remarkable lines version=6 File Format

This page is an effort to document version=6 of the lines format (.rm file), in order to add it to the different parsers/converters (in particular [maxio](https://github.com/lschwetlick/maxio)).


# Context: reMarkable lines File Formats

My tablet was updated to version 3.0.4.1305 last week. Since then the conversion scripts stopped working. Problem is that the lines files (.rm) have been updated from version=5 to version=6. We can see that the old files start with:

```
reMarkable .lines file, version=5
```

While the new ones start with:

```
reMarkable .lines file, version=6
```

Unfortunately, the format seems to have change a lot, and the [maxio](https://github.com/lschwetlick/maxio) converter stopped working.

Major changes in the format kind of makes sense, in particular because version 3 of the remarkable software seems to have added text support, which AFAICT was not supported in the previous formats.


# Lines version=3/version=5 File Format

Most of the jargon and knowledge comes from the [implementation](https://github.com/lschwetlick/maxio) and [the original analysis of the version=3 format](https://plasma.ninja/blog/devices/remarkable/binary/format/2017/12/26/reMarkable-lines-file-format.html). The change from version=3 to version=5 is relatively simple, and was documented [here](https://github.com/juruen/rmapi/issues/67).

A "notebook" (document) consists of pages. Pages consist of layers. Layers consists of strokes. Strokes consits of segments.
* A notebook is a separate document.
* A page is what you would think for a page.
* A "layer" is ???
* A "stroke" is ???
* A "segment" is basically a dot. Each one of them

To provide an idea of the contents, I created a notebook on a tablet on build 2 (lines version=5, see [here](https://github.com/chemag/maxio/examples/test1/v5/)), where the first page contains just a single dot (I just touched the screen with he stylus once, and I can see a single dot). Let's call this the "single dot" notebook. I extracted the files, and then copied them to a second remarkable tablet, this one on build 3. I open the file, added a point, and removed it (just opening the file does not cause the file to be converted to version=6, see [here](https://github.com/chemag/maxio/examples/test1/v6/)). I then extracted the files, and compared the .rm file contents.

First I added some print's to the maxio parser.

```
#file: test1/v5/508cfea7-9b18-4e77-b3d1-f4a67e70ddcf/f5184f96-afae-4e9a-8102-c2c986dc183e.rm
header: b'reMarkable .lines file, version=5          ' nlayers: 1 raw:\x72\x65\x4d\x61\x72\x6b\x61\x62\x6c\x65\x20\x2e\x6c\x69\x6e\x65\x73\x20\x66\x69\x6c\x65\x2c\x20\x76\x65\x72\x73\x69\x6f\x6e\x3d\x35\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x01\x00\x00\x00
  layer: 0/1
  nstrokes: 1 [offset: 51] raw:\x01\x00\x00\x00
    Stroke 0: pen_nr=13, colour=0, i_unk=0, width=2.0, unknown=0.0, nsegments=11 [offset=75] raw=\x0d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\x00\x0b\x00\x00\x00
      Segment 0: xpos=276.7100830078125, ypos=259.646484375, speed=0.7749431729316711, tilt=3.7647838592529297, width=5.9259257316589355 pressure=0.7004245519638062 [offset=99] raw=\xe4\x5a\x8a\x43\xc0\xd2\x81\x43\xad\x62\x46\x3f\x38\xf2\x70\x40\x2f\xa1\xbd\x40\x06\x4f\x33\x3f
      Segment 1: xpos=276.74139404296875, ypos=259.6581726074219, speed=0.09023801237344742, tilt=0.35727447271347046, width=5.9259257316589355 pressure=0.7342575192451477 [offset=123] raw=\xe6\x5e\x8a\x43\x3f\xd4\x81\x43\xb5\xce\xb8\x3d\xae\xec\xb6\x3e\x2f\xa1\xbd\x40\x4d\xf8\x3b\x3f
      Segment 2: xpos=276.73321533203125, ypos=259.7132568359375, speed=0.10342851281166077, tilt=0.7713145613670349, width=5.9259257316589355 pressure=0.8812189698219299 [offset=147] raw=\xda\x5d\x8a\x43\x4c\xdb\x81\x43\x54\xd2\xd3\x3d\xdf\x74\x45\x3f\x2f\xa1\xbd\x40\x91\x97\x61\x3f
      Segment 3: xpos=276.36431884765625, ypos=259.5073547363281, speed=0.7217628359794617, tilt=3.3392345905303955, width=5.9259257316589355 pressure=0.9814434051513672 [offset=171] raw=\xa2\x2e\x8a\x43\xf1\xc0\x81\x43\x73\xc5\x38\x3f\x05\xb6\x55\x40\x2f\xa1\xbd\x40\xe0\x3f\x7b\x3f
      Segment 4: xpos=276.246337890625, ypos=259.8296813964844, speed=0.5018981099128723, tilt=2.7499587535858154, width=5.9259257316589355 pressure=0.9862646460533142 [offset=195] raw=\x88\x1f\x8a\x43\x33\xea\x81\x43\x65\x7c\x00\x3f\x53\xff\x2f\x40\x2f\xa1\xbd\x40\xd7\x7b\x7c\x3f
      Segment 5: xpos=275.1815185546875, ypos=259.8385314941406, speed=0.34751254320144653, tilt=3.324712038040161, width=5.9259257316589355 pressure=0.9858895540237427 [offset=219] raw=\x3c\x97\x89\x43\x55\xeb\x81\x43\x2a\xed\xb1\x3e\x15\xc8\x54\x40\x2f\xa1\xbd\x40\x42\x63\x7c\x3f
      Segment 6: xpos=274.8877258300781, ypos=259.9025573730469, speed=0.15381628274917603, tilt=2.8576271533966064, width=5.9259257316589355 pressure=0.9621555805206299 [offset=243] raw=\xa1\x71\x89\x43\x87\xf3\x81\x43\x04\x82\x1d\x3e\x5d\xe3\x36\x40\x2f\xa1\xbd\x40\xd4\x4f\x76\x3f
      Segment 7: xpos=274.8074035644531, ypos=260.1326904296875, speed=0.5453184247016907, tilt=1.8659292459487915, width=5.9259257316589355 pressure=0.8736307621002197 [offset=267] raw=\x59\x67\x89\x43\xfc\x10\x82\x43\xfd\x99\x0b\x3f\xc5\xd6\xee\x3f\x2f\xa1\xbd\x40\x44\xa6\x5f\x3f
      Segment 8: xpos=274.8708801269531, ypos=260.05767822265625, speed=0.26531681418418884, tilt=5.414682388305664, width=5.9259257316589355 pressure=0.82357257604599 [offset=291] raw=\x79\x6f\x89\x43\x62\x07\x82\x43\x9b\xd7\x87\x3e\x14\x45\xad\x40\x2f\xa1\xbd\x40\xa7\xd5\x52\x3f
      Segment 9: xpos=274.9269714355469, ypos=260.0150146484375, speed=0.19027656316757202, tilt=5.632928848266602, width=5.9259257316589355 pressure=0.7330805659294128 [offset=315] raw=\xa7\x76\x89\x43\xec\x01\x82\x43\xdc\xd7\x42\x3e\xf4\x40\xb4\x40\x2f\xa1\xbd\x40\x2b\xab\x3b\x3f
      Segment 10: xpos=275.0770568847656, ypos=259.99822998046875, speed=0.0, tilt=0.0, width=5.9259257316589355 pressure=0.7000028491020203 [offset=339] raw=\xdd\x89\x89\x43\xc6\xff\x81\x43\x00\x00\x00\x00\x00\x00\x00\x00\x2f\xa1\xbd\x40\x63\x33\x33\x3f
```
In the file, we can see the page has only 1 layer, which has only 1 stroke, which has 11 segments. Note that the format is relatively simple: All the fields are either int or float, 4 bytes/field, in network order.

Let's see a hex dump of the version=5 file (based on the parser code). I added some comments to describe the contents.

```
// file header
00000000: 7265 4d61 726b 6162 6c65 202e 6c69 6e65  reMarkable .line
00000010: 7320 6669 6c65 2c20 7665 7273 696f 6e3d  s file, version=
00000020: 3520 2020 2020 2020 2020 20              5
00000020:                            01 0000 0001             .....
                                     nlayers=1| start of layer 0
// layer 0
                                              |nstrokes:1
00000030: 0000 00                                  ...

// stroke 0
                 | start of stroke 0
00000030:        0d 0000 00                           ....
                 pen_nr=0x0000000d=13 (mechanical pen)
00000030:                  00 0000 00                     .........
                           colour=0
00000030:                            00 0000 00               ....
                                     i_unk=0
00000030:                                      00                 .
                                               width=0x40000000=2.0
00000040: 0000 40                                  ..
00000040:        00 0000 00                           ....
                 unknown=0
00000040:                  0b 0000 00                     ....
                           nsegments=0x0b=11

00000040:                            e4 5a8a 43               .Z.C
// segment 0
                                     | start of segment 0
                                     xpos=0x438a5ae4=276.7100830078125
00000040:                                      c0                 .
                                               ypos=259.646484375
00000050: d281 43                                  ..C
00000050:        ad 6246 3f                           .bF?
                 speed=0.7749431729316711
00000050:                  38 f270 40                     8.p@
                           tilt=3.7647838592529297
00000050:                            2f a1bd 40               /..@
                                     width=5.9259257316589355
00000050:                                      06                 .
                                               pressure=0.7004245519638062
00000060: 4f33 3f                                  O3?

00000060:        e6 5e8a 43                     e     .^.C
                 | start of segment 1
                 xpos=276.74139404296875 ...
00000060:                  3f d481 43                     ?..C...=.
                           ypos=259.6581726074219
00000060:                            b5 ceb8 3d               ...=
                                     speed=0.09023801237344742
00000060:                                      ae                 .

00000070: ecb6 3e2f a1bd 404d f83b 3fda 5d8a 434c  ..>/..@M.;?.].CL
                                     | start of segment 2
00000080: db81 4354 d2d3 3ddf 7445 3f2f a1bd 4091  ..CT..=.tE?/..@.
00000090: 9761 3fa2 2e8a 43f1 c081 4373 c538 3f05  .a?...C...Cs.8?.
                 | start of segment 3
000000a0: b655 402f a1bd 40e0 3f7b 3f88 1f8a 4333  .U@/..@.?{?...C3
                                     | start of segment 4
000000b0: ea81 4365 7c00 3f53 ff2f 402f a1bd 40d7  ..Ce|.?S./@/..@.
000000c0: 7b7c 3f3c 9789 4355 eb81 432a edb1 3e15  {|?<..CU..C*..>.
                 | start of segment 5
000000d0: c854 402f a1bd 4042 637c 3fa1 7189 4387  .T@/..@Bc|?.q.C.
                                     | start of segment 6
000000e0: f381 4304 821d 3e5d e336 402f a1bd 40d4  ..C...>].6@/..@.
000000f0: 4f76 3f59 6789 43fc 1082 43fd 990b 3fc5  Ov?Yg.C...C...?.
                 | start of segment 7
00000100: d6ee 3f2f a1bd 4044 a65f 3f79 6f89 4362  ..?/..@D._?yo.Cb
                                     | start of segment 8
00000110: 0782 439b d787 3e14 45ad 402f a1bd 40a7  ..C...>.E.@/..@.
00000120: d552 3fa7 7689 43ec 0182 43dc d742 3ef4  .R?.v.C...C..B>.
                 | start of segment 9
00000130: 40b4 402f a1bd 402b ab3b 3fdd 8989 43c6  @.@/..@+.;?...C.
                                     | start of segment 10
00000140: ff81 4300 0000 0000 0000 002f a1bd 4063  ..C......../..@
00000140:                                      63                 c
                                               pressure=0.7000028491020203
00000150: 3333 3f                                  33?
```


# Lines version=6 File Format

I got the .rm file corresponding to the same page, and converted it to hex. I added some comments on data that is related to the version=5 file.

```
// header
00000000: 7265 4d61 726b 6162 6c65 202e 6c69 6e65  reMarkable .line
00000010: 7320 6669 6c65 2c20 7665 7273 696f 6e3d  s file, version=
00000020: 3620 2020 2020 2020 2020 20              6

// chunk 1
00000020:                            19 0000 0000             .....
00000030: 0101 0901 0c13 0000 0010 7f49 3ff7 c157  ...........I?..W
00000040: 5496 8ee4 6c07 d9cb 40fb 0100 0500 0000  T...l...@.......
00000050: 0001 0100 1f01 0121 0114 0000 0000 0001  .......!........
00000060: 0a14 0100 0000 2400 0000 0034 0000 0000  ......$....4....
00000070: 4400 0000 0010 0000 0000 0101 011f 000b  D...............
00000080: 2f00 0031 014c 0300 0000 1f00 011c 0000  /..1.L..........
00000090: 0000 0101 021f 0001 2c0a 0000 001f 0000  ........,.......
000000a0: 2c02 0000 0000 013c 0500 0000 1f00 0021  ,......<.......!
000000b0: 0123 0000 0000 0101 021f 000b 2c11 0000  .#..........,...
000000c0: 001f 000c 2c09 0000 0007 01              ....,......
000000c0:                            4c 6179 6572             Layer
                                     "Layer 1" string here
000000d0: 2031                                      1

000000d0:      3c05 0000                             <...
               ???=1340
000000d0:                001f 0000                       ....
                         ???=0x00001f00
000000d0:                          2101 1a00 0000            !.....
000000e0: 0001 0104 1f00 012f 000d 3f00 004f 0000  ......./..?..O..
000000f0: 5400 0000 006c 0400 0000 022f 000b 3f01  T....l...../..?.
00000100: 0000 0001 0105 1f00 0b2f 000e 3f00 004f  ........./..?..O
00000110: 0000 5400 0000 006c 2901 0000 0314       ..T....l).....
00000110:                                    0d00                ..
                                             pen_nr=13 (mechanical pen)
00000120: 0000                                     ..
00000120:      2400 0000                             $...
               ???=36
00000120:                0038 0000                       .8..
                         ???=56
00000120:                          0000 0000                 ....
                                   ???=0
00000120:                                    0040                .@
                                             ???=0x00444000 (4472832, 6.2677726127829e-39)
00000130: 4400                                     D.
00000130:      0000 005c                             ...\
               ???=0x5c000000 (1543503872, 1.4411518807585587e+17)
00000130:                0801 0000                       ....
                         ???=264


// segment 0
00000130:                          1ca5 d4c3                 ....
                                   | start of segment 0
                                   xpos=-425.2899169921875 (instead of 276.7100830078125)
00000130:                                    c0d2                ..
                                             ypos=259.646484375
00000140: 8143                                     .C
00000140:      ad62 463f                             .bF?
               speed=0.7749431729316711
00000140:                38f2 7040                       8.p@
                         tilt=3.7647838592529297
00000140:                          2fa1 bd40                 /..@
                                   width=5.9259257316589355
00000140:                                    064f                .O
                                             pressure=0.7004245519638062
00000150: 333f                                     3?
00000150:      1aa1 d4c3                             ....
               | start of segment 1
               xpos=-425.25860595703125 (instead of 276.74139404296875)
00000150:                3fd4 8143                       ?..C
                         ypos=259.6581726074219
00000150:                          b5ce b83d                 ...=
                                   speed=0.09023801237344742
00000150:                                    aeec                ..

00000160: b63e 2fa1 bd40 4df8 3b3f 26a2 d4c3 4cdb  .>/..@M.;?&...L.
                                             | start of segment 2
00000170: 8143 54d2 d33d df74 453f 2fa1 bd40 9197  .CT..=.tE?/..@..
00000180: 613f 5ed1 d4c3 f1c0 8143 73c5 383f 05b6  a?^......Cs.8?..
               | start of segment 3
00000190: 5540 2fa1 bd40 e03f 7b3f 78e0 d4c3 33ea  U@/..@.?{?x...3.
                                             | start of segment 4
000001a0: 8143 657c 003f 53ff 2f40 2fa1 bd40 d77b  .Ce|.?S./@/..@.{
000001b0: 7c3f c468 d5c3 55eb 8143 2aed b13e 15c8  |?.h..U..C*..>..
               | start of segment 5
000001c0: 5440 2fa1 bd40 4263 7c3f 5f8e d5c3 87f3  T@/..@Bc|?_.....
                                             | start of segment 6
000001d0: 8143 0482 1d3e 5de3 3640 2fa1 bd40 d44f  .C...>].6@/..@.O
000001e0: 763f a798 d5c3 fc10 8243 fd99 0b3f c5d6  v?.......C...?..
               | start of segment 7
000001f0: ee3f 2fa1 bd40 44a6 5f3f 8790 d5c3 6207  .?/..@D._?....b.
                                             | start of segment 8
00000200: 8243 9bd7 873e 1445 ad40 2fa1 bd40 a7d5  .C...>.E.@/..@..
00000210: 523f 5989 d5c3 ec01 8243 dcd7 423e f440  R?Y......C..B>.@
               | start of segment 9
00000220: b440 2fa1 bd40 2bab 3b3f 2376 d5c3 c6ff  .@/..@+.;?#v....
                                             | start of segment 10
00000230: 8143 0000 0000 0000 0000 2fa1 bd40       .C......../..@
00000230:                                    6333                c3
00000240: 333f                                     3?


// chunk 2
00000240:      6f00 0f11                             o...
               | start of ???
               ???=0x110f006f
00000240:                0000 0000                       ....
                         ???=0
00000240:                          0101 051f                 ....
                                   ???=0x1f050101
00000240:                                    000b                ..
                                             ???=0x012f0b00
00000250: 2f01                                     /.
00000250:      103f 000e                             .?..
               ???=0x0e003f10
00000250:                4f00 0054                       O..T
                         ???=0x5400004f
00000250:                          0100 0000                 ....
                                   ???=1

```

# Discussion

We can see the 11 segments. They look exactly like the ones in version=5, except that the xpos has been shifted 702 points (e.g. the first dot has been shifted from 276.7100830078125 to -425.2899169921875). This is likely related to pages in version=6 being easy to resize. The segments keep the simple format (integer or float, 4 bytes/field, network order). This suggests they keep the same simplicity everywhere else.

Chunk 1 must contain the layers and strokes description. I expect the converted document to still have 1 layer and 1 stroke.
* I can see "Layer 1" in text. This suggests a text-format to define layers (and name them?). That would be new.
* I can see a "0d000000" string. This could be the stroke pen id (0x0d, or mechanical pen).
* I was expecting to see a 0x0b field, for the number of segments (11 in the stroke). I can't see it. There are 4x bytes with the value 0x0b (offsets 0x7f, 0xba, 0xfd, 0x108), but none of them is followed by zero bytes, which would imply the format changes the nsegments field from 4 bytes to 1 byte.


Chunk 2 is interesting. I'm not sure what it is about. There are 28 bytes (compare to 20 bytes/segment), and the structure is different from the segment one. It may be related to the fact that I had to add a dot and remove it in order to force the conversion to version=6.
