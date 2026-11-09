add_library(platinumneuecommon${QT_MAJOR_VERSION} OBJECT platinumneueboxshadowrenderer.cpp)

set_target_properties(platinumneuecommon${QT_MAJOR_VERSION} PROPERTIES POSITION_INDEPENDENT_CODE TRUE)

target_link_libraries(platinumneuecommon${QT_MAJOR_VERSION}
    PUBLIC
        Qt${QT_MAJOR_VERSION}::Core
        Qt${QT_MAJOR_VERSION}::Gui)
