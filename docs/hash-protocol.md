# Hash protocol: `sha256-base62-v1`

The ID protocol is specified so future implementations can reproduce the same ID.

## URL normalization

Before hashing:

1. Trim surrounding whitespace.
2. Require `http` or `https`.
3. Lowercase the scheme and hostname.
4. Convert internationalized hostnames to IDNA ASCII.
5. Remove default ports (`80` for HTTP and `443` for HTTPS).
6. Use `/` when the path is empty.
7. Preserve path, query string, and fragment.
8. Reject embedded username/password credentials.

Tracking parameters are not removed. ShortRef avoids silently changing the meaning of technical-document and platform URLs.

## Hash and encoding

1. Encode the normalized URL as UTF-8.
2. Calculate SHA-256.
3. Interpret the 32-byte digest as one unsigned big-endian integer.
4. Encode it with `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`.
5. Left-pad the token with `0` to 43 characters.
6. Use the first 8 characters as the initial ID.
7. On collision, try 9, 10, 11, and 12 characters.

## Identity and migration

The hash determines the ID only at initial creation. After creation, the ID becomes a stable reference identity. Updating the destination does not recalculate or replace the ID.
