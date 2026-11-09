//////////////////////////////////////////////////////////////////////////////
// platinumneueanimationconfigitem.h
// animation configuration item
// -------------------
//
// SPDX-FileCopyrightText: 2010 Hugo Pereira Da Costa <hugo.pereira@free.fr>
//
// SPDX-License-Identifier: MIT
//////////////////////////////////////////////////////////////////////////////

#include <QAbstractScrollArea>
#include <QApplication>
#include <QIcon>

#include <KCMultiDialog>
#include <KLocalizedString>
#include <KPluginMetaData>

//__________________________________________
int main(int argc, char *argv[])
{
    KLocalizedString::setApplicationDomain("platinumneue_style_config");

    QApplication app(argc, argv);
    app.setApplicationName(i18n("PlatinumNeue Settings"));
    app.setWindowIcon(QIcon::fromTheme(QStringLiteral("platinumneue-settings")));

    KCMultiDialog dialog;
    dialog.setWindowTitle(i18n("PlatinumNeue Settings"));
    dialog.addModule(KPluginMetaData(QStringLiteral("kstyle_config/platinumneuestyleconfig")));
    dialog.addModule(KPluginMetaData(QStringLiteral("org.kde.kdecoration3.kcm/kcm_platinumneuedecoration.so")));
    dialog.show();

    const auto children = dialog.findChildren<QAbstractScrollArea *>();
    for (auto child : children) {
        child->adjustSize();
        child->viewport()->adjustSize();
    }

    return app.exec();
}
