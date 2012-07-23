#include <dbus/dbus.h>
#include <stdlib.h>
#include <stdio.h>

void status(const char *message)
{
    DBusMessage* msg;
    DBusConnection* conn;
    DBusError err;

    // initialise the error value
    dbus_error_init(&err);

    // connect to the DBUS system bus, and check for errors
    conn = dbus_bus_get(DBUS_BUS_SYSTEM, &err);
    if(dbus_error_is_set(&err))
    {
        fprintf(stderr, "Connection Error (%s)\n", err.message);
        dbus_error_free(&err);
    }
    if(NULL == conn)
    {
        exit(1);
    }

    // create a signal & check for errors
    msg = dbus_message_new_signal("/com/startos/ydm", // object name of the signal
            "com.startos.ydm", // interface name of the signal
            "changed"); // name of the signal
    if(NULL == msg)
    {
        fprintf(stderr, "Message Null\n");
        exit(1);
    }

    // append arguments onto signal
    dbus_message_append_args(msg, DBUS_TYPE_STRING, &message, DBUS_TYPE_INVALID);

    // send the message and flush the connection
    if(!dbus_connection_send(conn, msg, NULL))
    {
        fprintf(stderr, "Out Of Memory!\n");
        exit(1);
    }
    dbus_connection_flush(conn);

    // free the message
    dbus_message_unref(msg);
}