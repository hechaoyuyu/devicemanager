#ifndef _LSHW_H_
#define _LSHW_H_

#include <boost/python.hpp>
#include "main.h"
#include "options.h"
#include "super.h"
#include "stream.h"
#include "sensors.h"

using namespace boost::python;


class lshw
{
public:
    lshw();
    virtual ~lshw();

    void scan_device();
    string get_xml();

private:
    hwNode *computer;
};

char *degree_sign();

#endif