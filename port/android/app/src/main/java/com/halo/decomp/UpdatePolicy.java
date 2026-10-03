package com.halo.decomp;

import java.net.URI;

/** Pure policy: only this project's signed, complete APKs may replace the app. */
final class UpdatePolicy {
    static final String REPOSITORY="moistman42069/HaloCE-Quest-VR";
    static boolean allowedUrl(String address) {
        try { URI u=new URI(address);String h=u.getHost();
            return "https".equals(u.getScheme()) && u.getUserInfo()==null && (u.getPort()==-1 || u.getPort()==443) &&
                ("api.github.com".equals(h)||"github.com".equals(h)||"release-assets.githubusercontent.com".equals(h)||"objects.githubusercontent.com".equals(h));
        } catch(Exception e){return false;}
    }
    static String asset(String tag,boolean vr) {
        if(tag==null || !tag.matches("halo-ce-quest-test[0-9]+[a-z]?")) return null;
        return "HaloCE-"+(vr?"Quest-":"Android-")+tag.substring("halo-ce-quest-".length())+".apk";
    }
    static boolean newer(String tag,String installed) {
        // A candidate newer than the public release must never be offered a downgrade.
        try {
            String a=tag.substring("halo-ce-quest-test".length()),b=installed.substring(installed.indexOf("test")+4);
            int ai=Integer.parseInt(a.replaceAll("[^0-9]","")),bi=Integer.parseInt(b.replaceAll("[^0-9]",""));
            return ai>bi || ai==bi && a.compareTo(b)>0;
        } catch(Exception e){return false;}
    }
    static int upstreamVersion(String source) {
        if(source==null||source.length()>65536)return -1;
        java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?m)^#define[ \t]+HALO_PORT_NETWORK_VERSION[ \t]+([0-9]{1,5})[ \t]*$").matcher(source);
        if(!m.find())return -1;int value=Integer.parseInt(m.group(1));return m.find()||value<1||value>65535?-1:value;
    }
    static boolean digest(String d){return d!=null && d.matches("sha256:[0-9a-fA-F]{64}");}
}
