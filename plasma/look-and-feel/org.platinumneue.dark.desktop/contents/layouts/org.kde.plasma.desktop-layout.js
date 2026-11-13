// Platinum Neue: a plain, full-width bottom panel with a serif clock
loadTemplate("org.kde.plasma.desktop.defaultPanel")

var panel = panels()[0];
if (panel) {
    panel.location = "bottom";
    panel.height = 40;
    panel.floating = false;
    var clocks = panel.widgets("org.kde.plasma.digitalclock");
    for (var i = 0; i < clocks.length; i++) {
        var c = clocks[i];
        c.currentConfigGroup = ["Appearance"];
        c.writeConfig("autoFontAndSize", false);
        c.writeConfig("fontFamily", "EB Garamond");
        c.writeConfig("fontWeight", 500);
        c.writeConfig("fontSize", 13);
        c.writeConfig("dateDisplayFormat", "BesideTime");
        c.writeConfig("dateFormat", "custom");
        c.writeConfig("customDateFormat", "ddd d MMM");
    }
}
