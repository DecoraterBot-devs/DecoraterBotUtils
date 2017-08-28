# coding=utf-8
# dbcdformat.py
"""
dbcd File Format Python Scypt.
"""
import getopt
import os
import struct
import sys
import zlib
import json
from xml.dom.minidom import parse, Document


__all__ = [
    'EntryVer1', 'make_entries', 'unpacker_main',
    'reader_main', 'packer_main']


class EntryVer1(object):
    """
    Sets Data for entries.
    """
    def __init__(self, name, uncompressed_size, compressed_size, relative_offset, file_time, algorithm):
        self.name = name
        self.uncompressed_size = uncompressed_size
        self.compressed_size = compressed_size
        self.relative_offset = relative_offset
        self.file_time = file_time
        self.algorithm = algorithm


class Result:
    """ ... """
    def __init__(self, data):
        self.data = data

    def to_json(self):
        """ ... """
        return json.loads(self.data)

    def dump(self, filename, dbcdfile, jsondata):
        """ ... """
        type(self)
        reader_main(filename, dbcdfile, write=True)
        in_path = dbcdfile.replace('.dbcd', '') + '_tmp'
        json_file = os.path.join(
            in_path, filename)
        try:
            with open(json_file, mode='w') as file:
                file.write(json.dumps(jsondata, indent=4, sort_keys=True))
        except(OSError, IOError):
            pass
        writer_main(in_path, dbcdfile)


def make_entries(crc_er, entry_count):
    """
    Makes entries to Iterate through the dbcd File format.
    :param crc_er: xml data stuff.
    :param entry_count: number of entries.
    :return: entry list and relative offsets to the data.
    """
    entries = []
    relative_offseterr = 0
    # access_time = 0
    for x in range(entry_count):
        entry = EntryVer1(crc_er.firstChild.firstChild.getAttribute("Name"),
                          crc_er.firstChild.firstChild.getAttribute("Size"),
                          int(crc_er.firstChild.firstChild.getAttribute("CompressedSize")),
                          int(relative_offseterr),
                          int(crc_er.firstChild.firstChild.getAttribute("FileTime"), 16),
                          int(crc_er.firstChild.firstChild.getAttribute("Algorithm")))
        entries.append(entry)
        crc_er.firstChild.removeChild(crc_er.firstChild.firstChild)
        relative_offseterr += entry.compressed_size
    return (entries, relative_offseterr)


def unpacker_main(argv):
    """
    Main Unpacker Program Function.
    :param argv: Arguments.
    :return: Nothing.
    """
    if len(argv) < 1:
        print("Usage:\ndbcdextract --in <dbcd file name> --out <Folder name>")
        sys.exit(2)
    try:
        options, arguments = getopt.getopt(argv, 'i:o:', ['in=', 'out='])
    except getopt.GetoptError:
        sys.exit(2)
    in_path = None
    out_path = None
    for option, argument in options:
        if option in ('i', '--in'):
            in_path = argument
        if option in ('o', '--out'):
            out_path = argument
    if(not in_path or not out_path or not os.path.isfile(in_path) or (os.path.exists(out_path) and not
       os.path.isdir(out_path))):
        print("Usage:\ndbcdextract --in <dbcd file name> --out <Folder name>")
        sys.exit(2)
    else:
        os.makedirs(out_path)
    with open(in_path, 'rb') as file_object:
        file_data = file_object.read()
    offset = 0
    # version = struct.unpack_from(b'<26s26x', file_data, offset)[0]
    offset += 60
    entry_count = struct.unpack_from(b'<I4x', file_data, offset)[0]
    offset += 12
    # file_timer = struct.unpack_from(b'<I', file_data, offset)[0]
    offset += 4
    xml_size_file = struct.unpack_from(b'<I', file_data, offset)[0]
    offset += 4
    theunpack_offset = offset + xml_size_file
    with open(in_path, 'rb') as crc_reader:
        crc_reader.seek(offset)
        crc_data = crc_reader.read(xml_size_file)
    with open("crc.xml", 'wb') as crc_creator:
        crc_creator.write(crc_data)
    with open("crc.xml") as crc_reader:
        crc_er = parse(crc_reader)
    os.remove("crc.xml")
    entries, relative_offseterr = make_entries(crc_er, entry_count)
    for entry in entries:
        entry_file_data = (file_data[theunpack_offset + entry.relative_offset:theunpack_offset +
                           entry.relative_offset +
                           entry.compressed_size])
        if entry.algorithm == 0:
            entry_file_data = zlib.decompress(entry_file_data)
            file_path = os.path.join(out_path, entry.name)
        else:
            file_path = os.path.join(out_path, ".".join((entry.name, str(entry.uncompressed_size), str(entry.algorithm))))
        with open(file_path, 'wb') as file_object:
            file_object.write(entry_file_data)
    print("Extraction Complete.")


def reader_main(filename, dbcdfile, write=False):
    """
    Main Reader Program Function.
    """
    try:
        with open(dbcdfile, 'rb') as file_object:
            file_data = file_object.read()
        offset = 0
        # version = struct.unpack_from(b'<26s26x', file_data, offset)[0]
        offset += 60
        entry_count = struct.unpack_from(b'<I4x', file_data, offset)[0]
        offset += 12
        # file_timer = struct.unpack_from(b'<I', file_data, offset)[0]
        offset += 4
        xml_size_file = struct.unpack_from(b'<I', file_data, offset)[0]
        offset += 4
        theunpack_offset = offset + xml_size_file
        with open(dbcdfile, 'rb') as crc_reader:
            crc_reader.seek(offset)
            crc_data = crc_reader.read(xml_size_file)
        with open("crc.xml", 'wb') as crc_creator:
            crc_creator.write(crc_data)
        with open("crc.xml") as crc_reader:
            crc_er = parse(crc_reader)
        os.remove("crc.xml")
        entries, relative_offseterr = make_entries(crc_er, entry_count)
        for entry in entries:
            entry_file_data = (file_data[theunpack_offset + entry.relative_offset:theunpack_offset +
                               entry.relative_offset + entry.compressed_size])
            entry_file_data = zlib.decompress(entry_file_data)
            if not write:
                if entry.name == filename:
                    return Result(entry_file_data.decode('utf-8'))
            else:
                os.makedirs(dbcdfile.replace('.dbcd', '') + '_tmp')
                file_path = os.path.join(
                    dbcdfile.replace('.dbcd', '') + '_tmp', entry.name)
                with open(file_path, 'wb') as file_object:
                    file_object.write(entry_file_data)
    except FileNotFoundError:
        pass


def writer_main(in_path, out_path):
    """ ... """
    crc = Document()
    crc_file_info = crc.createElement("Files")
    crc.appendChild(crc_file_info)
    dbcd_file_entries = 0
    dbcd_compressed_file_data = b''
    for file_name in os.listdir(in_path):
        file_path = os.path.join(in_path, file_name)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            if file_size <= 0:
                continue
            try:
                file_object = open(file_path, 'rb')
                file_data = file_object.read()
            except IOError:
                pass
            else:
                file_name_new = file_name
                file_size = 0
                compressed_size = 0
                algorithm = 0
                try:
                    compressed_file_data = zlib.compress(file_data)
                    file_size = len(file_data)
                    compressed_size = len(compressed_file_data)
                except zlib.error:
                    pass
                else:
                    dbcd_file_entries += 1
                    dbcd_compressed_file_data += compressed_file_data
                    file_data_crc32 = zlib.adler32(compressed_file_data)  & 0xffffffff # work around for issue 1202
                    crc_file_info_file_item = crc.createElement("File")
                    crc_file_info_file_item.setAttribute("Name", file_name_new)
                    crc_file_info_file_item.setAttribute("Size", str(file_size))
                    crc_file_info_file_item.setAttribute("CompressedSize", str(compressed_size))
                    crc_file_info_file_item.setAttribute("Checksum", "%08x" % file_data_crc32)
                    crc_file_info_file_item.setAttribute("FileTime", "%08x" % 0)
                    crc_file_info_file_item.setAttribute("Algorithm", str(algorithm))
                    crc_file_info.appendChild(crc_file_info_file_item)
            finally:
                if file_object is not None:
                    file_object.close()
                    file_object = None
            os.remove(file_path)
    if dbcd_file_entries > 0 and len(dbcd_compressed_file_data) > 0:
        crc_file_data = crc.toxml()
        try:
            file_object = open(out_path, 'wb')
            dbcd_header = b"DecoraterBot Config Data File V.0.1"
            dbcd_header += struct.pack(b'<25x')
            dbcd_header += struct.pack(b'<2I', dbcd_file_entries, 1)
            _size = int(len(crc_file_data))
            compressed_data = zlib.adler32(bytes(crc_file_data, 'utf-8'))
            dbcd_header += struct.pack(b'<3I', 0, compressed_data & 0xFFFFFFFF, _size)
            file_object.write(dbcd_header)
            file_object.write(bytes(crc_file_data, 'utf-8'))
            file_object.write(dbcd_compressed_file_data)
        finally:
            if file_object is not None:
                file_object.close()
                file_object = None
        os.rmdir(in_path)


def packer_main(argv):
    """
    Main Packer Program Function.
    :param argv: Arguments.
    :return: Nothing.
    """
    if len(argv) < 2:
        print("Usage:\ndbcdpact --in <Folder name> --out <dbcd file name>")
        sys.exit(2)
    try:
        options, arguments = getopt.getopt(argv, 'i:o:', ['in=', 'out='])
    except getopt.GetoptError:
        sys.exit(2)
    in_path = None
    out_path = None
    for option, argument in options:
        if option in ('i', '--in'):
            in_path = argument
        elif option in ('o', '--out'):
            out_path = argument
    if not in_path or not out_path:
        print("Usage:\ndbcdpact --in <Folder name> --out <dbcd file name>")
        sys.exit(2)
    if not os.path.isdir(in_path):
        print("Usage:\ndbcdpact --in <Folder name> --out <dbcd file name>")
        sys.exit(2)
    writer_main(in_path, out_path)
    print("File created.")
