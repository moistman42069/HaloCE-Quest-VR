package com.halo.decomp;
import android.app.*;
import android.text.InputType;
import android.widget.*;
import java.io.File;
import java.util.LinkedHashMap;

final class NetworkSettings {
    /** Test20e: the connection the device uses now, for the run log (Wi-Fi or
     *  mobile data decides most direct-connection failures; see the native
     *  "Internet play" NAT lines). Shared by the Quest and Android builds. */
    static String describe(android.content.Context context) {
        try {
            android.net.ConnectivityManager manager=(android.net.ConnectivityManager)context.getSystemService(android.content.Context.CONNECTIVITY_SERVICE);
            android.net.Network network=manager==null?null:manager.getActiveNetwork();
            android.net.NetworkCapabilities caps=network==null?null:manager.getNetworkCapabilities(network);
            if(caps==null) return "no active network";
            StringBuilder kind=new StringBuilder();
            if(caps.hasTransport(android.net.NetworkCapabilities.TRANSPORT_WIFI)) kind.append("Wi-Fi");
            if(caps.hasTransport(android.net.NetworkCapabilities.TRANSPORT_ETHERNET)) kind.append(kind.length()>0?"+":"").append("Ethernet");
            if(caps.hasTransport(android.net.NetworkCapabilities.TRANSPORT_CELLULAR)) kind.append(kind.length()>0?"+":"").append("mobile data");
            if(caps.hasTransport(android.net.NetworkCapabilities.TRANSPORT_VPN)) kind.append(kind.length()>0?"+":"").append("VPN");
            if(kind.length()==0) kind.append("other");
            return kind+(caps.hasCapability(android.net.NetworkCapabilities.NET_CAPABILITY_NOT_METERED)?", unmetered":", metered")
                +(caps.hasCapability(android.net.NetworkCapabilities.NET_CAPABILITY_VALIDATED)?", internet validated":", internet not validated");
        } catch(Exception e) { return "unknown ("+e.getClass().getSimpleName()+")"; }
    }

    static void show(Activity activity,File root) {
        LinearLayout layout=new LinearLayout(activity); layout.setOrientation(LinearLayout.VERTICAL);
        int p=(int)(16*activity.getResources().getDisplayMetrics().density); layout.setPadding(p,p,p,p);
        CheckBox online=new CheckBox(activity); online.setText("Internet invites (off = LAN only)");
        online.setChecked(ConfigSettings.read(root,"network","online","true").equals("true")); layout.addView(online);
        CheckBox upnp=new CheckBox(activity); upnp.setText("Allow automatic router port mapping (UPnP)");
        upnp.setChecked(ConfigSettings.read(root,"network","allow_upnp","true").equals("true")); layout.addView(upnp);
        CheckBox clipboard=new CheckBox(activity); clipboard.setText("Read copied invites when returning to the game");
        clipboard.setChecked(ConfigSettings.read(root,"network","join_from_clipboard","true").equals("true")); layout.addView(clipboard);
        TextView label=new TextView(activity); label.setText("Internet UDP port: 0 selects automatically; 1024–65535 uses a fixed port for manual router forwarding."); layout.addView(label);
        EditText port=new EditText(activity); port.setInputType(InputType.TYPE_CLASS_NUMBER); port.setSingleLine(true);
        port.setText(ConfigSettings.read(root,"network","tunnel_port","0")); layout.addView(port);
        TextView info=new TextView(activity); info.setText("Applies on the next game launch. A directory listing is not a connectivity test: firewalls, carrier NAT, Wi-Fi isolation and an offline host can prevent joining. Enable Internet invites for remote play; for LAN, use the same network and Play > Multiplayer > Join Game > LAN. Public games are under Join Game > Server Browser; invites use Direct Link. Advanced address, broadcast/VPN, broker and STUN settings remain in config.toml; only change them if you know your network."); layout.addView(info);
        ScrollView scroll=new ScrollView(activity); scroll.addView(layout);
        AlertDialog dialog=new GamepadNavigation.Builder(activity).setTitle("Network settings").setView(scroll)
            .setPositiveButton("Save",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            try {
                int value=Integer.parseInt(port.getText().toString());
                if(value!=0&&(value<1024||value>65535)) throw new IllegalArgumentException("Use 0 or 1024–65535");
                LinkedHashMap<String,String> changes=new LinkedHashMap<>();
                changes.put("online",Boolean.toString(online.isChecked())); changes.put("allow_upnp",Boolean.toString(upnp.isChecked()));
                changes.put("join_from_clipboard",Boolean.toString(clipboard.isChecked())); changes.put("tunnel_port",Integer.toString(value));
                ConfigSettings.write(root,"network",changes); RunLog.line("Network preferences saved for next launch"); dialog.dismiss();
            } catch(Exception e) { info.setText("Could not save: "+e.getMessage()); }
        })); dialog.show();
    }
}
