#!/usr/bin/env python3
"""Test the imported menu assets and the real Expat-backed Android parser.

No game, map, GL context or APK is loaded. The parser's file/GL platform
boundary is replaced by an empty override folder and embedded XML fixtures.
"""

from pathlib import Path
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "port/assets/menus"


def check_assets():
    spec = importlib.util.spec_from_file_location("embed_assets", ROOT / "tools/embed_assets.py")
    embed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(embed)
    files = embed.menu_files()
    assert len(files) == len(set(files)), "duplicate embedded file"
    for name in files:
        assert (FOLDER / name).is_file(), name
        assert not Path(name).is_absolute() and ".." not in Path(name).parts, name
        if name.endswith(".png"):
            embed.png_size((FOLDER / name).read_bytes(), name)
    xml = [(name, ET.parse(FOLDER / name).getroot()) for name in files if name.endswith(".xml")]
    assert len(xml) >= 50, "an upstream menu file was lost"
    counts = {}
    for platform in ("android", "desktop"):
        elements = []

        def visit(element):
            if element.get("platform", platform) != platform:
                return
            elements.append(element)
            for child in element:
                visit(child)

        for _, tree in xml:
            visit(tree)
        names = {kind: {} for kind in ("widget", "bitmap", "strings")}
        for element in elements:
            if element.tag in names:
                name = element.get("name")
                assert name not in names[element.tag], (platform, element.tag, name)
                names[element.tag][name] = element
            if element.tag == "frame" and element.get("png"):
                assert element.get("png") in files, element.get("png")
        refs = {
            "bitmap": "bitmap", "header_bitmap": "bitmap", "footer_bitmap": "bitmap",
            "widget": "widget", "open": "widget", "replace": "widget", "focus": "widget",
            "otherwise": "widget", "description": "widget", "string_list": "strings",
        }
        for element in elements:
            for key, kind in refs.items():
                value = element.get(key)
                if not value or "\\" in value or (key == "replace" and element.tag != "on"):
                    continue
                assert value in names[kind], (platform, element.tag, element.get("name"), key, value)
        counts[platform] = {key: len(value) for key, value in names.items()}
        print(platform, counts[platform])
    for value in [b"", b"<menus/>", bytes(range(256)), b"\xff\x00\xfe"]:
        words = [int(word, 16) for word in re.findall("0x[0-9a-f]{8}", "".join(embed.words(value)))]
        decoded = b"".join(word.to_bytes(4, "little") for word in words)
        assert decoded[:len(value)] == value
        assert set(decoded[len(value):]) <= {0}
    payload = sum((FOLDER / name).stat().st_size for name in files)
    print(f"{len(files)} embedded files; {len(xml)} XML; {payload} menu bytes; references/PNGs/word encoding passed")
    return embed, xml, counts


def check_parser(embed, xml, counts):
    compiler = shutil.which("clang") or shutil.which("cc")
    assert compiler, "a C compiler is required for the real menu parser checks"
    parser = (ROOT / "port/linux/src/menu_files.c").read_text()
    parser = parser.split("/* ---------- art */", 1)[0]
    # The complete actual parser is retained. Only platform includes and the
    # separate GL texture-upload section are excluded from this host harness.
    for header in ["hud_hires.h", "platform.h", "port_config.h", "xgpu.h"]:
        parser = parser.replace(f'#include "{header}"', "")
    parser = parser.replace("#include <SDL3/SDL.h>", "")
    prefix = '#include <assert.h>\n#include <stdio.h>\n#include <string.h>\n'
    prefix += 'void platform_log(const char *format, ...) { (void)format; }\n'
    prefix += 'static void config_folder(char *out, unsigned long size);\n'
    arrays = []
    rows = []
    for index, (name, _) in enumerate(xml):
        data = (FOLDER / name).read_bytes()
        arrays.append(f"static const unsigned int fixture{index}[] = {{\n" + "\n".join(embed.words(data)) + "\n};")
        rows.append(f"{{ {json.dumps(name)}, fixture{index}, {len(data)} }},")
    fixtures = '\n#include "menu_files.h"\n' + "\n".join(arrays)
    fixtures += "\nconst struct menu_file_embedded menu_files_embedded[] = {\n" + "\n".join(rows) + "\n};\n"
    fixtures += f"const unsigned int menu_files_embedded_count = {len(xml)};\n"
    checks = r'''
static int accepts(const char *xml)
{
    struct reader reader;
    struct menu_file file;
    memset(&reader, 0, sizeof(reader));
    memset(&file, 0, sizeof(file));
    file.path = "fixture.xml";
    file.data = (const unsigned char *)xml;
    file.size = strlen(xml);
    return read_file(&reader, &file);
}
int main(void)
{
    const struct halo_menus *menus = halo_menus_load();
    unsigned short utf16[32];
    char nested[1500];
    int index;
    assert(menus);
    assert(menus == halo_menus_load());
    EXPECT_COUNTS
    assert(!strcmp(menus->root, "main_menu/main_menu"));
    assert(path_inside_folder("ce/title.png"));
    assert(!path_inside_folder("../title.png"));
    assert(!path_inside_folder("ce/.. /title.png"));
    assert(!path_inside_folder("/tmp/title.png"));
    assert(!path_inside_folder("C:\\title.png"));
    assert(accepts("<menus><widget name=\"ok\" width=\"32767\"/></menus>"));
    assert(accepts("<menus><widget platform=\"desktop\" invalid=\"ignored on Android\"/><widget name=\"ok\"/></menus>"));
    assert(!accepts("<menus><widget name=\"bad\" width=\"32768\"/></menus>"));
    assert(!accepts("<menus><widget name=\"bad\" width=\"abc\"/></menus>"));
    assert(!accepts("<menus><widget name=\"bad\" platform=\"unknown\"/></menus>"));
    assert(!accepts("<menus><widget name=\"bad\" bogus=\"yes\"/></menus>"));
    assert(!accepts("<menus><widget/></menus>"));
    assert(!accepts("<menus><widget name=\"bad\"></menus>"));
    assert(!accepts("<menus>unexpected text</menus>"));
    assert(!accepts("<menus><unknown/></menus>"));
    strcpy(nested, "<menus>");
    for (index = 0; index < 35; ++index) strcat(nested, "<widget name=\"deep\">");
    for (index = 0; index < 35; ++index) strcat(nested, "</widget>");
    strcat(nested, "</menus>");
    assert(!accepts(nested));
    assert(halo_menus_utf16("hi\\nthere", utf16, 32) == 10);
    assert(utf16[2] == '\r' && utf16[3] == '\n' && utf16[9] == 0);
    puts("actual Android menu parser: complete assets, platform filters, strict errors, depth/path guards and UTF-16 passed");
    return 0;
}
'''
    android = counts["android"]
    checks = checks.replace("EXPECT_COUNTS", "\n".join([
        f'assert(menus->widget_count == {android["widget"]});',
        f'assert(menus->bitmap_count == {android["bitmap"]});',
        f'assert(menus->string_list_count == {android["strings"]});',
    ]))
    with tempfile.TemporaryDirectory(prefix="test31-menu-") as temp:
        temp = Path(temp)
        source = temp / "parser.c"
        # This folder does not exist: no machine-local menu override is used.
        override = str(temp / "no-overrides") + "/"
        config = f'\nstatic void config_folder(char *out, unsigned long size) {{ snprintf(out, size, "%s", {json.dumps(override)}); }}\n'
        source.write_text(prefix + parser + fixtures + config + checks)
        expat = ROOT / "port/third_party/expat"
        target = temp / "parser"
        command = [compiler, "-DHALO_ANDROID=1", "-DHAVE_EXPAT_CONFIG_H", "-std=gnu11", "-O1",
            "-I" + str(expat), "-iquote", str(ROOT / "port/linux/include"), "-iquote", str(ROOT / "port/linux/src"),
            str(source), *(str(expat / name) for name in ["xmlparse.c", "xmlrole.c", "xmltok.c"]), "-o", str(target)]
        subprocess.run(command, check=True, cwd=ROOT)
        subprocess.run([str(target)], check=True, cwd=ROOT)


if __name__ == "__main__":
    check_parser(*check_assets())
