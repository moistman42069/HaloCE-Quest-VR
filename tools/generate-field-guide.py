"""Generate the offline launcher guide from current public docs and production config descriptions."""
from pathlib import Path
import re,ast
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'port/android/app/src/main/assets/guide';OUT.mkdir(parents=True,exist_ok=True)
for source,target in [('PLAYER-GUIDE.md','player-guide.txt'),('CONTROLS-AND-OPTIONS.md','controls.txt'),('ANDROID-TOUCH-CONTROLS.md','touch.txt')]:
    text=(ROOT/'docs'/source).read_text(encoding='utf-8')
    if target=='touch.txt': text+='\n\n'+(ROOT/'docs/ANDROID-GAMEPAD.md').read_text(encoding='utf-8')
    (OUT/target).write_text(text,encoding='utf-8')
s=(ROOT/'port/linux/src/port_config.c').read_text(encoding='utf-8')
s=s[s.index('static const struct config_setting config_settings[]'):s.index('/* ----------',s.index('static const struct config_setting config_settings[]')+1)]
rows=[]
for match in re.finditer(r'\{\s*"([a-z][a-z0-9_.]+)"\s*,\s*_config_(\w+)\s*,\s*("(?:\\.|[^"\\])*")(.*?)\},',s,re.S):
    name,kind,default,tail=match.groups()
    strings=re.findall(r'"(?:\\.|[^"\\])*"',tail)
    comment=''.join(ast.literal_eval(x) for x in strings[1:])
    rows.append(name+' ['+kind+']\nDefault: '+ast.literal_eval(default)+'\n'+comment+'\n')
if len(rows)<100:raise SystemExit('Config reference extraction incomplete')
(OUT/'settings.txt').write_text('NATIVE SETTINGS REFERENCE\n\nDefaults apply to new settings. Existing saved values win. VR settings apply to Quest only; desktop-only options do not affect Android. Restart for renderer, networking and other startup options. Use the in-game VR pages for live supported adjustments. The integrated project updater checks automatically in the launcher; Versions & updates controls checks and installation; inherited update.auto does not replace the mod with upstream.\n\n'+'\n'.join(rows),encoding='utf-8')
print('Bundled guides generated; settings:',len(rows))
