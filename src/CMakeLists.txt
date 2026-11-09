# Platinum Neue: Qt style + KWin decoration, forked from KDE Breeze 6.8.2 (see UPSTREAM).
cmake_minimum_required(VERSION 3.16)
project(platinumneue VERSION 0.1.0)

set(KF6_MIN_VERSION "6.30.0")
set(QT_MIN_VERSION "6.11.0")
set(KDE_COMPILERSETTINGS_LEVEL "5.82")

find_package(ECM ${KF6_MIN_VERSION} REQUIRED NO_MODULE)
set(CMAKE_MODULE_PATH ${ECM_MODULE_PATH} ${CMAKE_SOURCE_DIR}/cmake)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(QT_MAJOR_VERSION 6)
set(QT_NO_CREATE_VERSIONLESS_TARGETS ON)
set(QT_NO_CREATE_VERSIONLESS_FUNCTIONS ON)
option(BUILD_TESTING "Build the testing tree." OFF)

include(KDEInstallDirs6)
include(KDECMakeSettings)
include(KDECompilerSettings NO_POLICY_SCOPE)
include(ECMQtDeclareLoggingCategory)
include(ECMInstallIcons)
include(FeatureSummary)
include(GenerateExportHeader)

find_package(Qt6 ${QT_MIN_VERSION} REQUIRED CONFIG COMPONENTS Widgets Core Svg DBus Quick)
set(HAVE_QTDBUS ON)
find_package(KF6 ${KF6_MIN_VERSION} REQUIRED COMPONENTS
    CoreAddons ColorScheme Config GuiAddons I18n IconThemes WindowSystem KCMUtils FrameworkIntegration)
find_package(KDecoration3 REQUIRED)

set(PLATINUMNEUE_HAVE_KSTYLE ON)
set(PLATINUMNEUE_HAVE_QTQUICK ON)

add_subdirectory(libplatinumneuecommon libplatinumneuecommon6)
add_subdirectory(kstyle kstyle6)
add_subdirectory(kdecoration)

feature_summary(WHAT ALL FATAL_ON_MISSING_REQUIRED_PACKAGES)
