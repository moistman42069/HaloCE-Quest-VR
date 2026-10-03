package com.halo.decomp;
import java.io.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/** Reads the cache header, not an ISO filename's unverified Rev label.
 * Layout: source/cache/cache_files.c; type at 0x60 documented by SnowyMouse's
 * Halo Map Structure (CC BY 3.0), linked in docs/DATA-COMPATIBILITY.md. */
final class MapInfo {
    final String build, region, problem;
    final int version, type;
    final boolean multiplayer;
    private MapInfo(String build,int version,int type,String problem) {
        this.build=build; this.version=version; this.type=type; this.problem=problem;
        region=build.equals("01.01.14.2342")?"PAL":
            build.equals("01.10.12.2276")||build.equals("01.08.15.1749")?"NTSC":"unknown";
        multiplayer=problem.isEmpty()&&version==5&&type==1&&!region.equals("unknown");
    }
    static MapInfo read(File file) {
        try(RandomAccessFile in=new RandomAccessFile(file,"r")) {
            byte[] header=new byte[2048]; in.readFully(header);
            ByteBuffer b=ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN);
            if(b.getInt(0)!=0x68656164 || b.getInt(2044)!=0x666f6f74)
                return new MapInfo("",0,-1,"Not a recognized cache header (or a resource map)");
            int end=64; while(end<96&&header[end]!=0) end++;
            String build=new String(header,64,end-64,StandardCharsets.US_ASCII).replaceAll("[^ -~]","?");
            int version=b.getInt(4),type=b.getShort(96)&65535;
            return new MapInfo(build,version,type,version==5?"":"Not Xbox cache version 5");
        } catch(IOException e) { return new MapInfo("",0,-1,"Missing or truncated header"); }
    }
    String summary() { return problem.isEmpty()?"Xbox cache v"+version+", "+region+", build "+build+
        (type==1?", multiplayer":type==0?", campaign":type==2?", menu":", unknown map type"):problem; }
    static String sha256(File file) throws Exception {
        MessageDigest digest=MessageDigest.getInstance("SHA-256"); byte[] buffer=new byte[65536];
        try(InputStream in=new FileInputStream(file)) { for(int n;(n=in.read(buffer))!=-1;) {
            if(Thread.currentThread().isInterrupted()) throw new InterruptedIOException("Cancelled"); digest.update(buffer,0,n);
        } }
        StringBuilder text=new StringBuilder(); for(byte b:digest.digest()) text.append(String.format("%02x",b&255)); return text.toString();
    }
}
