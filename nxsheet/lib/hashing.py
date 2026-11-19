# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# Developed by Nexuzy Lab
#
# Nexuzy Sheet is released under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# License: MIT License
# https://opensource.org/licenses/MIT
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
