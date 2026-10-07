package com.halo.decomp;
import android.app.*;
import android.widget.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;

final class LauncherHelp {
    static final String DATA_COMPATIBILITY_NOTE = "Some server incompatibilities may be caused by different map files from ISO/revision versions or modified game data. Use Game files & versions to select another supported set. A revision label alone does not prove compatibility; network versions, missing maps and connection problems can also prevent joining.";
    // Retained for older internal callers; the launcher now uses topic pages.
    static final String COOP_GUIDE = InGameNetworkGuide.COOP;

    static void network(Activity activity) {
        String[] titles={"Join public or LAN games", "Host multiplayer", "Host online campaign co-op",
            "Invites & passwords", "Compatibility & troubleshooting", "Saved invites"};
        String[] pages={InGameNetworkGuide.BROWSE, InGameNetworkGuide.HOST_PVP,
            InGameNetworkGuide.COOP, InGameNetworkGuide.INVITES, InGameNetworkGuide.COMPATIBILITY};
        new GamepadNavigation.Builder(activity).setTitle("Multiplayer & co-op guide")
            .setItems(titles,(d,item)->{
                if(item==pages.length) savedInvites(activity);
                else page(activity,titles[item],pages[item]);
            }).setNegativeButton("Back",null).show();
    }

    /** Read-only access to pre-OpenCE launcher saves. No directory requests or migration writes. */
    private static void savedInvites(Activity activity) {
        List<String> names=new ArrayList<>(), links=new ArrayList<>();
        int unreadable=0;
        for(String store:new String[]{"server_browser","coop_browser"}) {
            try {
                String raw=activity.getSharedPreferences(store,Activity.MODE_PRIVATE).getString("saved","[]");
                if(raw==null || raw.length()>1024*1024) { unreadable++; continue; }
                org.json.JSONArray entries=new org.json.JSONArray(raw);
                for(int i=0;i<entries.length() && i<512;i++) {
                    org.json.JSONObject entry=entries.optJSONObject(i);
                    if(entry==null) { unreadable++; continue; }
                    String link=ServerInvite.normalize(entry.optString("invite",""));
                    if(link==null) { unreadable++; continue; }
                    names.add((store.equals("coop_browser")?"Co-op: ":"Multiplayer: ")
                        +ServerInvite.displayName(entry.optString("name","Unnamed server")));
                    links.add(link);
                }
                if(entries.length()>512) unreadable+=entries.length()-512;
            } catch(Exception e) { unreadable++; }
        }
        String note=unreadable==0?"":" Some saved entries could not be displayed; their stored data is unchanged.";
        if(links.isEmpty()) {
            page(activity,"Saved invites","No readable saved invites from earlier launchers."+note
                +" New joins use Play > Multiplayer > Join Game > Direct Link or Server Browser.");
            return;
        }
        if(unreadable>0) names.add("Some saved entries could not be displayed (details)");
        final String warning=note;
        new GamepadNavigation.Builder(activity).setTitle("Saved invites (kept on this device)")
            .setItems(names.toArray(new String[0]),(d,item)->{
                if(item>=links.size()) { page(activity,"Saved invites",warning); return; }
                String link=links.get(item);
                TextView text=new TextView(activity);
                text.setText("This saved invite may be from an old session. Copy it, then Play > Multiplayer > Join Game > Direct Link > PASTE LINK. "
                    +"If the host does not appear, request a new invite. Nothing is uploaded or deleted.\n\n"+link);
                text.setTextIsSelectable(true); text.setTextSize(16);
                int pad=(int)(20*activity.getResources().getDisplayMetrics().density);
                text.setPadding(pad,pad,pad,pad);
                ScrollView scroll=new ScrollView(activity); scroll.addView(text);
                new GamepadNavigation.Builder(activity).setTitle(names.get(item)).setView(scroll)
                    .setPositiveButton("Copy invite",(copy,which)->{
                        android.content.ClipboardManager clipboard=(android.content.ClipboardManager)
                            activity.getSystemService(Activity.CLIPBOARD_SERVICE);
                        if(clipboard==null) { page(activity,"Clipboard unavailable","Select and copy the displayed invite manually."); return; }
                        try {
                            clipboard.setPrimaryClip(android.content.ClipData.newPlainText("Halo invite",link));
                            Toast.makeText(activity,"Invite copied. Use Direct Link in the game.",Toast.LENGTH_LONG).show();
                        } catch(RuntimeException unavailable) {
                            page(activity,"Clipboard unavailable","Use ENTER LINK in Direct Link with this invite:\n\n"+link);
                        }
                    }).setNegativeButton("Close",null).show();
            }).setNegativeButton("Back",null).show();
    }
    static void show(Activity activity) {
        new GamepadNavigation.Builder(activity).setTitle("Field guide")
            .setItems(new String[]{"Multiplayer & co-op guide", "Getting started & multiplayer", "VR controls & settings", "Flat touch & gamepad", "Every setting: reference", "Credits & licenses"},(d,item)->{
                if(item==0) { network(activity); return; }
                int index=item-1;
                String[] files={"player-guide.txt","controls.txt","touch.txt","settings.txt","credits.txt"};
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
    static String geometryMigrationKey(boolean vr) {
        return vr?"vr_geometry_revision":"android_geometry_revision";
    }
    static boolean geometrySafe(File root,boolean vr) {
        boolean migrated;
        try { migrated=Integer.parseInt(ConfigSettings.read(root,"renderer",geometryMigrationKey(vr),"0"))>=1; }
        catch(NumberFormatException e) { migrated=false; }
        return !migrated || !ConfigSettings.read(root,"renderer","safe_geometry","true").equals("false");
    }
    static void saveGeometry(File root,boolean vr,boolean safe) throws IOException {
        Map<String,String> changes=new LinkedHashMap<>();
        changes.put("safe_geometry",Boolean.toString(safe));
        changes.put(geometryMigrationKey(vr),"1");
        ConfigSettings.write(root,"renderer",changes);
    }
    static void graphics(Activity activity,File root) {
        boolean vr=activity.getPackageName().endsWith(".vr");
        boolean current=geometrySafe(root,vr);
        new GamepadNavigation.Builder(activity).setTitle("Geometry compatibility")
            .setMessage("Safe geometry is the default for Quest VR and flat Android, including the first upgrade to this default. You can select Normal here; that choice is kept on later launches. Safe avoids scenery stretching into triangles or strips by bypassing static geometry caching, persistent streaming and GPU base-vertex rebasing. It can reduce frame rate. This is a renderer option, not a game-revision selection. Restart the game after changing it.\n\nCurrent: "+(current?"Safe":"Normal"))
            .setPositiveButton(current?"Use normal":"Use safe",(d,w)->{
                try { saveGeometry(root,vr,!current);
                    Toast.makeText(activity,"Saved for next launch",Toast.LENGTH_LONG).show(); }
                catch(IOException e) { page(activity,"Could not save",e.getMessage()); }
            }).setNegativeButton("Cancel",null).show();
    }
}
