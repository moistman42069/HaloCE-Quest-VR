package com.halo.decomp;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

/** Edits only named scalar keys. Preserves other sections/settings and writes atomically. */
final class ConfigSettings {
    static String contents(File root) throws IOException {
        if(root==null) throw new IOException("Game storage unavailable");
        File f=new File(root,"config.toml"); if(!f.exists()) return "";
        if(f.length()>1024*1024) throw new IOException("Config exceeds 1 MiB");
        return new String(Files.readAllBytes(f.toPath()),StandardCharsets.UTF_8);
    }
    static String read(File root,String section,String key,String fallback) {
        try {
            String current="";
            for(String line:contents(root).split("\\r?\\n")) {
                String s=line.trim();
                if(s.startsWith("[")&&s.contains("]")) current=s.substring(1,s.indexOf(']')).trim();
                else if(current.equals(section)&&s.matches(java.util.regex.Pattern.quote(key)+"\\s*=.*"))
                    return s.substring(s.indexOf('=')+1).split("#",2)[0].trim();
            }
        } catch(IOException ignored) {}
        return fallback;
    }
    static void write(File root,String section,Map<String,String> values) throws IOException {
        String original=contents(root), current=""; StringBuilder out=new StringBuilder();
        Set<String> written=new HashSet<>(); boolean found=false;
        for(String line:original.split("\\r?\\n",-1)) {
            String s=line.trim();
            if(s.startsWith("[")&&s.contains("]")) {
                if(current.equals(section)) appendMissing(out,values,written);
                current=s.substring(1,s.indexOf(']')).trim();
                if(current.equals(section)) { if(found) throw new IOException("Duplicate config section; repair config before editing."); found=true; }
            }
            String key=s.contains("=") ? s.substring(0,s.indexOf('=')).trim() : "";
            if(current.equals(section)&&values.containsKey(key)) {
                if(!written.add(key)) throw new IOException("Duplicate config key: "+key);
                out.append(key).append(" = ").append(values.get(key)).append('\n');
            } else out.append(line).append('\n');
        }
        if(!found) out.append('\n').append('[').append(section).append("]\n");
        appendMissing(out,values,written);
        File partial=new File(root,"config.toml.launcher.tmp"), target=new File(root,"config.toml");
        try(FileOutputStream stream=new FileOutputStream(partial)) { stream.write(out.toString().getBytes(StandardCharsets.UTF_8)); stream.getFD().sync(); }
        if(!partial.renameTo(target)) { partial.delete(); throw new IOException("Could not replace config atomically."); }
    }
    private static void appendMissing(StringBuilder out,Map<String,String> values,Set<String> written) {
        for(Map.Entry<String,String> entry:values.entrySet()) if(written.add(entry.getKey()))
            out.append(entry.getKey()).append(" = ").append(entry.getValue()).append('\n');
    }
}
