# ------------------------------------------------------------------------------------------------------------------------------------
#
#
#   During repo development, multiple issues have been found in existing Online Cheat Code databases, particularly in the SHN (XML) files.
#   This Utility is a collection of functions used to catch these issues as exceptions, and normalize and sanitize the file data.
#
#
# ------------------------------------------------------------------------------------------------------------------------------------



##############################################################################
#                                                                            #
#                      Enable Absolute Imports Function                      #
#                                                                            #
##############################################################################



#######################  Absolute Imports > Relative Imports  #######################



def enable_absolute_imports():
    import sys
    from os import getcwd
    PWD = getcwd()
    if PWD not in sys.path:
        sys.path.append(PWD)



enable_absolute_imports()



##############################################################################
#                                                                            #
#                    Escape Ampersand Character Function                     #
#                                                                            #
##############################################################################



'''
Certain characters in XML are reserved for Markup.
The Ampersand is particularly important in XML.
Reserved Characters begin with the Ampersand `&` and end with the Semicolon `;`.

    • &lt;   <
    • &gt;   >
    • &amp;  &
    • &apos; '
    • &quot; "


When the Ampersand is used for text in XML files, it must be escaped or it will cause errors.
Unfortunately, the Ampersand is commonly used to mean 'and'.

    Example:
        Infinite Ammo & Items
        Infinite Ammo and Items

Unless properly escaped, the Ampersand will results in `xml.parsers.expat.ExpatError: not well-formed (invalid token)`.
The following function finds the Ampersand in text within the file and properly escapes it.

# https://stackoverflow.com/a/60244529
'''



#######################  '&' in File --> In | Escaped '&' --> Out  #######################



def escape_ampersand(file_data):
    if '&' in file_data:
        # Escape only bare ampersands so existing entities like &amp; are preserved.
        normalized = re.sub(r'&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z][A-Za-z0-9]+;)', '&amp;', file_data)
    else:
        normalized = file_data
    return normalized



##############################################################################
#                                                                            #
#             Remove Leading and Trailing XML Junk Data Function             #
#                                                                            #
##############################################################################



'''
SHN files should begin with the XML Declaration followed by the Opening Tag.
They should end with a Closing Tag whose text matches the Opening Tag.

Example:

    <?xml version="1.0" encoding="utf-16"?>
    <Trainer>
        Cheat Stuff
    </Trainer>

For unknown reasons, many of the SHN files have `junk data` after the Closing Tag.
One SHN file was found to being with a `?` rather than the `<`.

This `junk data` causes XML Parser Errors.

The following functions uses a Regular Expression patter to match the data between the
XML Declaration and the Closing Tag.

The junk data still resides in the original file, but the when the file is read in as a string,
this RegEx Pattern will skip the `junk data`.
'''



import re



#######################  Leading and Trailing Junk-Data --> In | Valid XML --> Out  #######################



def remove_xml_junk_data(file_data):
    match = re.search(r'<\?xml.*</Trainer>', file_data, flags=re.DOTALL)
    if match:
        normalized = match.group()
    else:
        normalized = file_data
    return normalized



##############################################################################
#                                                                            #
#              Replace Escaped XML Reserve Characters Function               #
#                                                                            #
##############################################################################



'''
For unknown reasons, many of the MC4 files, once decrypted, escape the XML reserved characters.

    • &lt;   <
    • &gt;   >
    • &amp;  &
    • &apos; '
    • &quot; "

Complicating things further, the quote characters are literally escaped using a backslash character

    Example:
        &lt;?xml version=\\&quot;1.0\\&quot; encoding=\\&quot;utf-16\\&quot;?&gt;


The function below replaces the escaped reserved characters in the XML tags with the non-escaped character.
Ampersand is deliberately skipped, as it might be escaped intentionally.


Development Note:
    During development, this reduced the number of File Exceptions when bulk parsing MC4 files from 258 to 32.
    By passing the remained 32 File Exceptions through the `remove_xml_junk_data` function,
    the number of File Exceptions was reduced to 13, with the majority of remaining exceptions being
    `Data must be padded to 16 byte boundary in CBC mode`.
'''



#######################  Escaped XML Reserved Characters --> In | Valid XML --> Out  #######################



def replace_escaped_reserved_characters(file_data):
    normalized = file_data.replace('&lt;', '<').replace('&gt;', '>').replace('\\&quot;', '"').replace("\\&apos;", "'").replace('&quot;', '"').replace("&apos;", "'")
    return normalized



##############################################################################
#                                                                            #
#                    Reverse Add PKCS#7 Padding Function                     #
#                                                                            #
##############################################################################



'''
MC4 files are SHN files that have been PKCS#7 padded, AES Encrypted, and Base64 encoded.

    SHN to MC4 Encryption Steps:
        1. Add PKCS#7 padding
        2. AES-256-CBC Encrypt
        3. Base64 encode encrypted data

Decrypting MC4 files to SHN is simply the reverse:

    MC4 to SHN Decryption Steps:
        1. Base64 decode encrypted data
        2. AES-256-CBC decrypt
        3. Remove PKCS#7 padding

During development and bulk parsing, some of the decrypted MC4 files raise an exception error
`Data must be padded to 16 byte boundary in CBC mode` during the decryption step.

This is baffling as the file should not have been able to be encrypted without the padding.
AES CBC uses a block size of 16, and so data must be padded to the byte boundary.

    Exception - MC4 to SHN Decryption Steps:
        1. Base64 decode encrypted data
        2. Add PKCS#7 padding
        3. AES-256-CBC decrypt
        4. Remove PKCS#7 padding


While this results in a file that is decrypted, there is still remaining junk data that will cause
XML parsing to fail.  Given that the input itself was not properly created, we run headlong into the
'Garbage In / Garbage Out' principle.

The MC4 files that had this issue were finally fixed by hand, though automation was used to
cycle through the four steps above and save the decrypted data to an SHN file.


One example is the following MC4 cheat file along with its commit.
In fact, several, but not all, of the files in this commit had the same issue.

    https://github.com/GoldHEN/GoldHEN_Cheat_Repository/blob/main/mc4/CUSA33388_01.04_2.mc4
    https://github.com/GoldHEN/GoldHEN_Cheat_Repository/commit/54eec8338d32e5f7b71d3a9f04812ff50bdc93a7


Manually fixing these files and their corresponding XML decryption files is quite time consuming.
Perhaps someone can work out what the junk data is and what caused it. 
It was truly gibberish, as though decryption failed. It had to be removed by hand for each file.
'''



#######################  b'' --> In | b'\x07\x07' --> Out  #######################



def reverse_add_pkcs7_padding(mc4_as_bytes, block_size=16):
    padding_length = block_size - (len(mc4_as_bytes) % block_size)
    if padding_length == 0:
        padding_length = block_size
    padding_added = mc4_as_bytes + bytes([padding_length] * padding_length)
    return padding_added
