set(platinumneuedecoration_config_SRCS
    ../platinumneueexceptionlist.cpp
    platinumneueconfigwidget.cpp
    platinumneuedetectwidget.cpp
    platinumneueexceptiondialog.cpp
    platinumneueexceptionlistwidget.cpp
    platinumneueexceptionmodel.cpp
    platinumneueitemmodel.cpp
)
ki18n_wrap_ui(platinumneuedecoration_config_SRCS
   ui/platinumneueconfigurationui.ui
   ui/platinumneueexceptiondialog.ui
   ui/platinumneueexceptionlistwidget.ui
)

kcoreaddons_add_plugin(kcm_platinumneuedecoration SOURCES kcm_platinumneuedecoration.cpp ${platinumneuedecoration_config_SRCS} INSTALL_NAMESPACE "${KDECORATION_KCM_PLUGIN_DIR}")
kconfig_add_kcfg_files(kcm_platinumneuedecoration ../platinumneuesettings.kcfgc)
target_include_directories(kcm_platinumneuedecoration PRIVATE ${CMAKE_SOURCE_DIR}/kdecoration ${CMAKE_BINARY_DIR}/kdecoration/)
target_link_libraries(kcm_platinumneuedecoration
    PUBLIC
        Qt6::Core
        Qt6::Gui
        Qt6::DBus
    PRIVATE
        KF6::ConfigCore
        KF6::CoreAddons
        KF6::GuiAddons
        KF6::I18n
        KF6::IconThemes
        KF6::KCMUtils
)
kcmutils_generate_desktop_file(kcm_platinumneuedecoration)

# kcmshell6 < 6.27.0 doesn't know the --smoke-test param, so skip this test for
# now.
# TODO: Drop this when KF6_MIN_VERSION >= 6.27.0
if(KF6KCMUtils_VERSION VERSION_GREATER_EQUAL "6.27.0")
    add_test(NAME kcm_platinumneuedecoration_smoketest COMMAND kcmshell6 -style PlatinumNeue --smoke-test ${KDECORATION_KCM_PLUGIN_DIR}/kcm_platinumneuedecoration)
    set_tests_properties(kcm_platinumneuedecoration_smoketest PROPERTIES
        ENVIRONMENT_MODIFICATION QT_PLUGIN_PATH=path_list_prepend:${CMAKE_BINARY_DIR}/bin
    )
endif()
