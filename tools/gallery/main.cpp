// Widget gallery for checking the Platinum Neue style. Mirrors the mockup's "Controls" section.
#include <QtWidgets>

static QGroupBox *group(const QString &title, QLayout *layout)
{
    auto *g = new QGroupBox(title);
    g->setLayout(layout);
    return g;
}

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    QMainWindow win;
    win.setWindowTitle(QStringLiteral("Widget Gallery"));

    auto *view = win.menuBar()->addMenu(QStringLiteral("&File"));
    view->addAction(QStringLiteral("New Window"))->setShortcut(QKeySequence::New);
    win.menuBar()->addMenu(QStringLiteral("&Edit"));
    auto *v = win.menuBar()->addMenu(QStringLiteral("&View"));
    auto *tb = v->addAction(QStringLiteral("Show Toolbar"));
    tb->setCheckable(true);
    tb->setChecked(true);
    v->addAction(QStringLiteral("Show Hidden Files"))->setShortcut(QStringLiteral("Ctrl+H"));
    v->addSeparator();
    auto *sort = v->addMenu(QStringLiteral("Sort By"));
    sort->addAction(QStringLiteral("Name"));
    sort->addAction(QStringLiteral("Size"));
    v->addAction(QStringLiteral("Zoom Out"))->setEnabled(false);

    auto *toolbar = win.addToolBar(QStringLiteral("Main"));
    toolbar->addAction(QIcon::fromTheme(QStringLiteral("go-previous")), QStringLiteral("Back"));
    toolbar->addAction(QIcon::fromTheme(QStringLiteral("go-next")), QStringLiteral("Forward"));
    auto *toggle = toolbar->addAction(QIcon::fromTheme(QStringLiteral("view-list-details")), QStringLiteral("Details"));
    toggle->setCheckable(true);
    toggle->setChecked(true);
    auto *location = new QLineEdit(QStringLiteral("Home / Documents"));
    location->setMinimumWidth(220);
    toolbar->addWidget(location);
    auto *split = new QToolButton;
    split->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    split->setIcon(QIcon::fromTheme(QStringLiteral("view-split-left-right")));
    split->setText(QStringLiteral("Split"));
    split->setCheckable(true);
    split->setChecked(true); // checked so its frame is visible in screenshots
    toolbar->addWidget(split);
    toolbar->setIconSize(QSize(22, 22));

    auto *central = new QWidget;
    auto *grid = new QGridLayout(central);

    // buttons
    auto *b = new QVBoxLayout;
    auto *row = new QHBoxLayout;
    row->addWidget(new QPushButton(QStringLiteral("Cancel")));
    auto *apply = new QPushButton(QStringLiteral("Apply"));
    apply->setDefault(true);
    row->addWidget(apply);
    auto *dis = new QPushButton(QStringLiteral("Disabled"));
    dis->setEnabled(false);
    row->addWidget(dis);
    b->addLayout(row);
    auto *row2 = new QHBoxLayout;
    auto *on = new QPushButton(QStringLiteral("Toggle on"));
    on->setCheckable(true);
    on->setChecked(true);
    row2->addWidget(on);
    auto *tbtn = new QToolButton;
    tbtn->setIcon(QIcon::fromTheme(QStringLiteral("view-sort")));
    tbtn->setAutoRaise(true);
    row2->addWidget(tbtn);
    row2->addStretch();
    b->addLayout(row2);
    grid->addWidget(group(QStringLiteral("Buttons"), b), 0, 0);

    // choices
    auto *c = new QVBoxLayout;
    auto *c1 = new QCheckBox(QStringLiteral("Open folders in new tabs"));
    c1->setChecked(true);
    auto *c2 = new QCheckBox(QStringLiteral("Preview some file types"));
    c2->setTristate(true);
    c2->setCheckState(Qt::PartiallyChecked);
    auto *c3 = new QCheckBox(QStringLiteral("Show thumbnails over network"));
    c3->setEnabled(false);
    auto *r1 = new QRadioButton(QStringLiteral("Double-click opens"));
    r1->setChecked(true);
    c->addWidget(c1);
    c->addWidget(c2);
    c->addWidget(c3);
    c->addWidget(r1);
    c->addWidget(new QRadioButton(QStringLiteral("Single-click")));
    grid->addWidget(group(QStringLiteral("Choices"), c), 0, 1);

    // fields
    auto *f = new QFormLayout;
    f->addRow(QStringLiteral("Name"), new QLineEdit(QStringLiteral("Platinum Neue")));
    auto *search = new QLineEdit;
    search->setPlaceholderText(QStringLiteral("Filter by name"));
    search->setClearButtonEnabled(true);
    f->addRow(QStringLiteral("Search"), search);
    auto *combo = new QComboBox;
    combo->addItems({QStringLiteral("Medium (10 pt)"), QStringLiteral("Large (12 pt)")});
    f->addRow(QStringLiteral("Size"), combo);
    auto *spin = new QSpinBox;
    spin->setValue(24);
    f->addRow(QStringLiteral("Height"), spin);
    auto *ro = new QLineEdit(QStringLiteral("Read only"));
    ro->setEnabled(false);
    f->addRow(QStringLiteral("Locked"), ro);
    grid->addWidget(group(QStringLiteral("Fields"), f), 1, 0);

    // ranges
    auto *r = new QVBoxLayout;
    auto *slider = new QSlider(Qt::Horizontal);
    slider->setRange(0, 100);
    slider->setValue(50);
    slider->setTickPosition(QSlider::TicksBelow);
    slider->setTickInterval(25);
    r->addWidget(slider);
    auto *p1 = new QProgressBar;
    p1->setValue(58);
    r->addWidget(p1);
    auto *p2 = new QProgressBar;
    p2->setRange(0, 0);
    r->addWidget(p2);
    grid->addWidget(group(QStringLiteral("Ranges"), r), 1, 1);

    // tabs + list
    auto *tabs = new QTabWidget;
    auto *pane = new QLabel(QStringLiteral("The selected tab joins its pane."));
    pane->setMargin(12);
    tabs->addTab(pane, QStringLiteral("General"));
    tabs->addTab(new QWidget, QStringLiteral("Previews"));
    tabs->addTab(new QWidget, QStringLiteral("Trash"));
    tabs->addTab(new QWidget, QStringLiteral("Other"));
    grid->addWidget(tabs, 2, 0);

    auto *tree = new QTreeWidget;
    tree->setHeaderLabels({QStringLiteral("Name"), QStringLiteral("Size"), QStringLiteral("Modified")});
    tree->setRootIsDecorated(false);
    const char *rows[][3] = {{"Documents", "4 items", "Today"},     {"Music", "112 items", "Yesterday"}, {"Pictures", "38 items", "Oct 30"},
                             {"notes.md", "2.1 KB", "Today"},       {"report.pdf", "880 KB", "Nov 2"},   {"theme.svg", "14 KB", "Nov 6"},
                             {"tokens.json", "3.4 KB", "Today"}};
    for (auto &row : rows) {
        new QTreeWidgetItem(tree, {QString::fromLatin1(row[0]), QString::fromLatin1(row[1]), QString::fromLatin1(row[2])});
    }
    tree->setSortingEnabled(true);
    tree->sortByColumn(0, Qt::AscendingOrder);
    tree->setCurrentItem(tree->topLevelItem(2));
    tree->setColumnWidth(0, 130);
    grid->addWidget(tree, 2, 1);

    win.setCentralWidget(central);
    win.statusBar()->showMessage(QStringLiteral("12 items, 3 folders"));
    win.resize(760, 600);
    win.show();
    apply->setFocus();
    // PN_MENU_PNG=<file> renders the View menu (with a highlighted row) to an image and exits
    if (qEnvironmentVariableIsSet("PN_MENU_PNG")) {
        v->ensurePolished();
        v->adjustSize();
        v->setActiveAction(sort->menuAction());
        v->grab().save(qEnvironmentVariable("PN_MENU_PNG"));
        // and a tooltip next to it
        struct Tip : QLabel {
            using QLabel::QLabel;
            void paintEvent(QPaintEvent *e) override
            {
                QStylePainter p(this);
                QStyleOptionFrame opt;
                opt.initFrom(this);
                p.drawPrimitive(QStyle::PE_PanelTipLabel, opt);
                QLabel::paintEvent(e);
            }
        } tip(QStringLiteral("Sort items by name"));
        tip.setForegroundRole(QPalette::ToolTipText);
        tip.setBackgroundRole(QPalette::ToolTipBase);
        tip.setPalette(QToolTip::palette());
        tip.setMargin(4);
        tip.setIndent(4);
        tip.adjustSize();
        QString out = qEnvironmentVariable("PN_MENU_PNG");
        tip.grab().save(out.replace(QStringLiteral(".png"), QStringLiteral("-tip.png")));
        // Dolphin-like document-mode tabs beside a framed sidebar, middle tab selected
        QWidget doc;
        auto *h = new QHBoxLayout(&doc);
        h->setContentsMargins(0, 0, 0, 0);
        h->setSpacing(0);
        auto *side = new QFrame;
        side->setFrameShape(QFrame::StyledPanel);
        side->setFixedWidth(60);
        h->addWidget(side);
        auto *dt = new QTabWidget;
        dt->setDocumentMode(true);
        dt->setTabsClosable(true);
        dt->setMovable(true);
        for (const char *t : {"pkg", "src", "tools"}) {
            dt->addTab(new QWidget, QString::fromLatin1(t));
        }
        dt->setCurrentIndex(1);
        h->addWidget(dt);
        doc.resize(360, 90);
        QString out2 = qEnvironmentVariable("PN_MENU_PNG");
        doc.grab().save(out2.replace(QStringLiteral(".png"), QStringLiteral("-doctabs.png")));

        // scroll area with both scrollbars, for checking scrollbar metrics
        QPlainTextEdit edit;
        edit.setLineWrapMode(QPlainTextEdit::NoWrap);
        QString text;
        for (int i = 0; i < 80; ++i) {
            text += QStringLiteral("Line %1 of a long document that runs well past the right edge of the view\n").arg(i);
        }
        edit.setPlainText(text);
        edit.resize(300, 180);
        edit.setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOn);
        edit.verticalScrollBar()->setValue(20);
        edit.show();
        QString out3 = qEnvironmentVariable("PN_MENU_PNG");
        edit.grab().save(out3.replace(QStringLiteral(".png"), QStringLiteral("-scroll.png")));

        // a Gwenview-like status row: every framed control should be the same height
        QWidget row;
        auto *rl = new QHBoxLayout(&row);
        auto *fit = new QToolButton;
        fit->setText(QStringLiteral("Fit"));
        auto *zoom = new QToolButton;
        zoom->setIcon(QIcon::fromTheme(QStringLiteral("zoom-in")));
        auto *thumbs = new QPushButton(QStringLiteral("Show Thumbnails"));
        auto *zcombo = new QComboBox;
        zcombo->setEditable(true);
        zcombo->addItem(QStringLiteral("400%"));
        auto *zslider = new QSlider(Qt::Horizontal);
        zslider->setValue(30);
        auto *cap = new QProgressBar;
        cap->setValue(4);
        cap->setTextVisible(false);
        for (QWidget *w : {static_cast<QWidget *>(fit), static_cast<QWidget *>(zoom), static_cast<QWidget *>(thumbs),
                           static_cast<QWidget *>(zcombo), static_cast<QWidget *>(zslider), static_cast<QWidget *>(cap)}) {
            rl->addWidget(w);
        }
        row.resize(620, 50);
        row.show();
        QCoreApplication::processEvents();
        QLineEdit le;
        QSpinBox sb;
        QComboBox plainCombo;
        plainCombo.addItem(QStringLiteral("Name"));
        QPushButton iconPush(QIcon::fromTheme(QStringLiteral("document-open")), QStringLiteral("Open"));
        for (QWidget *w : {static_cast<QWidget *>(fit), static_cast<QWidget *>(zoom), static_cast<QWidget *>(thumbs), static_cast<QWidget *>(&iconPush),
                           static_cast<QWidget *>(zcombo), static_cast<QWidget *>(&plainCombo), static_cast<QWidget *>(&le), static_cast<QWidget *>(&sb)}) {
            printf("%s height %d\n", w->metaObject()->className(), w->sizeHint().height());
        }
        // pressed vs unpressed, as in a segmented toggle row
        QWidget prow;
        auto *pl = new QHBoxLayout(&prow);
        for (const char *t : {"Mask", "Effect", "Refresh"}) {
            auto *b = new QPushButton(QString::fromLatin1(t));
            b->setCheckable(true);
            b->setChecked(QByteArray(t) == "Effect");
            pl->addWidget(b);
        }
        auto *tbOn = new QToolButton;
        tbOn->setIcon(QIcon::fromTheme(QStringLiteral("view-list-details")));
        tbOn->setCheckable(true);
        tbOn->setChecked(true);
        pl->addWidget(tbOn);
        auto *tbOff = new QToolButton;
        tbOff->setIcon(QIcon::fromTheme(QStringLiteral("view-list-icons")));
        tbOff->setCheckable(true);
        pl->addWidget(tbOff);
        prow.resize(420, 50);
        prow.show();
        QCoreApplication::processEvents();
        QString out5 = qEnvironmentVariable("PN_MENU_PNG");
        prow.grab().save(out5.replace(QStringLiteral(".png"), QStringLiteral("-pressed.png")));

        QString out4 = qEnvironmentVariable("PN_MENU_PNG");
        row.grab().save(out4.replace(QStringLiteral(".png"), QStringLiteral("-row.png")));
        return 0;
    }
    // PN_GALLERY_MENU=1 opens View > Sort By after start, for screenshots of menus
    if (qEnvironmentVariableIsSet("PN_GALLERY_MENU")) {
        QTimer::singleShot(1500, &win, [&win, v, sort]() {
            const QRect r = win.menuBar()->actionGeometry(v->menuAction());
            v->popup(win.menuBar()->mapToGlobal(r.bottomLeft()));
            QTimer::singleShot(400, v, [v, sort]() {
                v->setActiveAction(sort->menuAction());
                sort->popup(v->mapToGlobal(v->actionGeometry(sort->menuAction()).topRight()));
            });
        });
    }
    return app.exec();
}
