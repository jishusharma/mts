"""aibridge_health.py - is the DSA AI Bridge agent answering on 127.0.0.1:7181?

Exit 0 = port accepts a TCP connection and the agent replies to an OPTIONS request (any HTTP status);
exit 1 = down. Does not send the token or run any command.
"""
import socket
import sys

HOST, PORT = "127.0.0.1", 7181


def main() -> int:
    try:
        s = socket.create_connection((HOST, PORT), timeout=3)
    except OSError as e:
        print(f"aibridge: DOWN ({e})")
        return 1
    try:
        s.settimeout(3)
        s.sendall(b"OPTIONS /run HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
        data = s.recv(256)
    except OSError as e:
        print(f"aibridge: port open, no HTTP reply ({e})")
        return 1
    finally:
        s.close()
    first = data.split(b"\r\n", 1)[0].decode("ascii", "replace")
    print(f"aibridge: UP ({first})")
    return 0 if first.startswith("HTTP/") else 1


if __name__ == "__main__":
    sys.exit(main())
