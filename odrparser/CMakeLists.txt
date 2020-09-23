cmake_minimum_required(VERSION 2.8.3)
# based on https://cliutils.gitlab.io/modern-cmake/

# define project
project(odrparser)

# c++ version
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/findTinyXML2)

find_package(catkin REQUIRED)

find_package(TinyXML2 REQUIRED)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES ${PROJECT_NAME}
  DEPENDS TinyXML2 
)

include_directories(
 include
 ${catkin_INCLUDE_DIRS}
 ${TinyXML2_INCLUDE_DIRS}
)

add_library(${PROJECT_NAME} 
    src/loadFile.cc
    src/odr_1_5.cc
    src/odr_1_5.hpp
)
target_link_libraries(${PROJECT_NAME} ${catkin_LIBRARIES} ${TinyXML2_LIBRARIES})