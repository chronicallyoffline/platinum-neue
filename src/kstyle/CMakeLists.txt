################# includes #################
include_directories(
  animations
  debug
)

include_directories(${CMAKE_SOURCE_DIR}/libplatinumneuecommon)
include_directories(${CMAKE_BINARY_DIR}/libplatinumneuecommon)

################# configuration #################
configure_file(config-platinumneue.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/config-platinumneue.h )

########### next target ###############
set(platinumneue_PART_SRCS
    animations/platinumneueanimation.cpp
    animations/platinumneueanimations.cpp
    animations/platinumneueanimationdata.cpp
    animations/platinumneuebaseengine.cpp
    animations/platinumneuebusyindicatordata.cpp
    animations/platinumneuebusyindicatorengine.cpp
    animations/platinumneuedialdata.cpp
    animations/platinumneuedialengine.cpp
    animations/platinumneueenabledata.cpp
    animations/platinumneuegenericdata.cpp
    animations/platinumneueheaderviewdata.cpp
    animations/platinumneueheaderviewengine.cpp
    animations/platinumneuescrollbardata.cpp
    animations/platinumneuescrollbarengine.cpp
    animations/platinumneuespinboxengine.cpp
    animations/platinumneuespinboxdata.cpp
    animations/platinumneuestackedwidgetdata.cpp
    animations/platinumneuestackedwidgetengine.cpp
    animations/platinumneuetabbarengine.cpp
    animations/platinumneuetabbardata.cpp
    animations/platinumneuetoolboxengine.cpp
    animations/platinumneuetransitiondata.cpp
    animations/platinumneuetransitionwidget.cpp
    animations/platinumneuewidgetstateengine.cpp
    animations/platinumneuewidgetstatedata.cpp
    debug/platinumneuewidgetexplorer.cpp
    platinumneueaddeventfilter.cpp
    platinumneueblurhelper.cpp
    platinumneueframeshadow.cpp
    platinumneuehelper.cpp
    platinumneuemdiwindowshadow.cpp
    platinumneuemnemonics.cpp
    platinumneuepropertynames.cpp
    platinumneueshadowhelper.cpp
    platinumneuesplitterproxy.cpp
    platinumneuestyle.cpp
    platinumneuestyleplugin.cpp
    platinumneuetileset.cpp
    platinumneuewindowmanager.cpp
    platinumneuetoolsareamanager.cpp
)

kconfig_add_kcfg_files(platinumneue_PART_SRCS ../kdecoration/platinumneuesettings.kcfgc)
kconfig_add_kcfg_files(platinumneue_PART_SRCS platinumneuestyleconfigdata.kcfgc)


add_library(platinumneue${QT_MAJOR_VERSION} MODULE ${platinumneue_PART_SRCS})

ecm_qt_declare_logging_category(platinumneue${QT_MAJOR_VERSION}
    HEADER
        platinumneue_logging.h
    IDENTIFIER
        PLATINUMNEUE
    CATEGORY_NAME
        platinumneue${QT_MAJOR_VERSION}
    DEFAULT_SEVERITY
        Warning
)

target_link_libraries(platinumneue${QT_MAJOR_VERSION}
    Qt${QT_MAJOR_VERSION}::Core
    Qt${QT_MAJOR_VERSION}::Gui
    Qt${QT_MAJOR_VERSION}::Widgets
)

if(HAVE_QTDBUS)
    target_link_libraries(platinumneue${QT_MAJOR_VERSION}
        Qt${QT_MAJOR_VERSION}::DBus
    )
endif()

if( PLATINUMNEUE_HAVE_QTQUICK )
    target_link_libraries(platinumneue${QT_MAJOR_VERSION} 
        Qt${QT_MAJOR_VERSION}::Quick
        KF${QT_MAJOR_VERSION}::CoreAddons
    )
endif()

target_link_libraries(platinumneue${QT_MAJOR_VERSION}
    KF${QT_MAJOR_VERSION}::CoreAddons
    KF${QT_MAJOR_VERSION}::ConfigCore
    KF${QT_MAJOR_VERSION}::ConfigGui
    KF${QT_MAJOR_VERSION}::GuiAddons
    KF${QT_MAJOR_VERSION}::IconThemes
    KF${QT_MAJOR_VERSION}::WindowSystem
)

if(QT_MAJOR_VERSION STREQUAL "5")
    target_link_libraries(platinumneue5 KF5::ConfigWidgets)
else()
    target_link_libraries(platinumneue6 KF6::ColorScheme)
endif()

target_link_libraries(platinumneue${QT_MAJOR_VERSION} platinumneuecommon${QT_MAJOR_VERSION})

if(KF${QT_MAJOR_VERSION}FrameworkIntegration_FOUND)
    target_link_libraries(platinumneue${QT_MAJOR_VERSION}  KF${QT_MAJOR_VERSION}::Style)
endif()


if (WIN32)
    # As stated in https://docs.microsoft.com/en-us/cpp/c-runtime-library/math-constants M_PI only gets defined
    # when if _USE_MATH_DEFINES is defined
    target_compile_definitions(platinumneue${QT_MAJOR_VERSION}  PRIVATE _USE_MATH_DEFINES _BSD_SOURCE)
endif()


########### install files ###############
install(TARGETS platinumneue${QT_MAJOR_VERSION}  DESTINATION ${KDE_INSTALL_QTPLUGINDIR}/styles/)
install(FILES platinumneue.themerc  DESTINATION  ${KDE_INSTALL_DATADIR}/kstyle/themes)
install(FILES platinumneue.kcfg DESTINATION ${KDE_INSTALL_KCFGDIR})

########### subdirectories ###############

if (QT_MAJOR_VERSION EQUAL "6" AND TARGET "KF6::KCMUtils")
    add_subdirectory(config)
endif()
