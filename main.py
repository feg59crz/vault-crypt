from cryptography.fernet import Fernet
import argparse
from argparse import ArgumentParser
import os


def cryptFile(key, file):
    origin_file = file
    fernet = Fernet(key)
    crypt_file = file + '.crypt'

    with open(origin_file, 'rb') as f:
        original = f.read()

    encrypted = fernet.encrypt(original)

    with open(crypt_file, 'wb') as cf:
        cf.write(encrypted)

    os.remove(origin_file)


def decryptFile(key, file):
    crypt_file = file
    fernet = Fernet(key)
    if not crypt_file.endswith('.crypt'):
        print("Warning: the file '" + crypt_file +
              "' does not end as an encrypted file (.crypt)")
        return
    decrypt_file = file[:-6]

    with open(crypt_file, 'rb') as enc_file:
        encrypted = enc_file.read()

    decrypted = fernet.decrypt(encrypted)

    with open(decrypt_file, 'wb') as dec_file:
        dec_file.write(decrypted)

    os.remove(crypt_file)


def decryptFolder(key, folder):
    for i in os.listdir(folder):
        path = os.path.join(folder, i)
        if os.path.isfile(path):
            decryptFile(key, path)
        elif os.path.isdir(path):
            decryptFolder(key, path)
        else:
            print(path, "not decrypted")


def cryptFolder(key, folder):
    for i in os.listdir(folder):
        path = os.path.join(folder, i)
        if os.path.isfile(path):
            cryptFile(key, path)
        elif os.path.isdir(path):
            cryptFolder(key, path)
        else:
            print(path, "not encrypted")


def checkKey(arg_key):
    if len(arg_key) == 44:
        key = arg_key
    else:
        if checkExist(arg_key):
            key = readKey(arg_key)
        else:
            key_path = arg_key
            if not key_path.endswith('.key'):
                key_path += '.key'
            if checkExist(key_path):
                key = readKey
            else:
                raise Exception("Error: No valid key provided")
    return key


def parseCrypt(args):
    if not args.key:
        raise Exception("Error: No key provided")
    key = checkKey(args.key)

    arg_path = args.path

    if os.path.isfile(arg_path):
        cryptFile(key, arg_path)
    elif os.path.isdir(arg_path):
        cryptFolder(key, arg_path)
    else:
        raise Exception("Error: No valid Folder or File")


def parseDecrypt(args):
    if not args.key:
        raise Exception("Error: No key provided")
    key = checkKey(args.key)

    arg_path = args.path

    if os.path.isfile(arg_path):
        decryptFile(key, arg_path)
    elif os.path.isdir(arg_path):
        decryptFolder(key, arg_path)
    else:
        raise Exception("Error: No valid Folder or File")


def parsekeyGen(args):
    key = genKey()
    if args.output:
        filename = args.output
        if not filename.endswith('.key'):
            filename += '.key'
        makeKey(filename, key)
        return True
    key = str(key)
    print(key[2:-1])
    return True


def initParse():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(help="subparsers")

    parser_keygen = subparsers.add_parser('keygen')
    parser_keygen.set_defaults(func=parsekeyGen)
    parser_keygen.add_argument("-o", "--output", action='store',
                               metavar="FILENAME", dest='output',
                               help="Directs the output to a name of your choice")

    parser_crypt = subparsers.add_parser('crypt')
    parser_crypt.set_defaults(func=parseCrypt)
    parser_crypt.add_argument(
        "-k", "--key", action='store', dest="key", help="key to use to decrypt")
    parser_crypt.add_argument("path", help="File or path to crypt")

    parser_crypt = subparsers.add_parser('decrypt')
    parser_crypt.set_defaults(func=parseDecrypt)
    parser_crypt.add_argument(
        "-k", "--key", action='store', dest="key", help="key to use to decrypt")
    parser_crypt.add_argument("path", help="File or path to decrypt")

    args = parser.parse_args()
    args.func(args)
    return args


def checkExist(file):
    if os.path.exists(file):
        return True
    return False


def genKey():
    key = Fernet.generate_key()
    return key


def makeKey(file, key):
    with open(file, 'wb') as f:
        f.write(key)


def readKey(file):
    with open(file, 'r') as k:
        output = k.read()
    return output


def main():
    args = initParse()


if __name__ == '__main__':
    main()
