package com.halo.decomp;

import android.app.Activity;
import android.app.AlertDialog;
import android.text.InputFilter;
import android.text.InputType;
import android.widget.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.function.BooleanSupplier;

/** Real native lobby bootstrap, with stock map validation and late join. */
final class PvpLauncher {
    static final String[] VARIANTS = {"slayer", "team_slayer", "ctf", "ironctf", "oddball", "team_oddball",
        "king", "team_king", "race", "team_race", "rally", "elimination", "stalker", "accumulation"};
    private final Activity activity;
    private final File root;
    private final BooleanSupplier ready, start;
    PvpLauncher(Activity activity, File root, BooleanSupplier ready, BooleanSupplier start) {
        this.activity=activity; this.root=root; this.ready=ready; this.start=start;
    }
    private void text(LinearLayout layout, String value) {
        TextView text=new TextView(activity); text.setText(value); text.setPadding(0,12,0,4); layout.addView(text);
    }
    private Spinner select(LinearLayout layout, String label, String[] values) {
        text(layout,label); Spinner spinner=new Spinner(activity);
        ArrayAdapter<String> adapter=new ArrayAdapter<>(activity,android.R.layout.simple_spinner_item,values);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter); layout.addView(spinner); return spinner;
    }
    private EditText input(LinearLayout layout, String label, String value, boolean number) {
        text(layout,label); EditText field=new EditText(activity); field.setSingleLine(true);
        if(number) field.setInputType(InputType.TYPE_CLASS_NUMBER);
        field.setText(value); layout.addView(field); return field;
    }
    void show() {
        ArrayList<String> maps=new ArrayList<>();
        File[] files=root==null ? null : new File(root,"maps").listFiles();
        if(files!=null) for(File file:files) {
            String name=file.getName();
            if(name.matches("[a-z0-9_]{1,31}\\.map") && MapInfo.read(file).multiplayer) maps.add(name.substring(0,name.length()-4));
        }
        Collections.sort(maps);
        if(maps.isEmpty()) { new AlertDialog.Builder(activity).setTitle("No multiplayer maps")
            .setMessage("Import legitimate Xbox game data containing multiplayer maps before hosting. PC/Custom Edition maps are not interchangeable with Xbox maps.")
            .setPositiveButton("OK",null).show(); return; }
        LinearLayout layout=new LinearLayout(activity); layout.setOrientation(LinearLayout.VERTICAL);
        int pad=(int)(16*activity.getResources().getDisplayMetrics().density); layout.setPadding(pad,pad,pad,pad);
        text(layout,"Create a native-port PvP lobby. Choose Start Game in the in-game lobby when ready. Compatible players can join a running match. Hosting uses this device; keep the game active.");
        EditText name=input(layout,"Server name (1–15 printable characters)","Halo CE host",false);
        name.setFilters(new InputFilter[]{new InputFilter.LengthFilter(15)});
        Spinner map=select(layout,"Installed multiplayer map",maps.toArray(new String[0]));
        int blood=maps.indexOf("bloodgulch"); if(blood>=0) map.setSelection(blood);
        String[] labels=Arrays.stream(VARIANTS).map(s->s.replace('_',' ')).toArray(String[]::new);
        Spinner variant=select(layout,"Built-in game variant",labels);
        EditText maximum=input(layout,"Player limit (2–128; 16 recommended to start)","16",true);
        EditText score=input(layout,"Score to win (0 = variant default)","0",true);
        text(layout,"128 is the native protocol limit, not a Quest performance guarantee. Map spawn capacity, host CPU, upload speed and player latency matter. Start small and increase after testing. Rules below apply when this launcher creates the lobby. Changing the built-in variant in the native lobby restores that variant's default extra rules.");
        EditText time=input(layout,"Time limit in minutes (0 = unlimited, up to 1440)",ConfigSettings.read(root,"pvp","time_limit","0"),true);
        EditText respawn=input(layout,"Vehicle respawn seconds (0 = never, up to 3600)",ConfigSettings.read(root,"pvp","vehicle_respawn_time","0"),true);
        Spinner friendly=select(layout,"Friendly fire",new String[]{"On","Off","Shields only","Explosives only"});
        Spinner radar=select(layout,"Radar players",new String[]{"All","Friends only","None"});
        CheckBox balance=new CheckBox(activity);balance.setText("Automatically balance teams");layout.addView(balance);
        CheckBox infinite=new CheckBox(activity);infinite.setText("Infinite grenades");layout.addView(infinite);
        CheckBox custom=new CheckBox(activity);custom.setText("Use custom starting weapons");layout.addView(custom);
        String[] weapons={"None (unarmed)","Random","Assault rifle","Pistol","Shotgun","Sniper rifle","Rocket launcher","Plasma pistol","Plasma rifle","Needler"};
        Spinner primary=select(layout,"Primary weapon (custom loadout)",weapons),secondary=select(layout,"Secondary weapon (custom loadout)",weapons);
        primary.setSelection(2);secondary.setSelection(3);
        text(layout,"Custom rules use native v11. All clients need a v11-capable build. The campaign browser/protocol stays separate. The host applies team damage, respawns and loadouts.");
        CheckBox publish=new CheckBox(activity); publish.setText("List publicly in the multiplayer browser (shares session invite)"); layout.addView(publish);
        text(layout,"Private: share the game's invite with friends. Public: ChupathingyCE receives the invite, server name, map and population. Internet play must be enabled in Network settings. LAN works on the same network; router/client isolation can block it.");
        TextView status=new TextView(activity); layout.addView(status);
        ScrollView scroll=new ScrollView(activity); scroll.addView(layout);
        AlertDialog dialog=new AlertDialog.Builder(activity).setTitle("Host multiplayer").setView(scroll)
            .setPositiveButton("Create lobby",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(ignored->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            if(!ready.getAsBoolean()) return;
            try {
                String host=name.getText().toString().trim();
                int cap=Integer.parseInt(maximum.getText().toString()), points=Integer.parseInt(score.getText().toString());
                if(!host.matches("[ -~]{1,15}") || cap<2 || cap>128 || points<0 || points>9999)
                    throw new IllegalArgumentException("Use a printable name, 2–128 players, and a score from 0–9999.");
                if(publish.isChecked() && !ConfigSettings.read(root,"network","online","true").equals("true"))
                    throw new IllegalArgumentException("Enable Internet play in Network settings before public hosting.");
                int minutes=Integer.parseInt(time.getText().toString()),seconds=Integer.parseInt(respawn.getText().toString());
                if(minutes<0||minutes>1440||seconds<0||seconds>3600)throw new IllegalArgumentException("Time must be 0-1440 minutes; respawn 0-3600 seconds.");
                Map<String,String> options=new LinkedHashMap<>();options.put("time_limit",Integer.toString(minutes));options.put("vehicle_respawn_time",Integer.toString(seconds));
                options.put("friendly_fire",Integer.toString(friendly.getSelectedItemPosition()));options.put("radar_players",Integer.toString(radar.getSelectedItemPosition()));
                options.put("auto_team_balance",Boolean.toString(balance.isChecked()));options.put("infinite_grenades",Boolean.toString(infinite.isChecked()));
                options.put("custom_loadout",Boolean.toString(custom.isChecked()));options.put("primary_weapon",Integer.toString(primary.getSelectedItemPosition()));options.put("secondary_weapon",Integer.toString(secondary.getSelectedItemPosition()));
                ConfigSettings.write(root,"pvp",options);
                for(String stale:new String[]{"join_link.txt","coop_host.txt"}) {
                    File f=new File(root,stale); if(f.exists()&&!f.delete()) throw new IOException("Could not clear a previous launch request.");
                }
                File partial=new File(root,"pvp_host.txt.tmp"), request=new File(root,"pvp_host.txt");
                String contents="1 "+cap+" "+(publish.isChecked()?1:0)+" "+points+" "+maps.get(map.getSelectedItemPosition())+" "+VARIANTS[variant.getSelectedItemPosition()]+"\n"+host+"\n";
                try(FileOutputStream out=new FileOutputStream(partial)) { out.write(contents.getBytes(StandardCharsets.UTF_8)); out.getFD().sync(); }
                if(!partial.renameTo(request)) { partial.delete(); throw new IOException("Could not save host request."); }
                RunLog.line("PvP lobby requested: map="+maps.get(map.getSelectedItemPosition())+" maximum="+cap);
                if(start.getAsBoolean()) dialog.dismiss(); else request.delete();
            } catch(Exception e) { status.setText(e.getMessage()==null ? "Invalid host settings." : e.getMessage()); }
        })); dialog.show();
    }
}
