#!/usr/bin/env python3
"""Widget gallery for checking the GTK theme. Usage: gtk-gallery.py 3|4 [--csd]"""
import sys

import gi

VER = sys.argv[1] if len(sys.argv) > 1 else "3"
CSD = "--csd" in sys.argv
gi.require_version("Gtk", f"{VER}.0")
from gi.repository import GLib, Gtk  # noqa: E402

G4 = VER == "4"


def add(box, w):
    box.append(w) if G4 else box.pack_start(w, False, False, 0)


def hbox(sp=8):
    return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=sp)


def vbox(sp=8):
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=sp)


def scrolled(child, w, h):
    sw = Gtk.ScrolledWindow()
    sw.set_size_request(w, h)
    sw.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
    sw.set_overlay_scrolling(False)
    if G4:
        sw.set_child(child)
        sw.set_has_frame(True)
    else:
        sw.add(child)
        sw.set_shadow_type(Gtk.ShadowType.IN)
    return sw


def build(win):
    root = vbox(10)
    for m in ("set_margin_top", "set_margin_bottom", "set_margin_start", "set_margin_end"):
        getattr(root, m)(12)

    row = hbox()
    add(row, Gtk.Button(label="Cancel"))
    ok = Gtk.Button(label="Apply")
    ok.get_style_context().add_class("suggested-action")
    add(row, ok)
    rm = Gtk.Button(label="Delete")
    rm.get_style_context().add_class("destructive-action")
    add(row, rm)
    tb = Gtk.ToggleButton(label="Toggled")
    tb.set_active(True)
    add(row, tb)
    dis = Gtk.Button(label="Disabled")
    dis.set_sensitive(False)
    add(row, dis)
    flat = Gtk.Button(label="Flat")
    flat.get_style_context().add_class("flat")
    add(row, flat)
    linked = hbox(0)
    linked.get_style_context().add_class("linked")
    for t in ("Left", "Middle", "Right"):
        add(linked, Gtk.Button(label=t))
    add(row, linked)
    add(root, row)

    row = hbox()
    e = Gtk.Entry()
    e.set_text("Text field")
    add(row, e)
    e2 = Gtk.Entry()
    e2.set_placeholder_text("Disabled")
    e2.set_sensitive(False)
    add(row, e2)
    add(row, Gtk.SpinButton.new_with_range(0, 100, 1))
    combo = Gtk.ComboBoxText()
    for t in ("Name", "Size", "Date"):
        combo.append_text(t)
    combo.set_active(0)
    add(row, combo)
    add(root, row)

    row = hbox(14)
    for label, state in (("Unchecked", 0), ("Checked", 1), ("Mixed", 2)):
        c = Gtk.CheckButton(label=label)
        c.set_active(state == 1)
        if state == 2:
            c.set_inconsistent(True)
        add(row, c)
    r1 = Gtk.CheckButton(label="Radio on") if G4 else Gtk.RadioButton(label="Radio on")
    r2 = Gtk.CheckButton(label="Radio off") if G4 else Gtk.RadioButton.new_with_label_from_widget(r1, "Radio off")
    if G4:
        r2.set_group(r1)
    r1.set_active(True)
    add(row, r1)
    add(row, r2)
    s1 = Gtk.Switch()
    s1.set_active(True)
    s1.set_valign(Gtk.Align.CENTER)
    add(row, s1)
    s2 = Gtk.Switch()
    s2.set_valign(Gtk.Align.CENTER)
    add(row, s2)
    add(root, row)

    row = hbox(14)
    sc = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    sc.set_value(60)
    sc.set_draw_value(False)
    sc.set_size_request(200, -1)
    add(row, sc)
    pb = Gtk.ProgressBar()
    pb.set_fraction(0.45)
    pb.set_size_request(200, -1)
    pb.set_valign(Gtk.Align.CENTER)
    add(row, pb)
    add(root, row)

    row = hbox(12)
    nb = Gtk.Notebook()
    for i, t in enumerate(("General", "Appearance", "Other")):
        lab = Gtk.Label(label=f"{t} settings")
        lab.set_size_request(260, 120)
        nb.append_page(lab, Gtk.Label(label=t))
    add(row, nb)
    GLib.idle_add(nb.set_current_page, 0)

    store = Gtk.ListStore(str, str, str)
    for r in (("Documents", "4 items", "Today"), ("Music", "112 items", "Yesterday"), ("Pictures", "38 items", "Oct 30"),
              ("notes.md", "2.1 KB", "Today"), ("report.pdf", "880 KB", "Nov 2"), ("theme.svg", "14 KB", "Nov 6"),
              ("tokens.json", "3.4 KB", "Today"), ("a.txt", "1 KB", "Today"), ("b.txt", "1 KB", "Today")):
        store.append(r)
    tv = Gtk.TreeView(model=store)
    for i, t in enumerate(("Name", "Size", "Modified")):
        col = Gtk.TreeViewColumn(t, Gtk.CellRendererText(), text=i)
        col.set_sort_column_id(i)
        col.set_min_width(110)
        tv.append_column(col)
    tv.get_selection().select_path(Gtk.TreePath.new_from_string("2"))
    add(row, scrolled(tv, 300, 160))
    add(root, row)

    if G4:
        win.set_child(root)
    else:
        win.add(root)

    if CSD:
        hb = Gtk.HeaderBar()
        if G4:
            hb.set_title_widget(Gtk.Label(label="Gallery"))
        else:
            hb.set_title("Gallery")
            hb.set_show_close_button(True)
        mb = Gtk.Button(label="Open")
        hb.pack_start(mb)
        win.set_titlebar(hb)


def main():
    if G4:
        app = Gtk.Application(application_id="org.platinumneue.gtkgallery4")

        def act(a):
            w = Gtk.ApplicationWindow(application=a, title=f"GTK {VER} gallery")
            w.set_default_size(820, 470)
            build(w)
            w.present()

        app.connect("activate", act)
        app.run([])
    else:
        w = Gtk.Window(title=f"GTK {VER} gallery")
        w.set_default_size(820, 470)
        w.connect("destroy", Gtk.main_quit)
        build(w)
        w.show_all()
        Gtk.main()


if __name__ == "__main__":
    main()
