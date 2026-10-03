/* Bounded launcher wire format; independent of the engine for parser tests. */
#ifndef NETWORK_PVP_REQUEST_H
#define NETWORK_PVP_REQUEST_H
#include <stdio.h>
#include <string.h>
struct pvp_request { int maximum, publish, score; char map[32], variant[32], name[16]; };
static const char *pvp_variants[] = {"slayer", "team_slayer", "ctf", "ironctf", "oddball",
    "team_oddball", "king", "team_king", "race", "team_race", "rally", "elimination", "stalker", "accumulation"};
static int pvp_request_parse(const char *text, struct pvp_request *out)
{
    struct pvp_request r; int version, consumed=0, i, valid=0; size_t length;
    if (sscanf(text,"%d %d %d %d %31s %31s%n", &version,&r.maximum,&r.publish,&r.score,r.map,r.variant,&consumed)!=6 ||
        version!=1 || r.maximum<2 || r.maximum>128 || (r.publish!=0 && r.publish!=1) || r.score<0 || r.score>9999 ||
        text[consumed]!='\n') return 0;
    /* Map stems, never paths; custom Xbox multiplayer maps are allowed. */
    for(i=0;r.map[i];i++) if(!((r.map[i]>='a'&&r.map[i]<='z') || (r.map[i]>='0'&&r.map[i]<='9') || r.map[i]=='_')) return 0;
    for(i=0;i<(int)(sizeof(pvp_variants)/sizeof(pvp_variants[0]));i++) if(!strcmp(r.variant,pvp_variants[i])) valid=1;
    if(!valid) return 0;
    text+=consumed+1; length=strcspn(text,"\n");
    if(length<1 || length>15 || text[length]!='\n' || text[length+1]) return 0;
    for(i=0;i<(int)length;i++) if((unsigned char)text[i]<32 || (unsigned char)text[i]>126) return 0;
    memcpy(r.name,text,length); r.name[length]=0; *out=r; return 1;
}
#endif
