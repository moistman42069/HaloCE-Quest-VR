"""Verify actual CE01 capacity gates and campaign saved-unit slot limits."""
from pathlib import Path
import re,subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/campaign-capacity';OUT.mkdir(parents=True,exist_ok=True)
def fn(text,name):
 start=text.rfind('\n',0,text.index(name))+1;end=text.index('{',start)+1;depth=1
 while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]+'\n'
source=(ROOT/'port/linux/game/network_campaign.c').read_text()
maps=source[source.index('static char const *campaign_maps[]'):source.index('static boolean campaign_map_valid')]
header=(ROOT/'port/linux/game/network_campaign.h').read_text()
defines='\n'.join(line for line in header.splitlines() if line.startswith('#define HALO_CAMPAIGN_'))
players=(ROOT/'source/game/players.c').read_text()
player_header=(ROOT/'source/game/players.h').read_text()
local_limit=re.search(r'MAXIMUM_LOCAL_PLAYERS = (\d+)',player_header)[1]
code=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define NUMBEROF(a) (sizeof(a)/sizeof(a[0]))
#define VALID_INDEX(i,n) ((i)>=0&&(i)<(n))
#define DATUM_INDEX_TO_ABSOLUTE_INDEX(i) ((i)&65535)
#define game_engine_none 0
struct network_game {struct {long version;char name[128];}map;struct {int game_engine_index;}variant;int minimum_players,maximum_players,maximum_teams,difficulty;};
struct player_datum {short local_player_index;};
static int campaign=1;
static boolean network_campaign_playing(void){return campaign;}
'''+defines+'\n#define MAXIMUM_LOCAL_PLAYERS '+local_limit+'\n'+maps+fn(source,'static boolean campaign_map_valid(')+fn(source,'boolean network_campaign_game(')+fn(source,'boolean network_campaign_prepare(')+fn(players,'static short player_saved_unit_slot(')+r'''
int main(void){
 struct network_game game={0};struct player_datum player={.local_player_index=NONE};
 for(int mission=0;mission<10;mission++)for(int difficulty=0;difficulty<4;difficulty++){
  char map[128];snprintf(map,sizeof(map),"levels\\%s\\%s",campaign_maps[mission],campaign_maps[mission]);
  assert(network_campaign_prepare(&game,map,difficulty));assert(network_campaign_game(&game));
  for(int capacity=1;capacity<=128;capacity++){game.minimum_players=game.maximum_players=capacity;assert(network_campaign_game(&game)==(capacity==2));}
 }
 assert(!network_campaign_prepare(&game,"levels\\a10\\a10",4));assert(!network_campaign_prepare(&game,"bad",1));
 for(int slot=0;slot<128;slot++)assert(player_saved_unit_slot(slot|0x120000,&player)==(slot<4?slot:NONE));
 campaign=0;player.local_player_index=1;assert(player_saved_unit_slot(127,&player)==1);
 puts("PASS: production CE01 gate across 128 capacities / 40 mission difficulties; 128 recovery slots audited; solo slot unchanged");
}
'''
path=OUT/'capacity.c';path.write_text(code)
subprocess.run(['clang','-std=c11','-fsanitize=address,undefined',str(path),'-o',str(OUT/'capacity')],check=True)
subprocess.run([str(OUT/'capacity')],check=True)
