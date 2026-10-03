package com.halo.decomp;
import android.app.*;
import android.widget.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;

final class LauncherHelp {
    static final String DATA_COMPATIBILITY_NOTE = "Some server incompatibilities may be caused by different map files from ISO/revision versions or modified game data. Use Game files & versions to select another supported set. A revision label alone does not prove compatibility; network versions, missing maps and connection problems can also prevent joining.";
    static void show(Activity activity) {
        new GamepadNavigation.Builder(activity).setTitle("Field guide")
            .setItems(new String[]{"Getting started & multiplayer", "VR controls & settings", "Flat touch & gamepad", "Every setting: reference"},(d,index)->{
                String[] files={"player-guide.txt","controls.txt","touch.txt","settings.txt"};
                try(InputStream in=activity.getAssets().open("guide/"+files[index])) {
                    ByteArrayOutputStream out=new ByteArrayOutputStream(); byte[] buffer=new byte[4096];
                    for(int n;(n=in.read(buffer))!=-1;) out.write(buffer,0,n);
                    page(activity,"Field guide",out.toString(StandardCharsets.UTF_8.name()));
                } catch(IOException e) { page(activity,"Guide unavailable","Could not open the bundled guide. See the project's docs on GitHub."); }
            }).setNegativeButton("Back",null).show();
    }
    static void page(Activity activity,String title,String content) {
        TextView text=new TextView(activity); text.setText(content); text.setTextSize(16); text.setTextIsSelectable(true);
        int pad=(int)(20*activity.getResources().getDisplayMetrics().density); text.setPadding(pad,pad,pad,pad);
        ScrollView scroll=new ScrollView(activity); scroll.addView(text);
        new GamepadNavigation.Builder(activity).setTitle(title).setView(scroll).setPositiveButton("Close",null).show();
    }
    static void data(Activity activity,File root) {
        TextView text=new TextView(activity); text.setText("Reading installed map headers…"); text.setPadding(24,16,24,16); text.setTextIsSelectable(true);
        ScrollView scroll=new ScrollView(activity); scroll.addView(text);
        ExecutorService worker=Executors.newSingleThreadExecutor();
        AlertDialog dialog=new GamepadNavigation.Builder(activity).setTitle("Game data & compatibility").setView(scroll)
            .setPositiveButton("Close",null).setNeutralButton("Fingerprint files",null).create();
        Runnable headers=()->{
            File[] files=root==null?null:new File(root,"maps").listFiles((dir,name)->name.endsWith(".map"));
            StringBuilder report=new StringBuilder(DATA_COMPATIBILITY_NOTE+"\n\nThis report reads actual cache builds and formats. PAL normalization is automatic. Original/Rev1/Rev2 disc labels remain unverified without trusted hashes. Co-op needs identical mission/resource files.\n\n");
            if(files==null) report.append("No maps found.");
            else { Arrays.sort(files,Comparator.comparing(File::getName)); for(File f:files) {
                String line=f.getName()+": "+MapInfo.read(f).summary()+"; "+f.length()+" bytes";
                report.append(line).append('\n'); RunLog.line("Data header: "+line);
            } }
            activity.runOnUiThread(()->{if(dialog.isShowing()) text.setText(report);});
        };
        dialog.setOnDismissListener(d->worker.shutdownNow());
        dialog.setOnShowListener(d->{
            worker.execute(headers);
            dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener(v->{
                dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setEnabled(false); text.setText("Hashing installed maps locally. This can take a minute. Results go into this launch's log; nothing is uploaded. Close to cancel.");
                worker.execute(()->{
                    StringBuilder report=new StringBuilder("SHA-256 file fingerprints (also recorded in launch log)\n\n");
                    File[] files=root==null?null:new File(root,"maps").listFiles((dir,name)->name.endsWith(".map"));
                    if(files!=null) { Arrays.sort(files,Comparator.comparing(File::getName)); for(File f:files) {
                        if(Thread.currentThread().isInterrupted()) break;
                        try { String line=f.getName()+"  "+MapInfo.sha256(f); report.append(line).append('\n'); RunLog.line("Data SHA256: "+line); }
                        catch(Exception e) { report.append(f.getName()).append(": ").append(e.getClass().getSimpleName()).append('\n'); }
                    } }
                    activity.runOnUiThread(()->{if(dialog.isShowing()) { text.setText(report); dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setEnabled(true); }});
                });
            });
        }); dialog.show();
    }
    static void graphics(Activity activity,File root) {
        boolean vr=activity.getPackageName().endsWith(".vr");
        boolean migrated=ConfigSettings.read(root,"renderer","vr_geometry_revision","0").equals("1");
        boolean current=(vr&&!migrated)||ConfigSettings.read(root,"renderer","safe_geometry",vr?"true":"false").equals("true");
        new GamepadNavigation.Builder(activity).setTitle("Geometry compatibility")
            .setMessage("Safe geometry is the VR default, including upgrades. Flat Android defaults to Normal. Use Safe if scenery stretches into triangles or strips. It bypasses static geometry caching, persistent streaming and GPU base-vertex rebasing. It can reduce frame rate. This is a renderer option, not a game-revision selection. Restart the game after changing it.\n\nCurrent: "+(current?"Safe":"Normal"))
            .setPositiveButton(current?"Use normal":"Use safe",(d,w)->{
                try { Map<String,String> changes=new LinkedHashMap<>();
                    changes.put("safe_geometry",Boolean.toString(!current));
                    if(vr) changes.put("vr_geometry_revision","1");
                    ConfigSettings.write(root,"renderer",changes);
                    Toast.makeText(activity,"Saved for next launch",Toast.LENGTH_LONG).show(); }
                catch(IOException e) { page(activity,"Could not save",e.getMessage()); }
            }).setNegativeButton("Cancel",null).show();
    }
}
