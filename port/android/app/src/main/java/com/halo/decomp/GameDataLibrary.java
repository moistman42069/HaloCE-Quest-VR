package com.halo.decomp;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** Managed, immutable-at-import game-data sets. No live maps are replaced. */
final class GameDataLibrary {
    static final int MAX_PROFILES=64, MAX_MAPS=512;
    static final long MAX_BYTES=12L*1024*1024*1024;
    final File base, versions, inbox;
    static final class Profile {
        final String id,label,build,fingerprint; final File root;
        Profile(String id,String label,String build,String fingerprint,File root) {
            this.id=id;this.label=label;this.build=build;this.fingerprint=fingerprint;this.root=root;
        }
        String description(){return label+" — "+build+" — "+fingerprint.substring(0,Math.min(12,fingerprint.length()));}
    }
    GameDataLibrary(File base) throws IOException {
        if(base==null)throw new IOException("Game storage is unavailable");
        this.base=base.getCanonicalFile();versions=new File(this.base,"game-versions");inbox=new File(versions,"inbox");
        if(!inbox.isDirectory()&&!inbox.mkdirs())throw new IOException("Cannot create game-data library");
    }
    static boolean idValid(String id){return id!=null&&id.matches("p-[a-f0-9]{32}");}
    static File activeRoot(File base) {
        if(base==null)return null;
        File marker=new File(base,"active-data.txt");
        try {
            if(!marker.exists())return base;
            if(marker.length()>64)throw new IOException("Invalid selection");
            String id=new String(Files.readAllBytes(marker.toPath()),StandardCharsets.UTF_8).replaceAll("^\\s+|\\s+$","");
            if(id.isEmpty())return base;
            if(!idValid(id))throw new IOException("Invalid profile ID");
            File root=new File(new File(base,"game-versions"),id);
            if(!root.getCanonicalFile().getParentFile().equals(new File(base,"game-versions").getCanonicalFile())||!new File(root,"profile.properties").isFile()||!new File(root,"maps/ui.map").isFile())
                throw new IOException("Selected profile is incomplete");
            return root;
        } catch(IOException e){return null;} // never silently launch a different set
    }
    List<Profile> list() throws IOException {
        List<Profile> result=new ArrayList<>();
        if(new File(base,"maps/ui.map").isFile())result.add(new Profile("","Existing game data",MapInfo.read(new File(base,"maps/ui.map")).summary(),"existing",base));
        File[] dirs=versions.listFiles();if(dirs==null)return result;
        Arrays.sort(dirs,Comparator.comparing(File::getName));
        for(File dir:dirs) if(idValid(dir.getName())&&dir.isDirectory()&&dir.getCanonicalFile().equals(dir.getAbsoluteFile())) {
            File file=new File(dir,"profile.properties");if(!file.isFile()||file.length()>262144)continue;
            Properties props=new Properties();try(InputStream in=new FileInputStream(file)){props.load(in);}
            if(!new File(dir,"maps/ui.map").isFile())continue;
            result.add(new Profile(dir.getName(),props.getProperty("label","Imported data"),props.getProperty("build","unknown"),props.getProperty("fingerprint","unknown"),dir));
        }
        return result;
    }
    File stage() throws IOException {
        if(list().size()>=MAX_PROFILES)throw new IOException("Library limit reached (64 sets)");
        File dir=new File(versions,"partial-"+UUID.randomUUID().toString());
        if(!dir.mkdir())throw new IOException("Cannot create import staging folder");return dir;
    }
    static boolean mapName(String name){return name!=null&&name.matches("(?i)[a-z0-9 _.-]{1,100}\\.map")&&!name.contains("..");}
    static void copy(InputStream in,File target,long limit) throws IOException {
        byte[] buffer=new byte[1024*1024];long total=0;
        try(OutputStream out=new FileOutputStream(target)) {for(int n;(n=in.read(buffer))!=-1;){
            if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("Import cancelled");
            total+=n;if(total>limit)throw new IOException("Import exceeds size limit");out.write(buffer,0,n);
        }}
    }
    static void copyMaps(File source,File stage) throws IOException {
        File maps=new File(stage,"maps");if(!maps.mkdir())throw new IOException("Cannot create maps staging folder");
        File[] files=source.listFiles();if(files==null)throw new IOException("Cannot read maps folder");long total=0;int count=0;
        for(File f:files)if(f.isFile()&&mapName(f.getName())) {
            if(!f.getCanonicalFile().equals(f.getAbsoluteFile()))throw new IOException("Linked files are not imported");
            total+=f.length();if(++count>MAX_MAPS||total>MAX_BYTES)throw new IOException("Game data exceeds library limits");
            File target=new File(maps,f.getName().toLowerCase(Locale.ROOT));
            if(target.exists())throw new IOException("Duplicate map name: "+f.getName());
            try(InputStream in=new FileInputStream(f)){copy(in,target,MAX_BYTES);}
        }
    }
    Profile finish(File stage,String label) throws Exception {
        if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("Import cancelled");
        if(!stage.getCanonicalFile().getParentFile().equals(versions.getCanonicalFile())||!stage.getName().startsWith("partial-"))throw new IOException("Invalid staging directory");
        File maps=new File(stage,"maps");MapInfo ui=MapInfo.read(new File(maps,"ui.map"));
        if(!ui.problem.isEmpty()||ui.region.equals("unknown")||ui.type!=2)throw new IOException("Requires supported Xbox Halo CE menu/cache data; "+ui.summary());
        File[] files=maps.listFiles((d,n)->mapName(n));if(files==null||files.length==0||files.length>MAX_MAPS)throw new IOException("Invalid map count");
        Arrays.sort(files,Comparator.comparing(File::getName));MessageDigest digest=MessageDigest.getInstance("SHA-256");
        Properties props=new Properties();Set<String> builds=new TreeSet<>();long total=0;
        for(File f:files){
            total+=f.length();if(total>MAX_BYTES)throw new IOException("Game data exceeds 12 GiB");
            if(!Arrays.asList("bitmaps.map","sounds.map","loc.map").contains(f.getName())){
                MapInfo info=MapInfo.read(f);if(!info.problem.isEmpty()||info.region.equals("unknown")||info.type>2)throw new IOException("Unsupported map: "+f.getName()+"; "+info.summary());
                builds.add(info.region+" "+info.build);
            }
            String hash=MapInfo.sha256(f);props.setProperty("map."+f.getName(),hash);
            digest.update((f.getName()+":"+f.length()+":"+hash+"\n").getBytes(StandardCharsets.UTF_8));
        }
        StringBuilder hex=new StringBuilder();for(byte b:digest.digest())hex.append(String.format("%02x",b&255));
        String fingerprint=hex.toString();for(Profile p:list())if(p.fingerprint.equals(fingerprint))return p;
        String id="p-"+UUID.randomUUID().toString().replace("-","");
        label=label==null?"Imported data":label.replaceAll("[\\p{Cntrl}]"," ").trim();if(label.length()>80)label=label.substring(0,80);
        String build=String.join(", ",builds);props.setProperty("label",label);props.setProperty("build",build);props.setProperty("fingerprint",fingerprint);
        props.setProperty("revision","unverified");props.setProperty("schema","1");
        File current=activeRoot(base);File config=new File(current==null?base:current,"config.toml");if(config.isFile()&&config.length()<1024*1024)Files.copy(config.toPath(),new File(stage,"config.toml").toPath());
        try(OutputStream out=new FileOutputStream(new File(stage,"profile.properties"))){props.store(out,"Detected cache builds and exact per-map SHA-256; disc revision not inferred from filenames");}
        if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("Import cancelled");
        File finished=new File(versions,id);if(!stage.renameTo(finished))throw new IOException("Cannot finalize game data");
        return new Profile(id,label,build,fingerprint,finished);
    }
    void discard(File stage)throws IOException {
        if(!stage.exists())return;
        if(!stage.getCanonicalFile().getParentFile().equals(versions.getCanonicalFile())||!stage.getName().startsWith("partial-"))throw new IOException("Refusing cleanup outside import staging");
        Files.walkFileTree(stage.toPath(),new SimpleFileVisitor<Path>(){
            @Override public FileVisitResult visitFile(Path p,java.nio.file.attribute.BasicFileAttributes a)throws IOException{Files.delete(p);return FileVisitResult.CONTINUE;}
            @Override public FileVisitResult postVisitDirectory(Path p,IOException e)throws IOException{if(e!=null)throw e;Files.delete(p);return FileVisitResult.CONTINUE;}
        });
    }
    void select(String id) throws IOException {
        boolean found=false;for(Profile p:list())if(p.id.equals(id)){found=true;break;}
        if(!found)throw new IOException("Profile is unavailable");
        File tmp=new File(base,"active-data.txt.tmp");Files.write(tmp.toPath(),id.getBytes(StandardCharsets.UTF_8));
        Files.move(tmp.toPath(),new File(base,"active-data.txt").toPath(),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
    }
    void rename(Profile p,String label) throws IOException {
        if(p.id.isEmpty())throw new IOException("Existing data keeps its original label");
        Properties props=new Properties();File file=new File(p.root,"profile.properties");
        try(InputStream in=new FileInputStream(file)){props.load(in);}label=label.trim();
        if(label.isEmpty()||label.length()>80||label.matches(".*[\\p{Cntrl}].*"))throw new IOException("Use a label of 1-80 characters");
        props.setProperty("label",label);File tmp=new File(p.root,"profile.properties.tmp");
        try(OutputStream out=new FileOutputStream(tmp)){props.store(out,"User label; detected identity unchanged");}
        Files.move(tmp.toPath(),file.toPath(),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
    }
    List<Profile> withMap(String map) throws IOException {
        List<Profile> result=new ArrayList<>();if(!map.matches("[A-Za-z0-9_-]{1,80}"))return result;
        for(Profile p:list())if(MapInfo.read(new File(p.root,"maps/"+map+".map")).multiplayer)result.add(p);return result;
    }
}
