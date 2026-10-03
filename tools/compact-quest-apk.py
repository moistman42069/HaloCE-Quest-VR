#!/usr/bin/env python3
"""Remove obsolete incremental ZIP space, then align/sign without changing APK payloads.
Use the same signing key as the input APK. Keystore password is read from the
HALO_APK_KEYSTORE_PASSWORD environment variable and never printed.
"""
import argparse,hashlib,os,re,subprocess,tempfile,zipfile
from pathlib import Path

def payloads(path):
    with zipfile.ZipFile(path) as z:
        return {i.filename:hashlib.sha256(z.read(i.filename)).digest() for i in z.infolist()
                if not signature(i.filename)}
def signature(name):
    return re.fullmatch(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:RSA|DSA|EC|SF))',name,re.I) is not None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--build-tools',required=True,type=Path);p.add_argument('--keystore',required=True,type=Path)
    p.add_argument('--alias',default='androiddebugkey');a=p.parse_args()
    if a.input.resolve()==a.output.resolve() or a.output.exists():raise SystemExit('Choose a new output path')
    if 'HALO_APK_KEYSTORE_PASSWORD' not in os.environ:raise SystemExit('Set HALO_APK_KEYSTORE_PASSWORD')
    def certificate(path):
        text=subprocess.check_output([str(a.build_tools/'apksigner'),'verify','--print-certs',str(path)],text=True)
        return re.search(r'certificate SHA-256 digest: (\w+)',text)[1]
    before=certificate(a.input);hashes=payloads(a.input);a.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='apk-compact-',dir=a.output.parent) as work:
        unsigned=Path(work)/'unsigned.apk';aligned=Path(work)/'aligned.apk'
        with zipfile.ZipFile(a.input) as src,zipfile.ZipFile(unsigned,'w') as dst:
            for i in src.infolist():
                if signature(i.filename):continue
                j=zipfile.ZipInfo(i.filename,i.date_time);j.compress_type=i.compress_type;j.external_attr=i.external_attr
                dst.writestr(j,src.read(i.filename))
        subprocess.run([str(a.build_tools/'zipalign'),'-P','16','-f','4',str(unsigned),str(aligned)],check=True)
        subprocess.run([str(a.build_tools/'apksigner'),'sign','--ks',str(a.keystore),'--ks-key-alias',a.alias,
            '--ks-pass','env:HALO_APK_KEYSTORE_PASSWORD','--out',str(a.output),str(aligned)],check=True)
    subprocess.run([str(a.build_tools/'zipalign'),'-c','-P','16','4',str(a.output)],check=True)
    if certificate(a.output)!=before or payloads(a.output)!=hashes:raise SystemExit('Signature identity or payload mismatch')
    print(f'PASS: identical payload hashes/certificate; {a.input.stat().st_size} -> {a.output.stat().st_size} bytes')
if __name__=='__main__':main()
