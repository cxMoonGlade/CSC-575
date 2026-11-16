"""Read selected official IDMT ZIP members using checked HTTP range responses."""
from pathlib import Path
import argparse
import io, json, urllib.request, zipfile

URL='https://zenodo.org/records/7544110/files/IDMT-SMT-GUITAR_V2.zip?download=1'
SIZE=1329918978
HERE=Path(__file__).resolve().parent


def parse_paths():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=HERE.parent/'data/idmt')
    parser.add_argument('--range-cache-dir', type=Path, default=None)
    args=parser.parse_args()
    output=args.data_dir.resolve()
    cache=args.range_cache_dir.resolve() if args.range_cache_dir else output/'range_cache'
    return cache,output


BASE,OUT=parse_paths()

class HTTPRangeFile(io.RawIOBase):
    def __init__(self):
        self.position=0
        self.cache=[]
        self.transferred=0
        BASE.mkdir(parents=True,exist_ok=True)
        tail_path=BASE/'idmt_zip_tail.bin'
        if not tail_path.exists():
            start=SIZE-100000
            request=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{SIZE-1}'})
            with urllib.request.urlopen(request,timeout=90) as response:
                if response.status != 206 or response.headers.get('Content-Range') != f'bytes {start}-{SIZE-1}/{SIZE}':
                    raise RuntimeError('Server did not provide the requested ZIP tail')
                data=response.read()
            if len(data) != 100000:
                raise RuntimeError('Truncated ZIP tail')
            tail_path.write_bytes(data)
            self.transferred+=len(data)
        tail=tail_path.read_bytes()
        if len(tail) != 100000:
            raise RuntimeError('Unexpected cached ZIP-tail length')
        self.cache.append((SIZE-len(tail),tail))
        central=BASE/'idmt_zip_central.bin'
        if central.exists():
            data=central.read_bytes()
            if len(data)!=703155: raise RuntimeError('Unexpected cached central-directory length')
            self.cache.append((1329215801,data))
    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position
    def seek(self,offset,whence=0):
        target=offset if whence==0 else self.position+offset if whence==1 else SIZE+offset
        if target<0: raise ValueError('Negative position')
        self.position=target
        return target
    def read(self,length=-1):
        if length<0: length=SIZE-self.position
        length=min(length,SIZE-self.position)
        if length<=0: return b''
        start=self.position;end=start+length
        for offset,data in reversed(self.cache):
            if offset<=start and end<=offset+len(data):
                self.position=end
                return data[start-offset:end-offset]
        fetch_end=min(SIZE,max(end,start+65536))
        request=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{fetch_end-1}'})
        with urllib.request.urlopen(request,timeout=90) as response:
            expected=f'bytes {start}-{fetch_end-1}/{SIZE}'
            if response.status!=206 or response.headers.get('Content-Range')!=expected:
                raise RuntimeError(f'Unexpected range response: {response.status} {response.headers.get("Content-Range")} != {expected}')
            data=response.read()
        if len(data)!=fetch_end-start: raise RuntimeError('Truncated byte range')
        self.transferred+=len(data)
        if start==1329215801 and len(data)==703155:
            (BASE/'idmt_zip_central.bin').write_bytes(data)
        self.cache.append((start,data))
        self.position=end
        return data[:length]

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/"archive_members.json").exists():
        raise FileExistsError("Preserve the existing archive inventory")
    remote=HTTPRangeFile()
    with zipfile.ZipFile(remote) as z:
        members=[dict(name=i.filename,size=i.file_size,compressed_size=i.compress_size,crc32=f'{i.CRC:08x}',header_offset=i.header_offset,compress_type=i.compress_type) for i in z.infolist()]
    (OUT/'archive_members.json').write_text(json.dumps(members,indent=2)+'\n')
    print('Members:',len(members),'remote bytes:',remote.transferred)
    print('ROOT/README:')
    for i in members:
        if 'readme' in i['name'].lower() or i['name'].count('/')<2: print(i)
    print('SUBSET4 first names:')
    subset=[i for i in members if '/dataset4/' in i['name']]
    for i in subset[:100]: print(i)
    print('subset4 count',len(subset))
