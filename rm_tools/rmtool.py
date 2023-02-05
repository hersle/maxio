#!/usr/bin/env python3

"""Script for operating on reMarkable tablet ".rm" files."""

import argparse
import datetime
import glob
import json
import subprocess
import sys
import tempfile
import os
import os.path

dirname = os.path.dirname(sys.modules[__name__].__file__)
test_dir = os.path.abspath(dirname)
sys.path.append(test_dir)

import rm2svg

# try to add the rmscene repo
VERSION_6_SUPPORT = False
rmscene_dirname = os.path.join(dirname, "..", "..", "rmscene", "src")
rmscene_test_dir = os.path.abspath(rmscene_dirname)
if os.path.isdir(rmscene_test_dir):
    sys.path.append(rmscene_test_dir)
    import rmscene.rm2svg as rm2svgv6
    VERSION_6_SUPPORT = True


ENUM_COMMANDS = ['list', 'convert', 'convert-all']

default_values = {
    'debug': 0,
    'rootdir': None,
    'outdir': None,
    'command': None,
    'infile': None,
    'outfile': None,
}


def read_metadata(rootdir, uuid):
    metadata_file = os.path.join(rootdir, uuid + '.metadata')
    with open(metadata_file, 'r') as f:
        json_text = f.read()
    return json.loads(json_text)


def read_content(rootdir, uuid):
    content_file = os.path.join(rootdir, uuid + '.content')
    with open(content_file, 'r') as f:
        json_text = f.read()
    return json.loads(json_text)


def read_pagedata(rootdir, uuid):
    pagedata_file = os.path.join(rootdir, uuid + '.pagedata')
    with open(pagedata_file, 'r') as f:
        text = f.read()
    return text.split()


class Node:
    def __init__(self, uuid, metadata):
        self.uuid = uuid
        self.metadata = metadata
        self.children = []
        self.next = None

    def __str__(self):
        s = 'uuid: "%s"' % self.uuid
        s += ' metadata: %r' % self.metadata
        s += ' children: %r' % self.children
        s += ' next: %r' % self.next
        return s


# parses the (raw) root directory
def get_repo_info(rootdir, debug):
    # create an unordered node list
    node_list = []
    metadata_list = glob.glob(os.path.join(rootdir, '*.metadata'))
    for metadata_file in metadata_list:
        uuid, _ = os.path.basename(metadata_file).split('.')
        metadata = read_metadata(rootdir, uuid)
        node_list.append([uuid, metadata])

    # add the node list into a tree
    rootnode = Node('', None)
    cur_uuid_list = [rootnode.uuid]
    cur_node = [rootnode]
    prev_node = None
    while node_list:
        new_cur_uuid_list = []
        new_cur_node = []
        new_node_list = []
        for uuid, metadata in node_list:
            if metadata['parent'] == 'trash':
                # ignore it
                pass
            elif metadata['parent'] in cur_uuid_list:
                # found the parent
                index = cur_uuid_list.index(metadata['parent'])
                node = Node(uuid, metadata)
                cur_node[index].children.append(node)
                new_cur_uuid_list.append(uuid)
                new_cur_node.append(node)
                if prev_node is not None:
                    prev_node.next = node
                prev_node = node
            else:
                # keep looking
                new_node_list.append([uuid, metadata])
        # reset status
        cur_uuid_list = new_cur_uuid_list
        cur_node = new_cur_node
        node_list = new_node_list

    # sort nodes alphabetically (visibleName)
    # using bubble-sort as sizes should be small
    # TODO(chemag): use some interview-acceptable sort here
    def do_bubble_sort(node):
        for indexl in range(len(node.children)):
            for indexr in range(indexl + 1, len(node.children)):
                vall = node.children[indexl].metadata['visibleName']
                valr = node.children[indexr].metadata['visibleName']
                if vall > valr:
                    # swap nodes
                    tmp = node.children[indexl]
                    node.children[indexl] = node.children[indexr]
                    node.children[indexr] = tmp
        # fix next pointers
        for index in range(len(node.children) - 1):
            node.children[index].next = node.children[index + 1]
        if len(node.children) > 0:
            node.children[len(node.children) - 1].next = None

    def node_sort(node):
        # start with the node itself
        do_bubble_sort(node)
        for node in node.children:
            node_sort(node)

    node_sort(rootnode)
    return rootnode


def list_repo(rootdir, debug):
    rootnode = get_repo_info(rootdir, debug)

    # dump lines
    def print_node(node, tab):
        if node.uuid == '':
            # do not print the root node
            pass
        else:
            uuid = node.uuid
            unix_ts = int(node.metadata['lastModified'])
            unix_dt = datetime.datetime.fromtimestamp(unix_ts / 1000)
            unix_str = unix_dt.strftime("%Y%m%d-%H:%M:%S.%f")
            visible_name = node.metadata['visibleName']
            print('%s %s %s %s' % ('  ' * tab, uuid, unix_str, visible_name))
        for node in node.children:
            print_node(node, tab + 1)

    tab = 0
    print_node(rootnode, tab)


def run(command, dry_run, **kwargs):
    env = kwargs.get('env', None)
    stdin = subprocess.PIPE if kwargs.get('stdin', False) else None
    bufsize = kwargs.get('bufsize', 0)
    universal_newlines = kwargs.get('universal_newlines', False)
    default_close_fds = True if sys.platform == 'linux2' else False
    close_fds = kwargs.get('close_fds', default_close_fds)
    shell = type(command) in (type(''), type(u''))
    if dry_run:
        return 0, b'stdout', b'stderr'
    p = subprocess.Popen(command, stdin=stdin, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, bufsize=bufsize,
                         universal_newlines=universal_newlines,
                         env=env, close_fds=close_fds, shell=shell)
    # wait for the command to terminate
    if stdin is not None:
        out, err = p.communicate(stdin)
    else:
        out, err = p.communicate()
    returncode = p.returncode
    # clean up
    del p
    # return results
    return returncode, out, err


def convert_file(infile, outfile, rootdir, debug):
    # get uuid
    uuid = os.path.basename(infile).split('.')[0]
    if not rootdir:
        rootdir = os.path.dirname(infile)
    # get file info
    # metadata = read_metadata(rootdir, uuid)
    content = read_content(rootdir, uuid)
    # pagedata = read_pagedata(rootdir, uuid)
    # create tempdir
    tmpdir = tempfile.mkdtemp(prefix='rmtool.tmp.', dir='/tmp')
    # convert pages to pdf
    pagepdf_list = []

    # get page list
    if content['formatVersion'] == 1:
        page_uuid_list = content['pages']
    elif content['formatVersion'] == 2:
        page_uuid_list = [page['id'] for page in content['cPages']['pages'] if 'deleted' not in page]

    for page_num, page_uuid in enumerate(page_uuid_list):
        # ensure the file exists
        page_path = os.path.join(rootdir, uuid, page_uuid + '.rm')
        assert(os.path.exists(page_path))
        pagerm = page_path
        pagesvg = os.path.join(tmpdir, page_uuid + '.svg')
        colored_annotations = True

        # determine background document's size:
        # 1) no background PDF (pure RM notebook): 1404px x 1872 px (RM screen size) = 157mm x 210mm (exported PDF)
        # 2) with background PDF: obtain its physical size and convert to RM pixels
        px_per_mm_x = 1404 / 157 # for unextended standard notes
        px_per_mm_y = 1872 / 210 # for unextended standard notes
        bg_pdf_path = os.path.join(rootdir, uuid + '.pdf')
        if os.path.exists(bg_pdf_path):
            command = f'identify -format "%w %h " "{bg_pdf_path}"' # TODO: get PDF without shell command
            returncode, out, err = run(command, False)
            w_h_pairs = [float(size) for size in out.split()]
            width_mm = w_h_pairs[2*page_num+0] / 72 * 25.4 # convert to mm
            height_mm = w_h_pairs[2*page_num+1] / 72 * 25.4 # # convert to mm
        else:
            width_mm  = width  / px_per_mm_x # for unextended standard notes: 157mm
            height_mm = height / px_per_mm_y # for unextended standard notes: 210mm
        width_px = width_mm * px_per_mm_x
        height_px = height_mm * px_per_mm_y

        try:
            rm2svg.rm2svg(pagerm, pagesvg, colored_annotations, width_px, height_px)
        except:
            rm2svgv6.rm2svg(pagerm, pagesvg, minwidth=width_px, minheight=height_px)

        pagepdf = os.path.join(tmpdir, page_uuid + '.pdf')
        command = 'rsvg-convert --format=pdf --width=%fmm --height=%fmm "%s" > "%s"' % (width_mm, height_mm, pagesvg, pagepdf)
        returncode, out, err = run(command, False)
        assert(returncode == 0), command
        pagepdf_list.append(pagepdf)

    # put all the pages together
    command = 'pdfunite %s "%s"' % (' '.join(pagepdf_list), outfile)
    returncode, out, err = run(command, False)
    assert(returncode == 0), command

    # if a background PDF exists, render the foreground annotations on top of it
    if os.path.exists(bg_pdf_path):
        fg_pdf_path = outfile # what we just rendered above
        outfile_merged = outfile.removesuffix('.pdf') + '_merged.pdf'
        command = 'qpdf "%s" --overlay "%s" -- "%s"' % (bg_pdf_path, fg_pdf_path, outfile_merged)
        returncode, out, err = run(command, False)
        assert(returncode == 0), command

        # overwrite outfile (foreground only) with outfile_merged (foreground + background)
        command = 'mv "%s" "%s"' % (outfile_merged, outfile)
        returncode, out, err = run(command, False)
        assert(returncode == 0), command


def convert_all(rootdir, outdir, debug):
    rootnode = get_repo_info(rootdir, debug)

    # traverse the tree
    def traverse_node(node, rootdir, outdir, debug):
        if node.uuid == '':
            # ignore the root node
            pass
        else:
            uuid = node.uuid
            unix_ts_ms = int(node.metadata['lastModified'])
            unix_ts = unix_ts_ms / 1000
            visible_name = node.metadata['visibleName']
            visible_name = visible_name.replace(' ', '_')
            t = node.metadata['type']
            if t == 'CollectionType':
                # folder: make sure the directory exists
                outdir = os.path.join(outdir, visible_name)
                if not os.path.exists(outdir):
                    os.mkdir(outdir, mode=0o755)
            elif t == 'DocumentType':
                # file: convert the file into a pdf
                # check whether the file already exists (with right timestamp)
                infile = os.path.join(rootdir, uuid)
                outfile = os.path.join(outdir, visible_name + '.pdf')
                do_convert = True
                if os.path.exists(outfile):
                    # output file already exists: check mtime
                    file_mtime = os.stat(outfile).st_mtime
                    if file_mtime > unix_ts:
                        # output file exists and is younger
                        do_convert = False
                if do_convert:
                    if debug > 0:
                        print('..converting %s -> %s' % (infile, outfile))
                    convert_file(infile, outfile, rootdir, debug)
        for node in node.children:
            traverse_node(node, rootdir, outdir, debug)

    traverse_node(rootnode, rootdir, outdir, debug)


def get_options(argv):
    """Generic option parser.

    Args:
        argv: list containing arguments

    Returns:
        Namespace - An argparse.ArgumentParser-generated option object
    """
    # init parser
    # usage = 'usage: %prog [options] arg1 arg2'
    # parser = argparse.OptionParser(usage=usage)
    # parser.print_help() to get argparse.usage (large help)
    # parser.print_usage() to get argparse.usage (just usage line)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
            '-d', '--debug', action='count',
            dest='debug', default=default_values['debug'],
            help='Increase verbosity (use multiple times for more)',)
    parser.add_argument(
            '--quiet', action='store_const',
            dest='debug', const=-1,
            help='Zero verbosity',)
    parser.add_argument(
            '-r', '--root', action='store', type=str,
            dest='rootdir', default=default_values['rootdir'],
            metavar='ROOT',
            help='use ROOT as root directory (xochitl)',)
    parser.add_argument(
            '-o', '--outdir', action='store', type=str,
            dest='outdir', default=default_values['outdir'],
            metavar='OUTDIR',
            help='use OUTDIR as outdir directory',)
    # add command
    parser.add_argument(
            'command', action='store', type=str,
            default=default_values['command'],
            choices=ENUM_COMMANDS,
            metavar='[%s]' % (' | '.join(ENUM_COMMANDS,)),
            help='command',)
    # add i/o
    parser.add_argument(
            'infile', type=str, nargs='?',
            default=default_values['infile'],
            metavar='input-file',
            help='input file',)
    parser.add_argument(
            'outfile', type=str, nargs='?',
            default=default_values['outfile'],
            metavar='output-file',
            help='output file',)
    # do the parsing
    options = parser.parse_args(argv[1:])
    return options


def main(argv):
    # parse options
    options = get_options(argv)
    # print results
    if options.debug > 0:
        print(options)
    # need a valid infile or root directory

    # do something
    if options.command == 'list':
        list_repo(options.rootdir, options.debug)
    elif options.command == 'convert':
        convert_file(options.infile, options.outfile, options.rootdir, options.debug)
    elif options.command == 'convert-all':
        convert_all(options.rootdir, options.outdir, options.debug)


if __name__ == '__main__':
    # at least the CLI program name: (CLI) execution
    main(sys.argv)
