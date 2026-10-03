#ifndef HALO_GAME_DATA_PROFILE_H
#define HALO_GAME_DATA_PROFILE_H
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <sys/stat.h>
#include <errno.h>
/* 0 original data, 1 selected managed data, -1 invalid/incomplete selection. */
static int halo_game_data_profile(const char *base,char *out,size_t capacity)
{
    char path[1024],id[66],candidate[1024];struct stat st;
    int path_length=snprintf(path,sizeof(path),"%s/active-data.txt",base);
    if(path_length<0||(size_t)path_length>=sizeof(path))return -1;
    FILE *file=fopen(path,"rb");if(!file)return errno==ENOENT?0:-1;
    size_t n=fread(id,1,sizeof(id)-1,file);int extra=fgetc(file);int failed=ferror(file);fclose(file);
    if(failed||extra!=EOF||n>64||memchr(id,0,n))return -1;id[n]=0;
    while(n&&isspace((unsigned char)id[n-1]))id[--n]=0;
    char *start=id;while(isspace((unsigned char)*start))start++;
    if(!*start)return 0;
    if(strlen(start)!=34||start[0]!='p'||start[1]!='-')return -1;
    for(int i=2;i<34;i++)if(!((start[i]>='0'&&start[i]<='9')||(start[i]>='a'&&start[i]<='f')))return -1;
    int length=snprintf(candidate,sizeof(candidate),"%s/game-versions/%s",base,start);
    if(length<0||(size_t)length>=capacity||(size_t)length>=sizeof(candidate))return -1;
    snprintf(path,sizeof(path),"%s/maps/ui.map",candidate);if(stat(path,&st)||!S_ISREG(st.st_mode))return -1;
    snprintf(path,sizeof(path),"%s/profile.properties",candidate);if(stat(path,&st)||!S_ISREG(st.st_mode))return -1;
    memcpy(out,candidate,(size_t)length+1);return 1;
}
#endif
