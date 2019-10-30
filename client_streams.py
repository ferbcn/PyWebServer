import asyncio
import urllib.parse
import sys

async def print_http_headers(url, port):
    url = urllib.parse.urlsplit(url)
    if url.scheme == 'https':
        reader, writer = await asyncio.open_connection(
            url.hostname, 443, ssl=True)
    else:
        readers, writers = [], []
        for i in range(100):
            reader, writer = await asyncio.open_connection(url.hostname, port)
            readers.append(reader)
            writers.append(writer)

            # Leav connections open

        await asyncio.sleep(5)

        for i in range(100):
            query = (
                #f"HEAD {url.path or '/'} HTTP/1.0\r\n"
                f"GET / HTTP/1.0\r\n"
                f"Host: {url.hostname}\r\n"
                f"\r\n")
            writers[i].write(query.encode('latin-1'))
            for _ in range(3):
                line = await readers[i].readline()
                if not line:
                    break
                line = line.decode('latin1').rstrip()
                if line:
                    print(line)
                    #await asyncio.sleep()

        for i in range(100):
            writers[i].close()


url = sys.argv[1]
port = sys.argv[2]

asyncio.run(print_http_headers(url, port))
