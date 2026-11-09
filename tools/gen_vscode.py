#!/usr/bin/env python3
"""Render tokens/tokens.json into a VS Code colour theme extension (light + dark).

Writes vscode/platinum-neue/ (unpacked extension) and vscode/platinum-neue-<ver>.vsix.
Install:  code --install-extension vscode/platinum-neue-<ver>.vsix

The workbench follows the Platinum hierarchy: grey chrome around a lighter content surface
(darker in dark mode), sunken inactive tabs with the active tab joining the editor, inset inputs,
and the accent only on selection, focus and primary buttons. VS Code can't read the system accent,
so the default token accent is used.

Usage: python3 tools/gen_vscode.py
"""
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "tokens" / "tokens.json").read_text())
OUT = ROOT / "vscode"
EXT = OUT / "platinum-neue"
VERSION = "0.1.0"
PUBLISHER = "platinumneue"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


def alpha(c, a):
    return c + f"{round(a * 255):02X}"


# syntax palette: muted, drawn from the accent and status tokens so code sits in the same family
SYNTAX = {
    "light": {"comment": "#8A867F", "keyword": "#7A4A8C", "string": "#2C7A45", "number": "#A9472A",
              "function": "#3F4FC4", "type": "#2A7372", "constant": "#9A6A0C", "tag": "#A9472A",
              "attribute": "#9A6A0C", "regexp": "#2A7372", "operator": "#57544E", "invalid": "#B43A28"},
    "dark": {"comment": "#7F7B74", "keyword": "#C08FD3", "string": "#7FC796", "number": "#E08562",
             "function": "#97A1F2", "type": "#5FBAB8", "constant": "#E0A642", "tag": "#E08562",
             "attribute": "#E0A642", "regexp": "#5FBAB8", "operator": "#A9A59E", "invalid": "#E8735F"},
}


def theme(mode):
    dark = mode == "dark"
    t = TOKENS["modes"][mode]
    acc = TOKENS["accents"][TOKENS["accents"]["default"]]
    A, on = acc[mode], acc["onDark" if dark else "onLight"]
    focus = acc["focusDark" if dark else "focusLight"]
    chrome, chrome2, raised, content = t["chrome"], t["chrome2"], t["raised"], t["content"]
    text, text2 = t["text"], t["text2"]
    line = mix(chrome, text, 0.5)             # control edge (controlLineColor in the Qt style)
    soft = mix(chrome, text, 0.2)             # panel separators
    sunken = mix(chrome, "#000000", 0.2) if dark else mix(chrome, text, 0.06)
    hover = mix(chrome, text, 0.08)
    sel_inactive = mix(A, content, 0.75 if not dark else 0.65)
    shadow = "#00000066" if dark else "#2824201F"
    s = SYNTAX[mode]

    colors = {
        # base
        "foreground": text, "descriptionForeground": text2, "disabledForeground": t["textDisabled"],
        "errorForeground": t["negative"], "focusBorder": focus, "contrastBorder": None,
        "widget.shadow": shadow, "widget.border": line, "selection.background": alpha(A, 0.35),
        "icon.foreground": text2, "sash.hoverBorder": focus, "textLink.foreground": t["link"],
        "textLink.activeForeground": t["link"], "textPreformat.foreground": s["string"],
        "textBlockQuote.background": chrome2, "textBlockQuote.border": line, "textCodeBlock.background": chrome2,
        "textSeparator.foreground": soft,
        # window chrome
        "titleBar.activeBackground": chrome, "titleBar.activeForeground": text,
        "titleBar.inactiveBackground": chrome, "titleBar.inactiveForeground": text2, "titleBar.border": soft,
        "activityBar.background": chrome, "activityBar.foreground": text, "activityBar.inactiveForeground": text2,
        "activityBar.border": soft, "activityBar.activeBorder": A, "activityBar.activeBackground": sunken,
        "activityBarBadge.background": A, "activityBarBadge.foreground": on,
        "activityBarTop.foreground": text, "activityBarTop.inactiveForeground": text2, "activityBarTop.activeBorder": A,
        "sideBar.background": chrome, "sideBar.foreground": text, "sideBar.border": soft,
        "sideBarTitle.foreground": text2, "sideBarSectionHeader.background": chrome2,
        "sideBarSectionHeader.foreground": text, "sideBarSectionHeader.border": soft,
        "panel.background": chrome, "panel.border": soft, "panelTitle.activeForeground": text,
        "panelTitle.inactiveForeground": text2, "panelTitle.activeBorder": A,
        "panelSectionHeader.background": chrome2, "panelSection.border": soft,
        "statusBar.background": chrome, "statusBar.foreground": text2, "statusBar.border": soft,
        "statusBar.noFolderBackground": chrome, "statusBar.debuggingBackground": mix(chrome, t["neutral"], 0.25),
        "statusBar.debuggingForeground": text, "statusBarItem.hoverBackground": hover,
        "statusBarItem.activeBackground": sunken, "statusBarItem.remoteBackground": A,
        "statusBarItem.remoteForeground": on, "statusBarItem.prominentBackground": chrome2,
        # tabs: sunken until selected; the active tab joins the editor
        "editorGroupHeader.tabsBackground": sunken, "editorGroupHeader.tabsBorder": line,
        "editorGroupHeader.noTabsBackground": chrome, "editorGroup.border": line,
        "editorGroup.dropBackground": alpha(A, 0.15),
        "tab.activeBackground": content, "tab.activeForeground": text, "tab.activeBorderTop": line,
        "tab.activeBorder": content, "tab.unfocusedActiveBackground": content, "tab.unfocusedActiveForeground": text2,
        "tab.inactiveBackground": sunken, "tab.inactiveForeground": text2, "tab.border": line,
        "tab.hoverBackground": mix(sunken, raised, 0.6), "tab.unfocusedHoverBackground": mix(sunken, raised, 0.4),
        "tab.lastPinnedBorder": line, "tab.dragAndDropBorder": focus,
        "breadcrumb.background": content, "breadcrumb.foreground": text2, "breadcrumb.focusForeground": text,
        "breadcrumb.activeSelectionForeground": text, "breadcrumbPicker.background": raised,
        # editor
        "editor.background": content, "editor.foreground": text,
        "editorLineNumber.foreground": mix(content, text, 0.35), "editorLineNumber.activeForeground": text,
        "editorCursor.foreground": text, "editor.lineHighlightBackground": alpha(text, 0.04),
        "editor.lineHighlightBorder": alpha(text, 0.0),
        "editor.selectionBackground": alpha(A, 0.30 if dark else 0.22),
        "editor.inactiveSelectionBackground": alpha(A, 0.15),
        "editor.selectionHighlightBackground": alpha(A, 0.14), "editor.wordHighlightBackground": alpha(text, 0.08),
        "editor.wordHighlightStrongBackground": alpha(A, 0.18),
        "editor.findMatchBackground": alpha(t["neutral"], 0.45), "editor.findMatchHighlightBackground": alpha(t["neutral"], 0.22),
        "editor.findMatchBorder": t["neutral"], "editor.rangeHighlightBackground": alpha(text, 0.05),
        "editorBracketMatch.background": alpha(A, 0.15), "editorBracketMatch.border": alpha(A, 0.6),
        "editorIndentGuide.background1": alpha(text, 0.08), "editorIndentGuide.activeBackground1": alpha(text, 0.25),
        "editorWhitespace.foreground": alpha(text, 0.18), "editorRuler.foreground": alpha(text, 0.10),
        "editorLink.activeForeground": t["link"], "editorCodeLens.foreground": text2,
        "editorGutter.background": content, "editorGutter.addedBackground": t["positive"],
        "editorGutter.modifiedBackground": A, "editorGutter.deletedBackground": t["negative"],
        "editorError.foreground": t["negative"], "editorWarning.foreground": t["neutral"],
        "editorInfo.foreground": A, "editorHint.foreground": text2,
        "editorOverviewRuler.border": soft, "editorStickyScroll.background": content,
        "editorStickyScrollHover.background": chrome2, "editorStickyScroll.shadow": shadow,
        "editorWidget.background": raised, "editorWidget.foreground": text, "editorWidget.border": line,
        "editorSuggestWidget.background": raised, "editorSuggestWidget.border": line,
        "editorSuggestWidget.selectedBackground": A, "editorSuggestWidget.selectedForeground": on,
        "editorSuggestWidget.highlightForeground": A, "editorSuggestWidget.focusHighlightForeground": on,
        "editorHoverWidget.background": raised, "editorHoverWidget.border": line,
        "peekView.border": line, "peekViewEditor.background": content, "peekViewResult.background": chrome,
        "peekViewTitle.background": chrome2,
        "diffEditor.insertedTextBackground": alpha(t["positive"], 0.18), "diffEditor.removedTextBackground": alpha(t["negative"], 0.18),
        "diffEditor.insertedLineBackground": alpha(t["positive"], 0.08), "diffEditor.removedLineBackground": alpha(t["negative"], 0.08),
        "minimap.background": content, "minimapSlider.background": alpha(text, 0.08),
        # scrollbars: a raised-looking thumb on the surface
        "scrollbar.shadow": shadow, "scrollbarSlider.background": alpha(line, 0.45),
        "scrollbarSlider.hoverBackground": alpha(line, 0.65), "scrollbarSlider.activeBackground": alpha(line, 0.8),
        # controls
        "button.background": A, "button.foreground": on, "button.hoverBackground": mix(A, "#000000", 0.1),
        "button.border": mix(A, "#000000", 0.25), "button.separator": alpha(on, 0.4),
        "button.secondaryBackground": raised, "button.secondaryForeground": text,
        "button.secondaryHoverBackground": t["raisedHover"],
        "input.background": content, "input.foreground": text, "input.border": line,
        "input.placeholderForeground": t["textDisabled"], "inputOption.activeBackground": alpha(A, 0.25),
        "inputOption.activeBorder": A, "inputOption.activeForeground": text,
        "inputValidation.errorBackground": mix(content, t["negative"], 0.12), "inputValidation.errorBorder": t["negative"],
        "inputValidation.warningBackground": mix(content, t["neutral"], 0.12), "inputValidation.warningBorder": t["neutral"],
        "inputValidation.infoBackground": mix(content, A, 0.12), "inputValidation.infoBorder": A,
        "dropdown.background": raised, "dropdown.foreground": text, "dropdown.border": line,
        "dropdown.listBackground": raised,
        "checkbox.background": content, "checkbox.border": line, "checkbox.foreground": text,
        "checkbox.selectBackground": raised, "checkbox.selectBorder": line,
        "badge.background": A, "badge.foreground": on,
        "progressBar.background": A,
        "keybindingLabel.background": raised, "keybindingLabel.foreground": text,
        "keybindingLabel.border": line, "keybindingLabel.bottomBorder": line,
        "toolbar.hoverBackground": hover, "toolbar.activeBackground": sunken,
        # lists and trees
        "list.activeSelectionBackground": A, "list.activeSelectionForeground": on,
        "list.activeSelectionIconForeground": on, "list.inactiveSelectionBackground": sel_inactive,
        "list.inactiveSelectionForeground": text, "list.hoverBackground": hover, "list.hoverForeground": text,
        "list.focusOutline": focus, "list.focusAndSelectionOutline": focus, "list.inactiveFocusOutline": alpha(focus, 0.0),
        "list.highlightForeground": A, "list.focusHighlightForeground": on,
        "list.dropBackground": alpha(A, 0.15), "list.errorForeground": t["negative"], "list.warningForeground": t["neutral"],
        "tree.indentGuidesStroke": alpha(text, 0.2), "tree.inactiveIndentGuidesStroke": alpha(text, 0.1),
        # menus, quick input, notifications: raised sheets
        "menu.background": raised, "menu.foreground": text, "menu.border": line, "menu.separatorBackground": soft,
        "menu.selectionBackground": A, "menu.selectionForeground": on,
        "menubar.selectionBackground": A, "menubar.selectionForeground": on,
        "quickInput.background": raised, "quickInput.foreground": text, "quickInputTitle.background": chrome2,
        "quickInputList.focusBackground": A, "quickInputList.focusForeground": on, "quickInputList.focusIconForeground": on,
        "pickerGroup.border": soft, "pickerGroup.foreground": text2,
        "notifications.background": raised, "notifications.foreground": text, "notifications.border": line,
        "notificationCenterHeader.background": chrome2, "notificationToast.border": line,
        "notificationsErrorIcon.foreground": t["negative"], "notificationsWarningIcon.foreground": t["neutral"],
        "notificationsInfoIcon.foreground": A,
        "editorHoverWidget.statusBarBackground": chrome2,
        # terminal
        "terminal.background": content, "terminal.foreground": text, "terminalCursor.foreground": text,
        "terminal.selectionBackground": alpha(A, 0.3), "terminal.border": soft,
        "terminal.ansiBlack": text if not dark else "#3A3936", "terminal.ansiRed": t["negative"],
        "terminal.ansiGreen": t["positive"], "terminal.ansiYellow": t["neutral"], "terminal.ansiBlue": t["link"],
        "terminal.ansiMagenta": t["visited"], "terminal.ansiCyan": s["type"],
        "terminal.ansiWhite": t["textDisabled"] if not dark else text2,
        "terminal.ansiBrightBlack": text2, "terminal.ansiBrightRed": mix(t["negative"], content, 0.2),
        "terminal.ansiBrightGreen": mix(t["positive"], content, 0.2), "terminal.ansiBrightYellow": mix(t["neutral"], content, 0.2),
        "terminal.ansiBrightBlue": mix(t["link"], content, 0.2), "terminal.ansiBrightMagenta": mix(t["visited"], content, 0.2),
        "terminal.ansiBrightCyan": mix(s["type"], content, 0.2), "terminal.ansiBrightWhite": text if dark else chrome2,
        # git decorations
        "gitDecoration.addedResourceForeground": t["positive"], "gitDecoration.untrackedResourceForeground": t["positive"],
        "gitDecoration.modifiedResourceForeground": t["neutral"], "gitDecoration.deletedResourceForeground": t["negative"],
        "gitDecoration.ignoredResourceForeground": t["textDisabled"], "gitDecoration.conflictingResourceForeground": t["negative"],
        "settings.headerForeground": text, "settings.modifiedItemIndicator": A,
        "welcomePage.tileBackground": raised, "walkThrough.embeddedEditorBackground": chrome2,
    }
    colors = {k: v for k, v in colors.items() if v is not None}

    def rule(scope, fg, style=None):
        r = {"scope": scope, "settings": {"foreground": fg}}
        if style:
            r["settings"]["fontStyle"] = style
        return r

    token_colors = [
        rule(["comment", "punctuation.definition.comment"], s["comment"], "italic"),
        rule(["keyword", "storage", "storage.type", "storage.modifier", "keyword.control"], s["keyword"]),
        rule(["keyword.operator", "punctuation.separator", "punctuation.accessor"], s["operator"]),
        rule(["string", "punctuation.definition.string", "markup.inline.raw"], s["string"]),
        rule(["string.regexp", "constant.character.escape"], s["regexp"]),
        rule(["constant.numeric", "constant.language.boolean"], s["number"]),
        rule(["constant", "constant.language", "variable.other.constant", "support.constant"], s["constant"]),
        rule(["entity.name.function", "support.function", "meta.function-call entity.name.function"], s["function"]),
        rule(["entity.name.type", "entity.name.class", "support.type", "support.class", "entity.other.inherited-class"], s["type"]),
        rule(["entity.name.tag", "meta.tag.sgml"], s["tag"]),
        rule(["entity.other.attribute-name", "support.type.property-name"], s["attribute"]),
        rule(["variable", "variable.parameter", "meta.definition.variable"], text),
        rule(["variable.language", "variable.language.this", "variable.language.self"], s["keyword"], "italic"),
        rule(["entity.name.namespace", "entity.name.module"], s["type"]),
        rule(["markup.heading", "entity.name.section"], s["function"], "bold"),
        rule(["markup.bold"], text, "bold"),
        rule(["markup.italic"], text, "italic"),
        rule(["markup.underline.link", "string.other.link"], t["link"]),
        rule(["markup.inserted"], t["positive"]),
        rule(["markup.deleted"], t["negative"]),
        rule(["markup.changed"], t["neutral"]),
        rule(["invalid", "invalid.illegal"], s["invalid"]),
    ]
    semantic = {
        "namespace": s["type"], "class": s["type"], "type": s["type"], "interface": s["type"], "enum": s["type"],
        "typeParameter": s["type"], "function": s["function"], "method": s["function"], "macro": s["constant"],
        "parameter": text, "variable": text, "property": text, "enumMember": s["constant"],
        "variable.readonly": s["constant"], "keyword": s["keyword"], "string": s["string"], "number": s["number"],
        "regexp": s["regexp"], "comment": {"foreground": s["comment"], "italic": True},
    }
    return {
        "name": f"Platinum Neue {mode.title()}",
        "type": "dark" if dark else "light",
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": token_colors,
        "semanticTokenColors": semantic,
    }


PACKAGE = {
    "name": "platinum-neue",
    "displayName": "Platinum Neue",
    "description": "A modern progression of Mac OS 8/9 Platinum, in light and dark. Part of the Platinum Neue desktop theme.",
    "version": VERSION,
    "publisher": PUBLISHER,
    "license": "GPL-2.0-or-later",
    "engines": {"vscode": "^1.70.0"},
    "categories": ["Themes"],
    "contributes": {"themes": [
        {"label": "Platinum Neue Light", "uiTheme": "vs", "path": "./themes/platinum-neue-light.json"},
        {"label": "Platinum Neue Dark", "uiTheme": "vs-dark", "path": "./themes/platinum-neue-dark.json"},
    ]},
}

README = """# Platinum Neue for VS Code

Light and dark colour themes matching the Platinum Neue KDE Plasma theme. Generated by
tools/gen_vscode.py from tokens/tokens.json.

Recommended settings, to match the rest of the desktop:

    "window.titleBarStyle": "native",
    "window.autoDetectColorScheme": true,
    "workbench.preferredLightColorTheme": "Platinum Neue Light",
    "workbench.preferredDarkColorTheme": "Platinum Neue Dark",
    "editor.scrollbar.verticalScrollbarSize": 20,
    "editor.scrollbar.horizontalScrollbarSize": 20
"""

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="{name}" Version="{version}" Publisher="{publisher}"/>
    <DisplayName>{display}</DisplayName>
    <Description xml:space="preserve">{desc}</Description>
    <Categories>Themes</Categories>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="{engine}"/>
      <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="ui,workspace"/>
    </Properties>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"/>
  </Assets>
</PackageManifest>
"""

CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".md" ContentType="text/markdown"/>
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
</Types>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (EXT / "themes").mkdir(parents=True)
    (EXT / "package.json").write_text(json.dumps(PACKAGE, indent=2) + "\n")
    (EXT / "README.md").write_text(README)
    for mode in ("light", "dark"):
        (EXT / "themes" / f"platinum-neue-{mode}.json").write_text(json.dumps(theme(mode), indent=2) + "\n")

    # a .vsix is a zip: manifest + content types + the extension folder
    vsix = OUT / f"platinum-neue-{VERSION}.vsix"
    with zipfile.ZipFile(vsix, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("extension.vsixmanifest", MANIFEST.format(
            name=PACKAGE["name"], version=VERSION, publisher=PUBLISHER, display=PACKAGE["displayName"],
            desc=PACKAGE["description"], engine=PACKAGE["engines"]["vscode"]))
        for f in sorted(EXT.rglob("*")):
            if f.is_file():
                z.write(f, "extension/" + f.relative_to(EXT).as_posix())
    print(f"wrote {vsix}")


if __name__ == "__main__":
    main()
