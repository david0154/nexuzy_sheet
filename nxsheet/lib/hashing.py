# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# Developed by Nexuzy Lab
#
# Nexuzy Sheet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Nexuzy Sheet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# License: GNU General Public License v3.0
# https://www.gnu.org/licenses/gpl-3.0.html
#
# Project: Nexuzy Sheet
# Developer: Nexuzy Lab
# Copyright: © 2026 Nexuzy Lab
# --------------------------------------------------------------------

"""

File hashing services

**Provides**

 * :func:`genkey` - Generates hash key
 * :func:`sign` - Returns a signature for a given file
 * :func:`verify` - Verifies file against signature

"""

import ast

from hashlib import blake2b
from hmac import compare_digest
import secrets


def genkey(nbytes: int = 64) -> bytes:
    """Returns a random byte sting that may be used as signature key

    :param nbytes: Length of key
    :return: Random byte string of length nbytes

    """

    if nbytes > blake2b.MAX_KEY_SIZE:
        raise ValueError("nbytes exceeds maximum allowed key size for BLAKE2b")

    return secrets.token_bytes(nbytes)


def sign(data: bytes, key: bytes) -> bytes:
    """Returns signature for file using blake2b

    Note: 64 bytes is the maximum that is supported in Python's BLAKE2b

    :param data: Data to be signed
    :param key: Signature key, len(key) <= 64
    :return: File signature hexdigest, encoded in utf-8

    """

    if not data:
        raise ValueError("No data provided for signing")

    if not key:
        raise ValueError("No signature key defined")

    if not isinstance(key, bytes):
        key = ast.literal_eval(key)

    if len(key) > blake2b.MAX_KEY_SIZE:
        key = key[:blake2b.MAX_KEY_SIZE]
        raise UserWarning("Key is too long and has been truncated")

    signature = blake2b(digest_size=64, key=key)
    signature.update(data)

    return signature.hexdigest().encode('utf-8')


def verify(data: bytes, signature: bytes, key: bytes) -> bool:
    """Verifies a signature

    :param data: Data to be verified
    :param signature: Signature for verification
    :param key: Signature key, len(key) <= 64
    :return: True if verification was successful else False

    """

    data_signature = sign(data, key)
    return compare_digest(data_signature, signature)
