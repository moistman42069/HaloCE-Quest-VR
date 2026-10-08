"""Generate the offline launcher guide from current public docs and production config descriptions."""
from pathlib import Path
import re,ast
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'port/android/app/src/main/assets/guide';OUT.mkdir(parents=True,exist_ok=True)
(OUT/'credits.txt').write_text((ROOT/'CREDITS.md').read_text(encoding='utf-8')+'\n\n'+(ROOT/'THIRD-PARTY-NOTICES.txt').read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
for source,target in [('PLAYER-GUIDE.md','player-guide.txt'),('CONTROLS-AND-OPTIONS.md','controls.txt'),('ANDROID-TOUCH-CONTROLS.md','touch.txt')]:
    text=(ROOT/'docs'/source).read_text(encoding='utf-8')
    if target == 'player-guide.txt':
        text = (ROOT/'docs/RELEASE-1.0.16.md').read_text(encoding='utf-8') + '\n\n---\n\n' + text
    if target=='touch.txt': text+='\n\n'+(ROOT/'docs/ANDROID-GAMEPAD.md').read_text(encoding='utf-8')
    (OUT/target).write_text(text,encoding='utf-8',newline='\n')
s=(ROOT/'port/linux/src/port_config.c').read_text(encoding='utf-8')
s=s[s.index('static const struct config_setting config_settings[]'):s.index('/* ----------',s.index('static const struct config_setting config_settings[]')+1)]
rows=[]
for match in re.finditer(r'\{\s*"([a-z][a-z0-9_.]+)"\s*,\s*_config_(\w+)\s*,\s*("(?:\\.|[^"\\])*")(.*?)\},',s,re.S):
    name,kind,default,tail=match.groups()
    if name=='renderer.safe_geometry': default='"true in Quest VR and flat Android; false on desktop"'
    strings=re.findall(r'"(?:\\.|[^"\\])*"',tail)
    comment=''.join(ast.literal_eval(x) for x in strings[1:])
    rows.append(name+' ['+kind+']\nDefault: '+ast.literal_eval(default)+'\n'+comment+'\n')
if len(rows)<100:raise SystemExit('Config reference extraction incomplete')
(OUT/'settings.txt').write_text('NATIVE SETTINGS REFERENCE\n\nDefaults apply to new settings. Both APKs default to Safe geometry, including a one-time migration of older settings (VR: vr_geometry_revision=1; flat Android: android_geometry_revision=1). Subsequent explicit Safe/Normal choices are preserved; the Android migration does not reset existing VR choices. Desktop geometry defaults stay unchanged. Test18 also applies third-person/right-controller vehicle defaults once; later vehicle selections persist. VR settings apply to Quest only; desktop-only options do not affect Android. Restart for renderer, networking and other startup options. Use the in-game VR pages for live supported adjustments. The integrated project updater checks automatically in the launcher; Versions & updates controls checks and installation; inherited update.auto does not replace the mod with upstream.\n\n'+'\n'.join(rows),encoding='utf-8',newline='\n')
print('Bundled guides generated; settings:',len(rows))
