// svgbounds <file.svg[z]> <id>... : print the bounds Plasma's FrameSvg sees for each element (QSvgRenderer::boundsOnElement)
#include <QGuiApplication>
#include <QSvgRenderer>
#include <QTransform>
#include <cstdio>
int main(int argc, char **argv)
{
    QGuiApplication app(argc, argv);
    QSvgRenderer r(QString::fromLocal8Bit(argv[1]));
    for (int i = 2; i < argc; ++i) {
        const QString id = QString::fromLocal8Bit(argv[i]);
        if (!r.elementExists(id)) { std::printf("%-28s missing\n", argv[i]); continue; }
        const QRectF b = r.transformForElement(id).mapRect(r.boundsOnElement(id));
        std::printf("%-28s %7.2f %7.2f %7.2f %7.2f\n", argv[i], b.x(), b.y(), b.width(), b.height());
    }
}
