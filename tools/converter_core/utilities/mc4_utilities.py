# ------------------------------------------------------------------------------------------------------------------------------------
#
#
#   This Utility contains functions used to work with MC4-Based Cheats, Encrypt MC4-Based Cheats, and Decrypt MC4-Based Cheats.
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



#######################################################################################################################################################
#                                                                                                                                                     #
#                                                      Functions Related to Decrypting MC4 to SHN                                                     #
#                                                                                                                                                     #
#######################################################################################################################################################



import base64
from Crypto.Cipher import AES



##############################################################################
#                                                                            #
#                  AES CBC Key and AES CBC IV Key Constants                  #
#                                                                            #
##############################################################################



# https://github.com/bucanero/save-decrypters/blob/master/mc4-cheat-decrypter/main.c#L13
# https://github.com/stole-panaggio/mc4-cheat-encrypter-decrypter-python-version/blob/master/mc4_cheat_decrypter.py



#######################  bucanero --> Keeping Hope Alive for 15+ Years  #######################



AES_256_CBC_KEY_MC4 = b'304c6528f659c766110239a51cl5dd9c'
AES_256_CBC_IV_MC4  = b'u@}kzW2u[u(8DWar'



##############################################################################
#                                                                            #
#                       Remove PKCS#7 Padding Function                       #
#                                                                            #
##############################################################################



'''
Source:
    https://node-security.com/posts/cryptography-pkcs-7-padding


Padding is used in certain block cipher modes (like ECB and CBC) when the plain-text needs to be a multiple of the block size.

Example:
    If the cypher is using a 16-byte block size, but the plain-text is only 9 bytes, then 7 additional bytes of padding are needed.

    The hex value `0x07` is used for the padding.

        7 bytes of padding would append `0x07` 7 times
            Example: b'\x07\x07\x07\x07\x07\x07\x07'


The last byte of decrypted text can be used to determine if padding was used.


For the 16-byte block size used by AES CBC, if the last byte of the decrypted text is 0, padding was not used (seems obvious).
If the last byte of the decrypted text is greater than 16, padding was not used.


If the last byte of the decrypted text is 16, 16 bytes of padding are used.


Said another way, if the plain-text length is a multiple of the block size, then a padding block (of size = block size) is added.


A value of 1-16 indicates that padding was used, and therefore must be removed.
'''



#######################  b'\x07\x07' --> In | b'' --> Out  #######################



def remove_pkcs7_padding(decrypted_mc4):
    last_byte = decrypted_mc4[-1]
    padding_length = last_byte
    if padding_length < 1 or padding_length > 16:
        return decrypted_mc4
    if decrypted_mc4.endswith(bytes([last_byte]) * padding_length):
        return decrypted_mc4[:-padding_length]
    else:
        return decrypted_mc4



##############################################################################
#                                                                            #
#                     Decrypt MC4 to SHN (XML) Function                      #
#                                                                            #
##############################################################################



'''
1. Base64 decode encrypted data
2. AES-256-CBC decrypt
3. Remove PKCS#7 padding
4. Replace Escaped Reserve Characters
5. Remove Leading and Trailing Junk Data
'''



from utilities.catch_exceptions_utilities import escape_ampersand
from utilities.catch_exceptions_utilities import remove_xml_junk_data
from utilities.catch_exceptions_utilities import replace_escaped_reserved_characters



#######################  MC4 --> In | SHN (XML) --> Out  #######################



def decrypt_mc4_to_shn(mc4_data):
    try:
        bin_data = base64.b64decode(mc4_data)
    except Exception:
        print('Base64 Decode Error!')
        return None
    cipher = AES.new(AES_256_CBC_KEY_MC4, AES.MODE_CBC, IV=AES_256_CBC_IV_MC4)
    decrypted_mc4 = cipher.decrypt(bin_data)
    padding_removed = remove_pkcs7_padding(decrypted_mc4)
    decrypted_string = padding_removed.decode('utf-8', errors='ignore')
    replaced_escaped = replace_escaped_reserved_characters(decrypted_string)
    escaped_ampersands = escape_ampersand(replaced_escaped)
    normalize_string = remove_xml_junk_data(escaped_ampersands)
    return normalize_string



##############################################################################
#                                                                            #
#                        Add PKCS#7 Padding Function                         #
#                                                                            #
##############################################################################



#######################  b'' --> In | b'\x07\x07' --> Out  #######################



def add_pkcs7_padding(shn_data, block_size=16):
    shn_as_bytes = shn_data.encode()
    padding_length = block_size - (len(shn_as_bytes) % block_size)
    if padding_length == 0:
        padding_length = block_size
    padding_added = shn_as_bytes + bytes([padding_length] * padding_length)
    return padding_added



##############################################################################
#                                                                            #
#                     Encrypt SHN (XML) to MC4 Function                      #
#                                                                            #
##############################################################################



'''
1. Add PKCS#7 padding
2. AES-256-CBC Encrypt
3. Base64 encode encrypted data
'''



#######################. SHN (XML) --> In | MC4 --> Out  #######################



def encrypt_shn_to_mc4(shn_data):

    padding_added = add_pkcs7_padding(shn_data, 16)
    cipher = AES.new(AES_256_CBC_KEY_MC4, AES.MODE_CBC, IV=AES_256_CBC_IV_MC4)
    encrypted_mc4 = cipher.encrypt(padding_added)
    try:
        base64_encoded = base64.b64encode(encrypted_mc4)
    except Exception:
        print('Base64 Error!')
        return shn_data
    return base64_encoded



# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   Development Notes:
#
#
#       >>> bin_data
#       b'\x02\x02\x87<\xbcY\xc1\x9f\xb6a\xf6,\x96b\xd4\\l\x94 \x92\xb45)\xfa\xd7_\r\x8a\x9c1(L\xab,>\x05\x96n\xdf\xc3\x87B\xb5?\x8b\x1b\x9a+q.K\xa5\x1cn\xc8#\xdd\'7\x97
#       \xa1\x02%PE\xea6\x98\x83+\x98\x1e\xecxdGPz\xf5\x10\xb1\x8dy\x81\x00\xab\x067\x05\x96\x07G(;g\x8c\x9aLi\xec\xfeoj\x89-\x84Ss\xba|C\x8c\xb8\xbf\nr\xd7j\x0e\\M\xf7
#       \xf0^\xd9\xfd\xd81}\xab\xdf\x01\xa7\xd6\x91\xebk\x1ff\x03c\xe0\x08i\x9b\x90\xfa\xddl\x99"\xfb%w\xff\x8e\x0bB\xc3\xf6\x03\xf7cia\t\x12~\xae\x1eU\xf9\xad\x00zJ
#       \x87M0\'\xab.\xb1\\yQ/A\xd6\xde\x0e;\xdd\xaf\xd5\x9et#\xce\xb3+\x91\xcb\xe4\xc3\xa9-\xb7\xca \xc9+)\x18\xdf\xad\x98\xd0\x11Fjq\xd8\xf7\x8c\x9c\x12.\x93\x02
#       \xa8\r{\xaf[G\xb3\x0f\x98\xe8\x9cz\x1bZ$\xec\x00\xc8\xc9\xa2\xde6\xef\x1d!u\x82G&4c\xe8\xf9~*\xdffg\x84\xe4\xf2S\xdc\xb68\x17[\xcb3\x97\xf7\xe7\x1d\x15\xcb\xd2
#       \xf9b)\xa9\tb\xc1\xcd#\x10\xc9\x10\x16\x0e\xf6\x87\xf8\x80\x12\xca\x884\x96\x1d\x10\xef\xe6\x8d%\x15(s\x8aD\xd9\xf7\xb0\xcen\x08\x0f\x98eN\xfc\xb4\x05\xfdi\xdeR
#       \xd6<f\xf5\x16\xd6\xca\xcd\x87\xf9\x95\xf3\x12P\xf4|x\xd3\xaf6uv\xf0\xb2\x8b\xd0pz\x16v`[/\xd7\xf8\xd4\xef`\xf3\xf4\xa7\x81N\xb55\xa3\xd0\x0c\xb1\x96\x8bC
#       \xfe\x03\xd9ku\xf5E\x9c\xedp\xe9\xa9i6\x8a\xc2\xd6\x8au\xc7\xf8\x9d\x88\xdb\x7fR\x8e9\xb3\xda%b\x87\xf7\xe6\xcd\xf0\x9a\x9a\xb8\x839\x91f\xc1;-t\x19\xec\x90
#       \xf4\x185n\x9d\xe3\xfbj\xf5\xa9_\xb82\xdf\xc6\x89\xd5H\xcd\xc3\x0ea\xd9\x86\x86:C+\r\xb7\x93x\xbf\x1f\x96%\x03Jt\xe5\xf3\xfc\xeab0\xf4L\xd9A"\xc4n\x0eG\xee
#       \xd5W\xa3\xbe\x05Zl@\xb5\x1d\xe18]\x83\xd7\x0bI\x11]?\x01\x87,7\x8f,*\xb50\xd3\xe0\xb8\xc1\x8e\xc6\xbc\xd48\xbe4\xac}Q\n\xb7[a
#       \x94\x94\xd2o0\x8a\x8dvv\x0f\xfa\xfd\xac\xe2|\x8eA\x8b'
#       >>>
#
#
#       >>> decrypted_mc4 = cipher.decrypt(bin_data)
#       >>> decrypted_mc4
#       b'<?xml version="1.0" encoding="utf-16"?>\r\n<Trainer xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#       Game="Nier Automata" Moder="Skal" Cusa="CUSA04480" Version="01.06" Process="eboot.bin">\r\n  <Genres Name="Action" />\r\n  <Genres Name="Adventure" />\r\n
#       <Items />\r\n  <Cheat Text="One hit kill">\r\n    <Cheatline>\r\n      <Offset>3D471B</Offset>\r\n      <Section>0</Section>\r\n      <ValueOn>4D-29-A6-50-08-00-00</ValueOn>\r\n
#       <ValueOff>41-29-9E-50-08-00-00</ValueOff>\r\n    </Cheatline>\r\n  </Cheat>\r\n</Trainer>\x07\x07\x07\x07\x07\x07\x07'
#       >>>
#
#
#       >>> padding_removed = remove_pkcs7_padding(decrypted_mc4)
#       >>> padding_removed
#       b'<?xml version="1.0" encoding="utf-16"?>\r\n<Trainer xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#       Game="Nier Automata" Moder="Skal" Cusa="CUSA04480" Version="01.06" Process="eboot.bin">\r\n  <Genres Name="Action" />\r\n  <Genres Name="Adventure" />\r\n
#       <Items />\r\n  <Cheat Text="One hit kill">\r\n    <Cheatline>\r\n      <Offset>3D471B</Offset>\r\n      <Section>0</Section>\r\n
#       <ValueOn>4D-29-A6-50-08-00-00</ValueOn>\r\n      <ValueOff>41-29-9E-50-08-00-00</ValueOff>\r\n    </Cheatline>\r\n  </Cheat>\r\n</Trainer>'
#       >>>
#
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

