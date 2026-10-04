package com.halo.decomp;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ContentValues;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import java.io.*;
import java.net.HttpURLConnection;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicBoolean;
import org.json.*;

/** Optional official archives, exported only. Never an app/engine update path. */
final class UpstreamDownloads {
    private static final String REPO="cybersecurity/halo-ce-universal";
    private static final long LIMIT=256L*1024*1024;
    private static final AtomicBoolean busy=new AtomicBoolean();
    static void show(Activity a) {
        if(!busy.compareAndSet(false,true)){message(a,"An upstream operation is already running.");return;}
        android.widget.Toast.makeText(a,"Checking official upstream releases...",0).show();
        new Thread(()->{
            try {
                JSONObject release=new JSONObject(new String(Updater.fetch("https://api.github.com/repos/"+REPO+"/releases/latest",1024*1024),StandardCharsets.UTF_8));
                String tag=release.getString("tag_name");
                if(!tag.matches("build-[0-9]{1,9}")||release.optBoolean("draft")||release.optBoolean("prerelease"))throw new IOException("Unrecognized official release");
                ArrayList<JSONObject> files=new ArrayList<>();ArrayList<String> labels=new ArrayList<>();
                JSONArray assets=release.getJSONArray("assets");
                for(int i=0;i<assets.length();i++) {
                    JSONObject f=assets.getJSONObject(i);String name=f.optString("name"),url=f.optString("browser_download_url");
                    if(!name.matches("halo-(android|linux|windows)-(release|debug)\\.zip"))continue;
                    if(!url.equals("https://github.com/"+REPO+"/releases/download/"+tag+"/"+name)||!UpdatePolicy.digest(f.optString("digest"))||f.optLong("size")<=0||f.optLong("size")>LIMIT)continue;
                    files.add(f);labels.add(name+" ("+(f.getLong("size")/1048576)+" MiB)");
                }
                if(files.isEmpty())throw new IOException("No official archives with verifiable integrity metadata");
                a.runOnUiThread(()->{
                    if(a.isFinishing()||a.isDestroyed())return;
                    new GamepadNavigation.Builder(a).setTitle("Official OpenCE "+tag)
                        .setItems(labels.toArray(new String[0]),(d,w)->new GamepadNavigation.Builder(a)
                            .setTitle("Download official archive?")
                            .setMessage("These are separate upstream builds, without this project's VR, co-op and launcher integrations. They do not update this mod. Android's upstream APK may share the flat app's package name but use a different signing key. Keep your existing mod installed.\n\nThis saves a verified ZIP to Download/HaloCE/Upstream. Nothing is extracted or installed. For mod updates use Check now on the previous screen.")
                            .setPositiveButton("Download ZIP",(confirm,which)->download(a,tag,files.get(w)))
                            .setNegativeButton("Cancel",null).show())
                        .setNegativeButton("Close",null).show();
                });
            }catch(Exception e){message(a,"Official release check failed: "+e.getMessage());}
            finally{busy.set(false);}
        },"upstream-release-check").start();
    }
    private static void message(Activity a,String text){a.runOnUiThread(()->{if(!a.isFinishing()&&!a.isDestroyed())new GamepadNavigation.Builder(a).setTitle("Official upstream archives").setMessage(text).setPositiveButton("OK",null).show();});}
    private static void download(Activity a,String tag,JSONObject asset) {
        if(!busy.compareAndSet(false,true))return;
        AtomicBoolean cancel=new AtomicBoolean();android.widget.TextView progress=new android.widget.TextView(a);progress.setPadding(32,24,32,24);progress.setText("Downloading and verifying official archive...");
        AlertDialog dialog=new GamepadNavigation.Builder(a).setTitle("Official upstream archive").setView(progress).setNegativeButton("Cancel",(d,w)->cancel.set(true)).create();dialog.setOnCancelListener(d->cancel.set(true));dialog.show();
        new Thread(()->{
            File temp=new File(a.getCacheDir(),"official-upstream.part");Uri pending=null;File legacyPart=null;
            try {
                long expected=asset.getLong("size"),count=0;MessageDigest hash=MessageDigest.getInstance("SHA-256");
                HttpURLConnection c=Updater.open(asset.getString("browser_download_url"));
                try(InputStream in=c.getInputStream();FileOutputStream out=new FileOutputStream(temp)) {
                    byte[] b=new byte[65536];int n;long reported=0;
                    while((n=in.read(b))!=-1){if(cancel.get())throw new IOException("Cancelled");count+=n;if(count>expected||count>LIMIT)throw new IOException("Archive size mismatch");out.write(b,0,n);hash.update(b,0,n);
                        if(count-reported>=1048576){reported=count;final long shown=count;a.runOnUiThread(()->progress.setText("Downloaded "+shown/1048576+" / "+expected/1048576+" MiB"));}}
                    out.getFD().sync();
                }finally{c.disconnect();}
                if(count!=expected||!asset.getString("digest").equalsIgnoreCase("sha256:"+Updater.hex(hash.digest())))throw new IOException("Archive checksum mismatch");
                if(cancel.get())throw new IOException("Cancelled");
                String name=tag+"-"+asset.getString("name");
                if(Build.VERSION.SDK_INT>=29) {
                    ContentValues values=new ContentValues();values.put(MediaStore.Downloads.DISPLAY_NAME,name);values.put(MediaStore.Downloads.MIME_TYPE,"application/zip");values.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/HaloCE/Upstream");values.put(MediaStore.Downloads.IS_PENDING,1);
                    pending=a.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,values);if(pending==null)throw new IOException("Downloads unavailable");
                    try(OutputStream out=a.getContentResolver().openOutputStream(pending);InputStream in=new FileInputStream(temp)){if(out==null)throw new IOException("Downloads unavailable");copy(in,out,cancel);}
                    if(cancel.get())throw new IOException("Cancelled");
                    ContentValues done=new ContentValues();done.put(MediaStore.Downloads.IS_PENDING,0);if(a.getContentResolver().update(pending,done,null,null)!=1)throw new IOException("Cannot finalize Downloads file");pending=null;
                } else {
                    File dir=new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS),"HaloCE/Upstream");if(!dir.isDirectory()&&!dir.mkdirs())throw new IOException("Downloads permission unavailable");
                    File target=new File(dir,name);if(target.exists())target=new File(dir,System.currentTimeMillis()+"-"+name);
                    legacyPart=new File(dir,target.getName()+".part");
                    try(InputStream in=new FileInputStream(temp);FileOutputStream out=new FileOutputStream(legacyPart)){copy(in,out,cancel);out.getFD().sync();}
                    if(cancel.get())throw new IOException("Cancelled");if(!legacyPart.renameTo(target))throw new IOException("Cannot finalize Downloads file");legacyPart=null;
                }
                RunLog.line("Verified upstream ZIP exported: "+tag+" "+asset.getString("name"));message(a,"Verified ZIP saved in Download/HaloCE/Upstream. Your mod, maps, settings and saves are unchanged.");
            }catch(Exception e){message(a,"Archive not saved: "+e.getMessage());}
            finally{
                try{if(pending!=null)a.getContentResolver().delete(pending,null,null);}catch(RuntimeException cleanup){RunLog.line("Upstream pending Downloads cleanup failed: "+cleanup.getClass().getSimpleName());}
                if(legacyPart!=null)legacyPart.delete();temp.delete();busy.set(false);a.runOnUiThread(()->{if(!a.isDestroyed())dialog.dismiss();});
            }
        },"upstream-archive-download").start();
    }
    private static void copy(InputStream in,OutputStream out,AtomicBoolean cancel)throws IOException{byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1){if(cancel.get())throw new IOException("Cancelled");out.write(b,0,n);}}
}
