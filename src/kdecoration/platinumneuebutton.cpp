/*
 * SPDX-FileCopyrightText: 2014 Martin Gräßlin <mgraesslin@kde.org>
 * SPDX-FileCopyrightText: 2014 Hugo Pereira Da Costa <hugo.pereira@free.fr>
 *
 * SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
 */
#include "platinumneuebutton.h"

#include <KColorUtils>
#include <KDecoration3/DecoratedWindow>
#include <KDecoration3/ScaleHelpers>
#include <KIconLoader>

#include <QPainter>
#include <QPainterPath>
#include <QVariantAnimation>

namespace PlatinumNeue
{
using KDecoration3::ColorGroup;
using KDecoration3::ColorRole;
using KDecoration3::DecorationButtonType;

//__________________________________________________________________
Button::Button(DecorationButtonType type, Decoration *decoration, QObject *parent)
    : DecorationButton(type, decoration, parent)
    , m_animation(new QVariantAnimation(this))
{
    // setup animation
    // It is important start and end value are of the same type, hence 0.0 and not just 0
    m_animation->setStartValue(0.0);
    m_animation->setEndValue(1.0);
    m_animation->setEasingCurve(QEasingCurve::InOutQuad);
    connect(m_animation, &QVariantAnimation::valueChanged, this, [this](const QVariant &value) {
        setOpacity(value.toReal());
    });

    // connections
    connect(decoration->window(), SIGNAL(iconChanged(QIcon)), this, SLOT(update()));
    connect(decoration->settings().get(), &KDecoration3::DecorationSettings::reconfigured, this, &Button::reconfigure);
    connect(this, &KDecoration3::DecorationButton::hoveredChanged, this, &Button::updateAnimationState);
    // hovering one button reveals every glyph, so repaint them all
    connect(this, &KDecoration3::DecorationButton::hoveredChanged, decoration, [decoration]() {
        decoration->update();
    });

    reconfigure();
}

//__________________________________________________________________
Button::Button(QObject *parent, const QVariantList &args)
    : Button(args.at(0).value<DecorationButtonType>(), args.at(1).value<Decoration *>(), parent)
{
    setGeometry(QRectF(QPointF(0, 0), preferredSize()));
}

//__________________________________________________________________
Button *Button::create(DecorationButtonType type, KDecoration3::Decoration *decoration, QObject *parent)
{
    if (auto d = qobject_cast<Decoration *>(decoration)) {
        Button *b = new Button(type, d, parent);
        const auto c = d->window();
        switch (type) {
        case DecorationButtonType::Close:
            b->setVisible(c->isCloseable());
            QObject::connect(c, &KDecoration3::DecoratedWindow::closeableChanged, b, &PlatinumNeue::Button::setVisible);
            break;

        case DecorationButtonType::Maximize:
            b->setVisible(c->isMaximizeable());
            QObject::connect(c, &KDecoration3::DecoratedWindow::maximizeableChanged, b, &PlatinumNeue::Button::setVisible);
            break;

        case DecorationButtonType::Minimize:
            b->setVisible(c->isMinimizeable());
            QObject::connect(c, &KDecoration3::DecoratedWindow::minimizeableChanged, b, &PlatinumNeue::Button::setVisible);
            break;

        case DecorationButtonType::ContextHelp:
            b->setVisible(c->providesContextHelp());
            QObject::connect(c, &KDecoration3::DecoratedWindow::providesContextHelpChanged, b, &PlatinumNeue::Button::setVisible);
            break;

        case DecorationButtonType::Shade:
            b->setVisible(c->isShadeable());
            QObject::connect(c, &KDecoration3::DecoratedWindow::shadeableChanged, b, &PlatinumNeue::Button::setVisible);
            break;

        case DecorationButtonType::Menu:
            QObject::connect(c, &KDecoration3::DecoratedWindow::iconChanged, b, [b]() {
                b->update();
            });
            break;

        default:
            break;
        }

        return b;
    }

    return nullptr;
}

//__________________________________________________________________
void Button::paint(QPainter *painter, const QRectF &repaintRegion)
{
    Q_UNUSED(repaintRegion)

    if (!decoration()) {
        return;
    }

    switch (type()) {
    case KDecoration3::DecorationButtonType::Menu: {
        const QRectF area = geometry().marginsRemoved(m_padding);
        const auto pd = qobject_cast<Decoration *>(decoration());
        const qreal side = std::min({area.width(), area.height(), qreal(pd ? pd->buttonSize() + 2 : 16)});
        QRectF iconRect(0, 0, side, side);
        iconRect.moveCenter(area.center());
        const auto c = decoration()->window();
        if (auto deco = qobject_cast<Decoration *>(decoration())) {
            const QPalette activePalette = KIconLoader::global()->customPalette();
            QPalette palette = c->palette();
            palette.setColor(QPalette::WindowText, deco->fontColor());
            KIconLoader::global()->setCustomPalette(palette);
            c->icon().paint(painter, iconRect.toRect());
            if (activePalette == QPalette()) {
                KIconLoader::global()->resetPalette();
            } else {
                KIconLoader::global()->setCustomPalette(palette);
            }
        } else {
            c->icon().paint(painter, iconRect.toRect());
        }
        break;
    }
    case KDecoration3::DecorationButtonType::Spacer:
        break;
    default:
        painter->save();
        drawIcon(painter);
        painter->restore();
        break;
    }
}

//__________________________________________________________________
void Button::drawIcon(QPainter *painter) const
{
    auto d = qobject_cast<Decoration *>(decoration());
    if (!d) {
        return;
    }
    painter->setRenderHints(QPainter::Antialiasing);

    const auto c = d->window();
    const qreal scale = c->scale();
    const qreal px = std::max(KDecoration3::pixelSize(scale), KDecoration3::snapToPixelGrid(1, scale));
    const qreal radius = 2;

    // visible box, centred in the (larger) hit area and snapped to the pixel grid
    const QRectF area = geometry().marginsRemoved(m_padding);
    const qreal bs = d->buttonSize();
    const QRectF box(KDecoration3::snapToPixelGrid(area.center().x() - bs / 2, scale),
                     KDecoration3::snapToPixelGrid(area.center().y() - bs / 2, scale),
                     bs,
                     bs);
    const QRectF frame = box.adjusted(px / 2, px / 2, -px / 2, -px / 2);

    const bool active = c->isActive();
    const bool dark = d->isDarkTitleBar();
    const QColor titleBar = d->titleBarColor();
    const QColor text = c->color(ColorGroup::Active, ColorRole::Foreground);
    const QColor raised = c->palette().color(QPalette::Button);
    const QColor warn = c->color(ColorGroup::Warning, ColorRole::Foreground);
    const QColor line = KColorUtils::mix(titleBar, text, active ? 0.5 : 0.22);
    const QColor hi = dark ? QColor(255, 255, 255, 15) : QColor(255, 255, 255, 242);
    const QColor shade = dark ? QColor(0, 0, 0, 102) : QColor(40, 36, 30, 31);

    // toggles that are on look pressed in, like a pressed button
    const bool toggle = type() == DecorationButtonType::KeepAbove || type() == DecorationButtonType::KeepBelow
        || type() == DecorationButtonType::OnAllDesktops || type() == DecorationButtonType::ExcludeFromCapture || type() == DecorationButtonType::Shade;
    const bool down = isPressed() || (toggle && isChecked());

    auto topLine = [&](const QColor &color, qreal y) {
        painter->setPen(QPen(color, px));
        painter->drawLine(QPointF(frame.left() + radius, y), QPointF(frame.right() - radius, y));
    };

    if (down) {
        painter->setPen(QPen(line, px));
        painter->setBrush(KColorUtils::mix(titleBar, Qt::black, dark ? 0.2 : 0.06));
        painter->drawRoundedRect(frame, radius, radius);
        topLine(shade, frame.top() + px);
    } else if (active) {
        // 1px cast shadow, then the raised face
        painter->setPen(Qt::NoPen);
        painter->setBrush(shade);
        painter->drawRoundedRect(box.translated(0, px), radius, radius);

        QColor fill = raised;
        QColor border = line;
        if (type() == DecorationButtonType::Close) {
            // faint warm tint, never a full red
            fill = KColorUtils::mix(raised, warn, 0.16);
            border = KColorUtils::mix(line, warn, 0.4);
        }
        if (isHovered()) {
            fill = fill.lighter(dark ? 112 : 103);
        }
        painter->setPen(QPen(border, px));
        painter->setBrush(fill);
        painter->drawRoundedRect(frame, radius, radius);
        topLine(hi, frame.top() + px);
    } else {
        // inactive windows: plain outlines
        painter->setPen(QPen(line, px));
        painter->setBrush(Qt::NoBrush);
        painter->drawRoundedRect(frame, radius, radius);
    }

    // glyphs appear together when any button is hovered (and on the pressed one)
    if (!(isHovered() || isPressed() || d->anyButtonHovered())) {
        return;
    }

    QColor glyph = text;
    glyph.setAlphaF(0.85);
    painter->translate(box.topLeft());
    painter->scale(bs / 14.0, bs / 14.0);
    QPen pen(glyph, 1.4);
    pen.setCapStyle(Qt::RoundCap);
    pen.setJoinStyle(Qt::RoundJoin);
    painter->setPen(pen);
    painter->setBrush(Qt::NoBrush);

    switch (type()) {
    case DecorationButtonType::Close:
        painter->drawLine(QPointF(4.5, 4.5), QPointF(9.5, 9.5));
        painter->drawLine(QPointF(9.5, 4.5), QPointF(4.5, 9.5));
        break;
    case DecorationButtonType::Minimize:
        painter->drawLine(QPointF(4, 7), QPointF(10, 7));
        break;
    case DecorationButtonType::Maximize:
        if (isChecked()) {
            painter->drawRect(QRectF(4.5, 4.5, 5, 5));
        } else {
            painter->drawLine(QPointF(7, 4), QPointF(7, 10));
            painter->drawLine(QPointF(4, 7), QPointF(10, 7));
        }
        break;
    case DecorationButtonType::Shade:
        painter->drawLine(QPointF(4, 4.5), QPointF(10, 4.5));
        if (isChecked()) {
            painter->drawPolyline(QVector<QPointF>{QPointF(4.5, 7), QPointF(7, 9.5), QPointF(9.5, 7)});
        } else {
            painter->drawPolyline(QVector<QPointF>{QPointF(4.5, 9.5), QPointF(7, 7), QPointF(9.5, 9.5)});
        }
        break;
    case DecorationButtonType::KeepAbove:
        painter->drawPolyline(QVector<QPointF>{QPointF(4.5, 7), QPointF(7, 4.5), QPointF(9.5, 7)});
        painter->drawPolyline(QVector<QPointF>{QPointF(4.5, 10), QPointF(7, 7.5), QPointF(9.5, 10)});
        break;
    case DecorationButtonType::KeepBelow:
        painter->drawPolyline(QVector<QPointF>{QPointF(4.5, 4), QPointF(7, 6.5), QPointF(9.5, 4)});
        painter->drawPolyline(QVector<QPointF>{QPointF(4.5, 7), QPointF(7, 9.5), QPointF(9.5, 7)});
        break;
    case DecorationButtonType::OnAllDesktops:
        painter->setBrush(glyph);
        painter->setPen(Qt::NoPen);
        painter->drawEllipse(QPointF(7, 7), 1.8, 1.8);
        break;
    case DecorationButtonType::ApplicationMenu:
        painter->drawLine(QPointF(4, 4.5), QPointF(10, 4.5));
        painter->drawLine(QPointF(4, 7), QPointF(10, 7));
        painter->drawLine(QPointF(4, 9.5), QPointF(10, 9.5));
        break;
    case DecorationButtonType::ContextHelp: {
        QPainterPath path;
        path.moveTo(5, 5.5);
        path.arcTo(QRectF(5, 3.5, 4, 4), 180, -180);
        path.cubicTo(QPointF(9, 8), QPointF(7, 7.5), QPointF(7, 9));
        painter->drawPath(path);
        painter->drawPoint(QPointF(7, 11));
        break;
    }
    case DecorationButtonType::ExcludeFromCapture:
        painter->drawEllipse(QPointF(7, 7), 3, 3);
        painter->drawLine(QPointF(4, 10), QPointF(10, 4));
        break;
    default:
        break;
    }
}

//________________________________________________________________
void Button::reconfigure()
{
    // animation
    auto d = qobject_cast<Decoration *>(decoration());
    if (!d) {
        return;
    }

    switch (type()) {
    case KDecoration3::DecorationButtonType::Spacer:
        setPreferredSize(QSizeF(d->buttonSize() * 0.5, d->buttonSize()));
        break;
    default:
        // hit area is wider than the visible box by one button gap
        setPreferredSize(QSizeF(d->buttonSize() + Metrics::TitleBar_ButtonGap, d->buttonSize()));
        break;
    }

    m_animation->setDuration(d->animationsDuration());
}

//__________________________________________________________________
void Button::updateAnimationState(bool hovered)
{
    auto d = qobject_cast<Decoration *>(decoration());
    if (!(d && d->animationsDuration() > 0)) {
        return;
    }

    m_animation->setDirection(hovered ? QAbstractAnimation::Forward : QAbstractAnimation::Backward);
    if (m_animation->state() != QAbstractAnimation::Running) {
        m_animation->start();
    }
}

} // namespace
