"""
Abandon all hope ye who enter. 'Tis here where madness lies.
Datatables are so fucking confusing I'm not sure where to begin.

check out what "SendProp" is.

DataTable_LoadDataTablesFromBuffer is called.
while "readonebit" is 1, do this loop.
first, a "needsDecoder" bit is read.
"RecvTable_RecvClassInfos" is called, which in turn calls RecvTable_ReadInfos.
then ReadAndAllocateString is read on the buffer. (m_pNetTableName)
then a 10-bit unsigned integer is read, amt of props in here. (m_pProps)
then there's a check for if this integer is above 0, and sets it to NULL if it's not.

prepare to read a bunch of sendprops.

5 bits are read as an unsigned integer, as the prop type.
then 16 bits for a SendProp flags are read, 11 if it's demo protocol 2.
checkity checks 

aight we done reading props
back to RecvTable_RecvClassInfos, we call DataTable_SetupReceiveTableFromSendTable
what the fuck is this
"""
class SendProp:

def ParseDatatables(datatables_to_parse):
    while (datatables_to_parse.readb(1).any()):
        needsDecoder = datatables_to_parse.any()