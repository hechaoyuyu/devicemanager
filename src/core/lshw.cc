/* 
 * File:   lshw.cc
 * Author: hechao
 * 
 * Created on 2011年10月13日, 下午1:25
 */

#include "lshw.h"

lshw::lshw()
{
    computer = new hwNode("computer", hw::system);
}

lshw::~lshw()
{
    if (computer)
        delete computer;
}

void lshw::scan_device()
{
    enable("output:numeric");
    disable("output:sanitize");
    scan_system(*computer);
}

string lshw::get_xml()
{
    return computer->asXML();
}


BOOST_PYTHON_MODULE(lshw)
{
    class_<lshw, boost::noncopyable > ("lshw", "This is a lshw project python extend", init<>())
            .def("scan_device", &lshw::scan_device)
            .def("get_xml", &lshw::get_xml)
            ;
    def("sensors", &sensors);
    def("record_sign", &record_sign);
    def("stream_triad", &stream_triad);
    def("super_pi", &super_pi);
}