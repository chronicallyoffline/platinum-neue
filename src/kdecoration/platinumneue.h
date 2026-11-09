/*
 * SPDX-FileCopyrightText: 2014 Hugo Pereira Da Costa <hugo.pereira@free.fr>
 *
 * SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
 */

#pragma once

#include "platinumneuesettings.h"

#include <QList>
#include <QSharedPointer>

namespace PlatinumNeue
{
//* convenience typedefs
using InternalSettingsPtr = QSharedPointer<InternalSettings>;
using InternalSettingsList = QList<InternalSettingsPtr>;
using InternalSettingsListIterator = QListIterator<InternalSettingsPtr>;

//* metrics
namespace Metrics
{
//* corner radius, in units of small spacing
// Keep this value in sync with Bias_Default in
// kstyle/platinumneuemetrics.h
// NOTE: this value is multiplied by settings()->smallSpacing()
// which is always 2 on wayland, but can be something else on X11
// Platinum Neue: 3px corners (1.5 x smallSpacing of 2)
static constexpr qreal Frame_FrameRadius = 1.5;

//* titlebar metrics, in units of small spacing
// Platinum Neue: buttons and caption fill the full titlebar height, so no vertical margins.
static constexpr int TitleBar_TopMargin = 0;
static constexpr int TitleBar_BottomMargin = 0;
static constexpr int TitleBar_SideMargin = 2;
static constexpr int TitleBar_ButtonSpacing = 0;

//* Platinum Neue titlebar metrics, in logical pixels (see tokens/tokens.json)
static constexpr int TitleBar_MinHeight = 26;
static constexpr int TitleBar_TextPadding = 4; // above and below the caption text
static constexpr int TitleBar_ButtonGap = 6; // visible gap between button boxes
static constexpr int TitleBar_StripeGap = 8; // between pinstripes and caption text
static constexpr int TitleBar_StripeMin = 12; // shortest stripe run worth drawing
static constexpr int Pinstripe_Count = 3;
static constexpr int Pinstripe_Pitch = 4;

// shadow dimensions (pixels)
static constexpr int Shadow_Overlap = 3;

// frame intensities (called bias in KColorUtilities::Mix)
// Keep this value in sync with Bias_Default in
// kstyle/platinumneuemetrics.h
static constexpr qreal Bias_Default = 0.20;
}

//* standard pen widths
namespace PenWidth
{
/* Using 1 instead of slightly more than 1 causes symbols drawn with
 * pen strokes to look skewed. The exact amount added does not matter
 * as long as it isn't too visible.
 */
// The standard pen stroke width for symbols.
static constexpr qreal Symbol = 1.01;
}

//* exception
enum ExceptionMask {
    None = 0,
    BorderSize = 1 << 4,
};
}
