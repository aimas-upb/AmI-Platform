#!/usr/bin/python

##    PyTranspose
##    Copyright 2011 Michael C Smith <maxomai@gmail.com> <http://maxomai.org/>
##
##    This program is written for Python 2.x and may not work with Python 3 or
##    later.
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

##TODO:
##    Investigate/eliminate trailing line
##    Test on Windows
##    Document better; try to get docs on Soureforge.

import sys

helptext =  """Usage: transpose [OPTION] SOURCE...
Transpose one or more SOURCE files and write result to standard output. If 
no source files are set then standard input is assumed. NOTE: it is not
recommended at this time to use this utility with very large (1GB or larger)
files. 

Mandatory arguments to long options are mandatory for short options.
    -d, --delimiter=STRING      Sets STRING as the delimiter.
    -h, --help                  Print this message.
    -o, --output=FILE           Sets FILE as the output. If not set then
                                standard output is assumed.
    -t, --tab                   Use tab as the delimiter. (Default)
    -U, --unix                  Force UNIX newlines in output
    -v, --version               Print the version.
    -w, --whitespace            Use any whitespace as a delimiter. Note:
    -W, --win                   Force Windows newlines ("\r\n") in output                            the resulting output will be space-delimited.

Report bugs to maxomai@gmail.com.
Project home page: <http://www.maxomai.org/blog/pytranspose/>
My home page: <http://www.maxomai.org/>"""

version =   """transpose 0.1
Copyright (c) Michael C Smith <maxomai@gmail.com>
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law."""

def parseargs() :
    "Parses arguments for the command."

    def invalid_argument(s):
            print "Invalid argument: " + s
            print help
            exit()

    delimiter="\t"
    outfilename=""
    infilenames=[]
    mode=""
    for arg in sys.argv[1:]:
        #-d or --delimiter
        if arg.startswith('-d='):
            delimiter=arg[3:]
            ##print delimiter #debug
        elif arg.startswith('--delimiter='):
            delimiter=arg[12:]
            ##print delimiter #debug
        # -h or --help
        elif arg == "-h" or arg == "--help":
            print helptext
            exit()
        # -o or --output
        elif arg.startswith("-o="):
            outfilename=arg[3:]
            ##print arg[3:] #debug
        elif arg.startswith("--output="):
            outfilename=arg[9:]
            ##print arg[9:] #debug
        # -t or --tab
        elif arg == "-t" or arg == "--tab":
            delimiter = "\t"
        # -U or --unix
        elif arg == "-U" or arg == "--unix":
            mode="unix"
        # -v or --version
        elif arg == "-v" or arg == "--version":
            print version
            exit()
        # -w or --whitespace
        elif arg == "-w" or arg == "--whitespace":
            delimiter = None #str.split(None) tokenizes on whitespace
        # -W or --win
        elif arg == "-W" or arg == "--win":
            mode="win"
        # any other comment-like argument
        elif arg.startswith("-"):
            invalid_argument(arg)
        # Any non-comment arg is an input file name.
        else:
            infilenames.append(arg)
    return [delimiter, outfilename, infilenames, mode]


def parsefile (f, delimiter) :
    """
Takes an open file and a delimiter; returns [a,maxlength] where a
is a 2D array of tokens and maxlength is the length of the longest single row.
    """
    a = []
    a_append = a.append                         #ref to fxn; cuts call time
    maxlength = 0
    for line in f:                              #todo: optimize this
        tokens = line.rstrip().split(delimiter) #todo: optimize this
        a_append(tokens)
        if (maxlength < len(tokens)):
            maxlength = len(tokens)
    return [a, maxlength]

def parsefiles (filenames, delimiter) :
    """
Takes a list of file names and a delimiter; returns [a,maxlength] where a
is a 2D array of tokens and maxlength is the length of the longest single row.
If the list is empty then stdin is assumed.
    """
    a = []
    maxlength = 0
    a_extend=a.extend                       #ref to fxn; cuts call time
    if (len(filenames) > 0) :
        for filename in filenames:
            f = open(filename, "r")         #todo: make robust
            [_a, _maxlength] = parsefile(f, delimiter)
            if (maxlength < _maxlength):
                maxlength = _maxlength
            if(len(_a) > 0):                #do not extend with empty arrays
                a_extend(_a)                #todo: verify that this works
            f.close()
    else:
        #read from stdin
        [a, maxlength] = parsefile(sys.stdin, delimiter)
    return [a, maxlength]

def getEndline(winmode):
    "Determines the endline string based on mode, or on OS."
    if (mode=="win"):
        _result="\r\n"
    elif (mode=="unix"):
        _result="\n"    
    elif ( sys.platform.startswith("win") ):
        _result="\r\n"
    else:
        _result="\n"
    return _result

def transpose(a, maxlength, delimiter, mode):
    """
Returns a transposed array of data, with delimiters added to denote empty
cells.
    """
    if (delimiter == None):
        _delimiter = " "
    else:
        _delimiter = delimiter
    endline = getEndline(mode)              #todo: make robust
    result= []
    result_append=result.append             #ref to fxn; cuts call time
    for i in range(maxlength):
        for line in a:
            if (i < len(line)):
                result_append(line[i])
            result_append(_delimiter)
        result[len(result)-1] = endline     #remove last delim from line
    return result

#main code

[delimiter, outfilename, infilenames, mode] = parseargs()
[a, maxlength] = parsefiles(infilenames, delimiter)
result = transpose(a, maxlength, delimiter, mode)
##print result #debug
if (outfilename==""):
    print "".join(result)
else:
    #todo: make more robust
    outfile = open(outfilename, "w")
    outfile.write(''.join(result))
    outfile.flush()
    outfile.close()
