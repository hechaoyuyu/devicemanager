/* 
 * File:   lshw.cc
 * Author: hechao
 * 
 * Created on 2011年10月13日, 下午1:25
 */

#include <boost/python.hpp>
#include <cstdio>
#include <string>
#include <sensors/sensors.h>
#include <sensors/error.h>
#include <langinfo.h>
#include <iconv.h>
#include <dbus/dbus.h>
#include <stdbool.h>
#include <errno.h>
#include <stdlib.h>
#include <fstream>
#include <iostream>
#include "main.h"
#include "options.h"

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

using namespace boost::python;

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

//读取状态
/*
void status(const char *message)
{
    fstream out("/tmp/flag", ios::out);
    out << message;
    out.clear();
}
*/

void status(const char *message)
{
   DBusMessage* msg;
   DBusConnection* conn;
   DBusError err;

   // initialise the error value
   dbus_error_init(&err);

   // connect to the DBUS system bus, and check for errors
   conn = dbus_bus_get(DBUS_BUS_SYSTEM, &err);
   if (dbus_error_is_set(&err))
   {
      fprintf(stderr, "Connection Error (%s)\n", err.message);
      dbus_error_free(&err);
   }
   if (NULL == conn)
   {
      exit(1);
   }

   // create a signal & check for errors
   msg = dbus_message_new_signal("/com/ylmf/ydm", // object name of the signal
                                 "com.ylmf.ydm", // interface name of the signal
                                 "changed"); // name of the signal
   if (NULL == msg)
   {
      fprintf(stderr, "Message Null\n");
      exit(1);
   }

   // append arguments onto signal
   dbus_message_append_args(msg, DBUS_TYPE_STRING, &message, DBUS_TYPE_INVALID);

   // send the message and flush the connection
   if (!dbus_connection_send(conn, msg, NULL))
   {
      fprintf(stderr, "Out Of Memory!\n");
      exit(1);
   }
   dbus_connection_flush(conn);

   // free the message
   dbus_message_unref(msg);
}


string sensors()
{
    FILE *sens_conf_file = NULL;

    int chipnum=0, err;
    double curvalue;
    char* degree;
    char buffer[100] = {}; //init zero
    string result;

    const sensors_chip_name *name = NULL;
    err = sensors_init(sens_conf_file);
    if (err)
    {
        snprintf(buffer, sizeof(buffer), "sensors_init %s", sensors_strerror(err));
        result = string(buffer);
        return result;
    }

    degree = degree_sign();

    while ((name = sensors_get_detected_chips(NULL, &chipnum)) != NULL)
    {
        if (name->bus.type != SENSORS_BUS_TYPE_VIRTUAL)
        {
            sensors_get_value(name, 0, &curvalue);
            snprintf(buffer, sizeof(buffer), "%.f%sC", curvalue, degree);
        }
    }

    sensors_cleanup();

    result = string(buffer);
    return result;
}

static char *iconv_from_utf8_to_locale(char *string, const char* fallback_string)
{
    const size_t buffer_inc = 80; // Increment buffer size in 80 bytes step
    const char *charset;
    iconv_t cd;
    size_t nconv;

    char *dest_buffer;
    char *old_dest_buffer;
    char *dest_buffer_ptr;
    char *src_buffer;
    char *src_buffer_ptr;

    size_t dest_buffer_size;
    size_t dest_buffer_size_left;
    size_t src_buffer_size;

    setlocale(LC_ALL, "");
    charset = nl_langinfo(CODESET);

    cd = iconv_open(charset, "UTF-8");
    if (cd == (iconv_t) - 1)
        return strdup(fallback_string);

    dest_buffer_size = dest_buffer_size_left = buffer_inc;
    dest_buffer_ptr = dest_buffer = (char *) malloc(dest_buffer_size);
    src_buffer_ptr = src_buffer = strdup(string);
    src_buffer_size = strlen(src_buffer) + 1;

    while (src_buffer_size != 0)
    {
        nconv = iconv(cd, &src_buffer_ptr, &src_buffer_size, &dest_buffer_ptr, &dest_buffer_size_left);
        if (nconv == (size_t) - 1)
        {
            if (errno != E2BIG)
                goto iconv_error;

            dest_buffer_size += buffer_inc;
            dest_buffer_size_left = buffer_inc;
            old_dest_buffer = dest_buffer;
            dest_buffer = (char *) realloc(dest_buffer, dest_buffer_size);
            if (dest_buffer == NULL)
                goto iconv_error;
            dest_buffer_ptr = (dest_buffer_ptr - old_dest_buffer) + dest_buffer;
        }
    }
    iconv_close(cd);
    free(src_buffer);
    dest_buffer = (char *) realloc(dest_buffer, dest_buffer_size - dest_buffer_size_left);
    return dest_buffer;

iconv_error:
    iconv_close(cd);
    if (dest_buffer != NULL)
        free(dest_buffer);
    free(src_buffer);
    return strdup(fallback_string);
}

char *degree_sign()
{
    char str[] = {0xc2, 0xb0, 0x00};

    return iconv_from_utf8_to_locale(str, " \0");
}

string record_sign()
{
    char* degree;
    char buffer[10];
    string result;

    degree = degree_sign();
    snprintf(buffer, sizeof(buffer), "%sC", degree);
    result = string(buffer);

    return result;
}

BOOST_PYTHON_MODULE(lshw)
{
    class_<lshw, boost::noncopyable > ("lshw", "This is a lshw project python extend", init<>())
            .def("scan_device", &lshw::scan_device)
            .def("get_xml", &lshw::get_xml)
            ;
    def("sensors", &sensors);
    def("record_sign", &record_sign);
}