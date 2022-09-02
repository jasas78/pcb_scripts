#
#  /home/dyn/.config/kicad/6.0/eeschema.json
# "command": "\"/usr/bin/python3\" \"${KIPRJMOD}/script_kicad/cvs_bom_gen001_h3d.py\" \"%I\" \"%O.csv\"",
# 
# Example python script to generate a BOM from a KiCad generic netlist
#
# Example: Sorted and Grouped CSV BOM
#

"""
    @package
    Output: CSV (comma-separated)
    Grouped By: Value
    Sorted By: Ref
    Fields: Item, Qty, Reference(s), Value, LibPart, Footprint, Datasheet, all additional symbol fields

    Outputs ungrouped components first, then outputs grouped components.

    Command line:
    python "pathToFile/bom_csv_grouped_by_value.py" "%I" "%O.csv"
"""

from __future__ import print_function

import csv
import sys
import os

path01 = '/usr/share/kicad/plugins/'
if os.path.isdir(path01) :
    sys.path.append(path01)
#else:
#    print( "error 02" )

path02 = 'C:/Program Files/KiCad/6.0/bin/scripting/plugins/'
if os.path.isdir(path02) :
    sys.path.append(path02)
#else:
#    print( "error 12" )

# Import the KiCad python helper module and the csv formatter
import kicad_netlist_reader
#import kicad_netlist_reader_h3d
import kicad_utils

# A helper function to convert a UTF8/Unicode/locale string read in netlist
# for python2 or python3 (Windows/unix)
def fromNetlistText( aText ):
    currpage = sys.stdout.encoding      #the current code page. can be none
    if currpage is None:
        return aText
    if currpage != 'utf-8':
        try:
            return aText.encode('utf-8').decode(currpage)
        except UnicodeDecodeError:
            return aText
    else:
        return aText

def myEqu(self, other):
    """myEqu is a more advanced equivalence function for components which is
    used by component grouping. Normal operation is to group components based
    on their value and footprint.

    In this example of a custom equivalency operator we compare the
    value, the part name and the footprint.
    """
    result = True
    if self.getValue() != other.getValue():
        result = False
    elif self.getPartName() != other.getPartName():
        result = False
    elif self.getFootprint() != other.getFootprint():
        result = False

    return result

# Override the component equivalence operator - it is important to do this
# before loading the netlist, otherwise all components will have the original
# equivalency operator.
kicad_netlist_reader.comp.__eq__ = myEqu
#kicad_netlist_reader_h3d.comp.__eq__ = myEqu

if len(sys.argv) != 3:
    print("Usage ", __file__, "<generic_netlist.xml> <output.csv>", file=sys.stderr)
    sys.exit(1)


# Generate an instance of a generic netlist, and load the netlist tree from
# the command line option. If the file doesn't exist, execution will stop
net = kicad_netlist_reader.netlist(sys.argv[1])
#net = kicad_netlist_reader_h3d.netlist(sys.argv[1])

# Open a file to write to, if the file cannot be opened output to stdout
# instead
try:
    f = kicad_utils.open_file_write(sys.argv[2], 'w')
except IOError:
    e = "Can't open output file for writing: " + sys.argv[2]
    print( __file__, ":", e, sys.stderr )
    f = sys.stdout

# subset the components to those wanted in the BOM, controlled
# by <configure> block in kicad_netlist_reader.py
components = net.getInterestingComponents()

compfields = net.gatherComponentFieldUnion(components)
partfields = net.gatherLibPartFieldUnion()

# remove Reference, Value, Datasheet, and Footprint, they will come from 'columns' below
partfields -= set( ['Reference', 'Value', 'Datasheet', 'Footprint'] )

columnset = compfields | partfields     # union

# prepend an initial 'hard coded' list and put the enchillada into list 'columns'
columns = ['Item', 'Qty', 'Reference(s)', 'Value', 'LibPart', 'Footprint', 'Datasheet'] + sorted(list(columnset))
columns = ['Idx', 'Qty', 'Ref', 'PartNum', 'Part', 'libSch', 'libFootprint' ]
columns = ['libSch', 'libFootprint', 'Qty', 'Idx', 'PartNum', 'Ref', 'Value', ]

# Create a new csv writer object to use as the output formatter
out = csv.writer( f, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL )

# override csv.writer's writerow() to support encoding conversion (initial encoding is utf8):
def writerow( acsvwriter, columns ):
    utf8row = []
    for col in columns:
        utf8row.append( fromNetlistText( str(col) ) )
    acsvwriter.writerow( utf8row )

# Output a set of rows as a header providing general information
title01 = ['libSch', 'libFootprint', 'Qty', 'Idx', 'PartNum', 'Ref', 'Value', ]
title02 = ['idx', 'PartSource', 'PartNum', 'PartDesc', 'Qty', 'Total', 'RefDes', 'PartMfg', 'PartMfgNumber']
writerow( out, title02 )
writerow( out, [] )                        # blank line
writerow( out, ['Date:', net.getDate()] )
writerow( out, ['Tool:', net.getTool()] )
writerow( out, ['Generator:', sys.argv[0]] )
writerow( out, ['Component Count:', len(components)] )
writerow( out, [] )
writerow( out, ['Individual Components1:'] )
writerow( out, [] )                        # blank line
writerow( out, columns )

# Output all the interesting components individually first:
row = []
idx01 = 0
for c in components:
    del row[:]
    idx01 += 1

    row.append( c.getLibName() + ":" + c.getPartName() ) # LibPart
    #row.append( c.getDescription() )
    row.append( c.getFootprint() )
#    row.append( c.getDatasheet() )
    row.append('')                                      # Qty is always 1, why print it

    row.append(idx01)                                      # item is blank in individual table
    row.append( c.getField("PartNum") )                          # Value
    row.append( c.getRef() )                            # Reference
    #row.append( c.getPartNum() )                          # Value
    row.append( c.getValue() )                          # Value


    # from column 7 upwards, use the fieldnames to grab the data
#    for field in columns[7:]:
#        row.append( c.getField( field ) );

    writerow( out, row )


writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line

######################################################## middle line 002 : begin

writerow( out, ['','','','Collated Components2:'] )
writerow( out, [] )                        # blank line
writerow( out, title01 )                   # reuse same title02



# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
grouped = net.groupComponents(components)

# Output component information organized by group, aka as collated:
idx02 = 0
cnt02 = 0
for group in grouped:
    del row[:]
    refs = ""
    idx02 += 1

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if len(refs) > 0:
            refs += ", "
        refs += component.getRef()
        c = component

    row.append( c.getLibName() + ":" + c.getPartName() )
    row.append( net.getGroupFootprint(group) )
    #row.append( net.getGroupDatasheet(group) )
    row.append( len(group) )
    cnt02 += len(group) 

    # Fill in the component groups common data
    # columns = ['Item', 'Qty', 'Reference(s)', 'Value', 'LibPart', 'Footprint', 'Datasheet'] + sorted(list(columnset))
    row.append( idx02 )
    row.append( c.getField("PartNum") )                          # Value
    #row.append( c.getPartNum() )                          # Value
    row.append( refs );
    row.append( c.getValue() )

    # from column 7 upwards, use the fieldnames to grab the data
    #for field in columns[7:]:
    #    row.append( net.getGroupField(group, field) );

    writerow( out, row  )

del row[:]
row.append( cnt02 )
row.append( cnt02 )
row.append( cnt02 )
writerow( out, row  )
######################################################## middle line 002 : end

######################################################## middle line 003 : begin
row = []
#del row[:]

writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, ['','','Full_list','Collated Components3: Total Qty == Qty * 5 + 2 '] )
writerow( out, [] )                        # blank line
writerow( out, title02 )                   # reuse same title02



# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
grouped = net.groupComponents(components)

# Output component information organized by group, aka as collated:
idx23 = 0
cnt22 = 0
cnt23 = 0
for group in grouped:
    del row[:]
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if len(refs) > 0:
            refs += ", "
        refs += component.getRef()
        c = component

    row.append( idx23 + 1)

    #row.append( c.getField("source") )                   # source
    cvv = c.getField("source") 
    if "" == cvv :
        cvv = c.getField("source") 
    if "" == cvv :
        row.append( "Digikey-" )                          # default source
    else:
        row.append( cvv )                                 # real source

    partNumber = c.getField("PartNum") 
    if "" == partNumber :
        partNumber = "noPartNumber"
    row.append( partNumber )                          # partNumber

    partDesc = c.getField("PartDesc") 
    if "" == partDesc :
        partDesc = c.getField("partdesc") 
    if "" == partDesc :
        partDesc = c.getField("desc") 
    if "" == partDesc :
        partDesc = c.getField("Desc") 
    if "" == partDesc :
        partDesc = c.getField("DESC") 
    if "" == partDesc :
        partDesc = "noPartDesc"
    row.append( partDesc )                          # partDesc

    qtY = len(group) 
    row.append( qtY )
    qtY2 = qtY * 5 + 2 
    row.append( qtY2 )

    row.append( refs );

    partMfg = c.getField("PartMfg") 
    if "" == partMfg :
        partMfg = c.getField("Mfg") 
    if "" == partMfg :
        partMfg = "no_Mfg_Info" 
    row.append( partMfg )                          # partMfg

    mfgNum = c.getField("MfgNum") 
    if "" == mfgNum :
        mfgNum = c.getField("Mfg") 
    if "" == mfgNum :
        mfgNum = partNumber
        #mfgNum = "no_Mfg_Info" 
    row.append( mfgNum )                          # mfgNum

    partValue = c.getValue()

    idx23 += 1
    cnt22 += qtY 
    cnt23 += qtY2
    writerow( out, row  )

del row[:]
row.append( "" )
row.append( "" )
row.append( "" )
row.append( "single_PCB_parts_amount" )
row.append( cnt22 )
row.append( "" )
row.append( "total_PCB_parts_amount" )
row.append( cnt23 )
writerow( out, row  )
######################################################## middle line 003 : end

######################################################## middle line 004 : begin
row = []
#del row[:]

writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, ['','','Installed_list','Collated Components4: Total Qty == Qty * 5 + 2 '] )
writerow( out, [] )                        # blank line
writerow( out, title02 )                   # reuse same title02



# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
grouped = net.groupComponents(components)

# Output component information organized by group, aka as collated:
idx43 = 0
cnt42 = 0
cnt43 = 0
for group in grouped:
    del row[:]
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if len(refs) > 0:
            refs += ", "
        refs += component.getRef()
        c = component

    row.append( idx43 + 1)

    #row.append( c.getField("source") )                   # source
    cvv = c.getField("source") 
    if "" == cvv :
        cvv = c.getField("source") 
    if "" == cvv :
        row.append( "Digikey-" )                          # default source
    else:
        row.append( cvv )                                 # real source

    partNumber = c.getField("PartNum") 
    if "" == partNumber :
        partNumber = "noPartNumber"
    row.append( partNumber )                          # partNumber

    partDesc = c.getField("PartDesc") 
    if "" == partDesc :
        partDesc = c.getField("partdesc") 
    if "" == partDesc :
        partDesc = c.getField("desc") 
    if "" == partDesc :
        partDesc = c.getField("Desc") 
    if "" == partDesc :
        partDesc = c.getField("DESC") 
    if "" == partDesc :
        partDesc = "noPartDesc"
    row.append( partDesc )                          # partDesc

    qtY = len(group) 
    row.append( qtY )
    qtY2 = qtY * 5 + 2 
    row.append( qtY2 )

    row.append( refs );

    partMfg = c.getField("PartMfg") 
    if "" == partMfg :
        partMfg = c.getField("Mfg") 
    if "" == partMfg :
        partMfg = "no_Mfg_Info" 
    row.append( partMfg )                          # partMfg

    mfgNum = c.getField("MfgNum") 
    if "" == mfgNum :
        mfgNum = c.getField("Mfg") 
    if "" == mfgNum :
        mfgNum = partNumber
        #mfgNum = "no_Mfg_Info" 
    row.append( mfgNum )                          # mfgNum

    partValue = c.getValue()

    ii4=partNumber.find('DNP')
    jj4=len(partNumber)
    if partNumber == 'DNP' or 0 == ii4 or 3 == (jj4 - ii4) :
        del row[:] #do nothing
    else:
        idx43 += 1
        cnt42 += qtY 
        cnt43 += qtY2
        writerow( out, row  )
        if partNumber == 'noPartNumber' and "" != partValue :
            del row[:] #do nothing
            row.append( idx43 );
            row.append( "unknown" );
            row.append( partValue );
            row.append( "<<--This_is_a_very_special_part-->>" );
            row.append( 0 );
            row.append( 0 );
            row.append( "ZZZZZZZZZZZZZ" );
            row.append( "ZZZZZZZZZZZZZ" );
            row.append( "ZZZZZZZZZZZZZ" );
            writerow( out, row  )

del row[:]
row.append( "" )
row.append( "" )
row.append( "" )
row.append( "single_PCB_parts_amount" )
row.append( cnt42 )
row.append( "" )
row.append( "total_PCB_parts_amount" )
row.append( cnt43 )
writerow( out, row  )
######################################################## middle line 004 : end

######################################################## middle line 005 : begin
row = []
#del row[:]

writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, ['','','DNP_list','Collated Components4: Total Qty == Qty * 5 + 2 '] )
writerow( out, [] )                        # blank line
writerow( out, title02 )                   # reuse same title02



# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
grouped = net.groupComponents(components)

# Output component information organized by group, aka as collated:
idx53 = 0
cnt52 = 0
cnt53 = 0
for group in grouped:
    del row[:]
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if len(refs) > 0:
            refs += ", "
        refs += component.getRef()
        c = component

    row.append( idx53 + 1)

    #row.append( c.getField("source") )                   # source
    cvv = c.getField("source") 
    if "" == cvv :
        cvv = c.getField("source") 
    if "" == cvv :
        row.append( "Digikey-" )                          # default source
    else:
        row.append( cvv )                                 # real source

    partNumber = c.getField("PartNum") 
    if "" == partNumber :
        partNumber = "noPartNumber"
    row.append( partNumber )                          # partNumber

    partDesc = c.getField("PartDesc") 
    if "" == partDesc :
        partDesc = c.getField("partdesc") 
    if "" == partDesc :
        partDesc = c.getField("desc") 
    if "" == partDesc :
        partDesc = c.getField("Desc") 
    if "" == partDesc :
        partDesc = c.getField("DESC") 
    if "" == partDesc :
        partDesc = "noPartDesc"
    row.append( partDesc )                          # partDesc

    qtY = len(group) 
    row.append( qtY )
    qtY2 = qtY * 5 + 2 
    row.append( qtY2 )

    row.append( refs );

    partMfg = c.getField("PartMfg") 
    if "" == partMfg :
        partMfg = c.getField("Mfg") 
    if "" == partMfg :
        partMfg = "no_Mfg_Info" 
    row.append( partMfg )                          # partMfg

    mfgNum = c.getField("MfgNum") 
    if "" == mfgNum :
        mfgNum = c.getField("Mfg") 
    if "" == mfgNum :
        mfgNum = partNumber
        #mfgNum = "no_Mfg_Info" 
    row.append( mfgNum )                          # mfgNum

    partValue = c.getValue()

    ii4=partNumber.find('DNP')
    jj4=len(partNumber)
    if not(partNumber == 'DNP' or 0 == ii4 or 3 == (jj4 - ii4)) :
        del row[:] #do nothing
    else:
        idx53 += 1
        cnt52 += qtY 
        cnt53 += qtY2
        writerow( out, row  )
        if partNumber == 'noPartNumber' and "" != partValue :
            del row[:] #do nothing
            row.append( idx53 );
            row.append( "unknown" );
            row.append( partValue );
            row.append( "<<--This_is_a_very_special_part-->>" );
            row.append( 0 );
            row.append( 0 );
            row.append( "ZZZZZZZZZZZZZ" );
            row.append( "ZZZZZZZZZZZZZ" );
            row.append( "ZZZZZZZZZZZZZ" );
            writerow( out, row  )

del row[:]
row.append( "" )
row.append( "" )
row.append( "" )
row.append( "single_PCB_parts_amount" )
row.append( cnt52 )
row.append( "" )
row.append( "total_PCB_parts_amount" )
row.append( cnt53 )
writerow( out, row  )
######################################################## middle line 005 : end

######################################################## middle line 006 : begin
row = []
#del row[:]

writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
writerow( out, ['','','DNP_expend_list','Collated Components4: Total Qty == Qty * 5 + 2 '] )
writerow( out, [] )                        # blank line
writerow( out, title02 )                   # reuse same title02



# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
grouped = net.groupComponents(components)

# Output component information organized by group, aka as collated:
idx63 = 0
cnt62 = 0
cnt63 = 0
for group in grouped:
    del row[:]
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if len(refs) > 0:
            refs += ", "
        refs += component.getRef()
        c = component


    #row.append( c.getField("source") )                   # source
    cvv = c.getField("source") 
    if "" == cvv :
        cvv = c.getField("source") 
    if "" == cvv :
        cvv = "Digikey-"                                  # default source

    partNumber = c.getField("PartNum") 
    if "" == partNumber :
        partNumber = "noPartNumber"

    partDesc = c.getField("PartDesc") 
    if "" == partDesc :
        partDesc = c.getField("partdesc") 
    if "" == partDesc :
        partDesc = c.getField("desc") 
    if "" == partDesc :
        partDesc = c.getField("Desc") 
    if "" == partDesc :
        partDesc = c.getField("DESC") 
    if "" == partDesc :
        partDesc = "noPartDesc"

    qtY = len(group) 
    qtY2 = qtY * 5 + 2 

    partMfg = c.getField("PartMfg") 
    if "" == partMfg :
        partMfg = c.getField("Mfg") 
    if "" == partMfg :
        partMfg = "no_Mfg_Info" 

    mfgNum = c.getField("MfgNum") 
    if "" == mfgNum :
        mfgNum = c.getField("Mfg") 
    if "" == mfgNum :
        mfgNum = partNumber
        #mfgNum = "no_Mfg_Info" 

    partValue = c.getValue()

    ii4=partNumber.find('DNP')
    jj4=len(partNumber)
    if (partNumber == 'DNP' or 0 == ii4 or 3 == (jj4 - ii4)) :
        partNumber = "DNP"
        partDesc   = "DNP"
        #refs       = "DNP"
        mfgNum     = "DNP"

    idx63 += 1
    cnt62 += qtY 
    cnt63 += qtY2

    row.append( idx63 )
    row.append( cvv )                                 # real source
    row.append( partNumber )                          # partNumber
    row.append( partDesc )                          # partDesc
    row.append( qtY )
    row.append( qtY2 )
    row.append( refs );
    row.append( partMfg )                          # partMfg
    row.append( mfgNum )                          # mfgNum

    writerow( out, row  )

    if partNumber == 'noPartNumber' and "" != partValue :
        del row[:] #do nothing
        row.append( idx63 );
        row.append( "unknown" );
        row.append( partValue );
        row.append( "<<--This_is_a_very_special_part-->>" );
        row.append( 0 );
        row.append( 0 );
        row.append( "ZZZZZZZZZZZZZ" );
        row.append( "ZZZZZZZZZZZZZ" );
        row.append( "ZZZZZZZZZZZZZ" );
        writerow( out, row  )

del row[:]
row.append( "" )
row.append( "" )
row.append( "" )
row.append( "single_PCB_parts_amount" )
row.append( cnt62 )
row.append( "" )
row.append( "total_PCB_parts_amount" )
row.append( cnt63 )
writerow( out, row  )
######################################################## middle line 006 : end

writerow( out, [] )                        # blank line
writerow( out, [] )                        # blank line
f.close()
