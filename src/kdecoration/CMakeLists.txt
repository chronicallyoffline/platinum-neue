add_definitions(-DTRANSLATION_DOMAIN="platinumneue_kwin_deco")

################# includes #################
include_directories(${CMAKE_SOURCE_DIR}/libplatinumneuecommon)
include_directories(${CMAKE_BINARY_DIR}/libplatinumneuecommon)

################# newt target #################
### plugin classes
set(platinumneuedecoration_SRCS
    platinumneuebutton.cpp
    platinumneuedecoration.cpp
    platinumneuesettingsprovider.cpp
    platinumneueexceptionlist.cpp
)

### build library
kconfig_add_kcfg_files(platinumneuedecoration_SRCS platinumneuesettings.kcfgc)
add_library(platinumneuedecoration MODULE
    ${platinumneuedecoration_SRCS}
    ${platinumneuedecoration_config_PART_FORMS_HEADERS})

set_target_properties(platinumneuedecoration PROPERTIES
    OUTPUT_NAME org.kde.platinumneue
)

target_link_libraries(platinumneuedecoration
    PRIVATE
        platinumneuecommon6
        Qt6::DBus
        KF6::CoreAddons
        KF6::ConfigGui
        KF6::GuiAddons
        KF6::I18n
        KF6::IconThemes
        KDecoration3::KDecoration
        KF6::ColorScheme
)

install(TARGETS platinumneuedecoration DESTINATION ${KDE_INSTALL_PLUGINDIR}/${KDECORATION_PLUGIN_DIR})
install(FILES platinumneuesettingsdata.kcfg DESTINATION ${KDE_INSTALL_KCFGDIR} RENAME platinumneue-decoration.kcfg)

add_subdirectory(config)

